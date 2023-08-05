# -*- coding:utf-8 -*-

from threading import Event, Lock
from twisted.conch import recvline
from twisted.internet import reactor

CTRL_C = b'\x03'
CTRL_D = b'\x04'
CTRL_L = b'\x0c'
CTRL_A = b'\x01'
CTRL_E = b'\x05'
CTRL_R = b'\x12'  # todo: reverse search

CTRL_RIGHT = b"\x1b\x5b\x31\x3b\x35\x43"
CTRL_LEFT = b"\x1b\x5b\x31\x3b\x35\x44"
CTRL_DEL = b"\x1b\x5b\x33\x3b\x35\x7e"
HOME = b"\x1b\x5b\x4f\x48"
END = b"\x1b\x5b\x4f\x46"


class ShellIOProxy:
    def __init__(self, terminal):
        self.terminal = terminal
        self.input_event = Event()
        self.lines_lock = Lock()
        self.lines = []
        self.__t_write = self.terminal.write

    def write(self, data):
        if isinstance(data, unicode):
            data = data.encode("utf8")
        self.terminal.write(data)

    def flush(self):
        pass

    def echo(self, active=True):
        self.terminal.write = self.__t_write if active else (lambda c: None)
        if active:
            self.terminal.nextLine()

    def __hidden_input(self, c):
        if len(c) != 1 or not (31 < ord(c) < 128):
            if c != '\n':
                self.__t_write(c)
        else:
            self.__t_write('*')

    def hidden(self, active=True, hide_input=0):
        if active:
            self.terminal.write = self.__hidden_input
        else:
            self.terminal.write = self.__t_write
            for i in range(hide_input):
                self.terminal.cursorBackward()
                self.terminal.deleteCharacter()
            self.terminal.nextLine()

    def line_received(self, line):
        with self.lines_lock:
            self.lines.append(line)
        retv = self.terminal.write == self.__t_write
        self.input_event.set()
        return retv

    def readline(self):
        if not self.lines:
            self.input_event.wait()
            self.input_event.clear()
        with self.lines_lock:
            if not self.lines:
                return "\n"
            line = self.lines.pop(0)
            if line is None:
                raise KeyboardInterrupt
        return line + "\n"


class ShellProtocol(recvline.HistoricRecvLine):
    def __init__(self, user):
        recvline.HistoricRecvLine.__init__(self)
        self.user = user
        self.completion_try = None
        self.completion_opts = []

    def connectionMade(self):
        recvline.HistoricRecvLine.connectionMade(self)
        self.keyHandlers[CTRL_C] = self.handle_INT
        self.keyHandlers[CTRL_D] = self.handle_EOF
        self.keyHandlers[CTRL_L] = self.handle_FF
        self.keyHandlers[CTRL_A] = self.handle_HOME
        self.keyHandlers[CTRL_E] = self.handle_END

        self.io = ShellIOProxy(self.terminal)
        from phen.plugin import Manager
        shell_cls = Manager.singleton["ssh"].plugin.shell_cls
        self.shell = shell_cls(
            ctx=self.user.ctx,
            stdin=self.io,
            stdout=self.io,
            color=self.user.use_color
        )
        reactor.callInThread(self.cmdloop)

    def cmdloop(self):
        cfg = self.user.ctx.account.get_config()
        if "motd" in cfg:
            self.shell.intro = "\n".join(
                (self.shell.intro, cfg["motd"], "")
            )
        while True:
            try:
                self.shell.cmdloop()
                break
            except KeyboardInterrupt:
                self.shell.intro = None
        self.terminal.transport.loseConnection()

    def lineReceived(self, line):
        if not self.io.line_received(line) and line:
            self.historyLines.pop(-1)
            self.historyPosition = len(self.historyLines)

    def initializeScreen(self):
        # self.terminal.reset()
        self.setInsertMode()

    def handle_INT(self):
        self.lineBuffer = []
        self.lineBufferIndex = 0
        self.terminal.nextLine()
        self.io.line_received(None)
        self.io.echo()

    def handle_TAB(self):
        start = self.currentLineBuffer()[0]
        if start == self.completion_try:
            if not self.completion_opts:
                self.terminal.write("\x07")
                return
            self.terminal.nextLine()
            self.terminal.write(self.shell.columnize(self.completion_opts))
            self.terminal.write(b"> " + b"".join(self.lineBuffer))
        else:
            completions = self.complete_command(start, len(start))
            self.completion_opts = [
                opt.encode("utf8") if not isinstance(opt, bytes) else opt
                for opt in completions
            ]
            boundary = start.rfind(b" ")
            # complete common prefix
            insidx = len(start)
            if boundary != -1:
                insidx = insidx - boundary - 1
            while self.completion_opts:
                if insidx >= len(self.completion_opts[0]):
                    break
                c = self.completion_opts[0][insidx]
                if any(insidx >= len(opt) or c != opt[insidx]
                       for opt in self.completion_opts[1:]):
                    break
                self.terminal.write(c)
                start += c
                insidx += 1
            tail = self.lineBuffer[self.lineBufferIndex:]
            self.lineBuffer = list(start) + tail
            self.lineBufferIndex = len(start)
            if len(self.completion_opts) < 2:
                self.completion_try = None
                self.completion_opts = []
            else:
                self.completion_try = start

    def complete_command(self, text, endidx):
        cmd, args, dummy = self.shell.parseline(text)
        boundary = (text and text[endidx - 1] == b" ")
        if cmd is None or not (args or boundary):
            return self.shell.completenames(cmd or "", "", 0, 0)
        else:
            mname = 'complete_' + cmd
            compfunc = getattr(self.shell, mname, self.shell.completedefault)
            stext = " ".join((cmd, args))
            return compfunc(args, stext, 0, 0)
        return []

    def handle_EOF(self):
        if not hasattr(self, "tried_to_disconnect"):
            self.io.line_received("exit")
            self.tried_to_disconnect = True
        else:
            # the following is not used because it resets the terminal
            # self.terminal.loseConnection()
            self.terminal.transport.loseConnection()

    def handle_FF(self):
        self.terminal.reset()

    def _skip_word_left(self):
        idx = self.lineBufferIndex
        # walk spaces until word
        while (self.lineBufferIndex and
               self.lineBuffer[self.lineBufferIndex - 1] == ' '):
            self.handle_LEFT()
        if idx != self.lineBufferIndex:
            return
        # walk word until spaces
        while (self.lineBufferIndex and
               self.lineBuffer[self.lineBufferIndex - 1] != ' '):
            self.handle_LEFT()

    def _skip_word_right(self):
        idx = self.lineBufferIndex
        # walk spaces until word
        while (self.lineBufferIndex < len(self.lineBuffer) - 1 and
               self.lineBuffer[self.lineBufferIndex] == ' '):
            self.handle_RIGHT()
        if idx != self.lineBufferIndex:
            return
        # walk word until spaces
        while (self.lineBufferIndex < len(self.lineBuffer) - 1 and
               self.lineBuffer[self.lineBufferIndex] != ' '):
            self.handle_RIGHT()

    def _remove_word_right(self):
        if self.lineBuffer[self.lineBufferIndex] == ' ':
            # erase spaces until word
            while (self.lineBufferIndex < len(self.lineBuffer) and
                   self.lineBuffer[self.lineBufferIndex] == ' '):
                self.handle_DELETE()
        else:
            while (self.lineBufferIndex < len(self.lineBuffer) and
                   self.lineBuffer[self.lineBufferIndex] != ' '):
                self.handle_DELETE()

    def unhandledControlSequence(self, seq):
        if seq == CTRL_LEFT:
            return self._skip_word_left()
        if seq == CTRL_RIGHT:
            return self._skip_word_right()
        if seq == HOME:
            self.handle_HOME()
            return
        if seq == END:
            self.handle_END()
            return
        if seq == CTRL_DEL:
            return self._remove_word_right()
#        seqstr = "".join("\\x%02x" % c for c in bytearray(seq))
#        print('unhandled b"{}"'.format(seqstr))

    def keystrokeReceived(self, keyId, modifier):
        if modifier == self.terminal.ALT:
            if keyId == self.terminal.BACKSPACE:
                idx = self.lineBufferIndex
                # erase spaces until word
                while (self.lineBufferIndex and
                       self.lineBuffer[self.lineBufferIndex - 1] == ' '):
                    self.handle_BACKSPACE()
                if idx != self.lineBufferIndex:
                    return
                # erase word until spaces
                while (self.lineBufferIndex and
                       self.lineBuffer[self.lineBufferIndex - 1] != ' '):
                    self.handle_BACKSPACE()
                return
        super(ShellProtocol, self).keystrokeReceived(keyId, modifier)
