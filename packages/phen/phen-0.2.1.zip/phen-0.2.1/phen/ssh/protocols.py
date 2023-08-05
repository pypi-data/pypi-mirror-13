# -*- coding:utf-8 -*-

from six import BytesIO
from twisted.internet import protocol, reactor


class CopyKeys(protocol.Protocol):
    def __init__(self, user, cmd):
        self.ctx = user.ctx
        self.buff = BytesIO()

    def connectionMade(self):
        self.transport.write(b"\0")

    def dataReceived(self, data):
        if self.buff.tell() > 1 << 16:  # no key is this big
            self.transport.loseConnection()
        else:
            self.buff.write(data)

    def eofReceived(self, *p):
        key = self.buff.getvalue().strip()
        cfg = self.ctx.account.get_config()
        keys = cfg.get("ssh-keys", [])
        if not isinstance(keys, list):
            keys = [keys]
        if key not in keys:
            keys.append(key)
        cfg["ssh-keys"] = keys
        self.ctx.account.set_config(cfg)
        self.transport.loseConnection()


class SecureCopyProtocol(protocol.Protocol):
    def __init__(self, user, cmd):
        self.ctx = user.ctx
        args = []
        dest = []
        for arg in cmd.split()[1:]:
            if arg.startswith(b"-"):
                args.append(arg)
            else:
                dest.append(arg)
        args = b" ".join(args)
        self.dest = b" ".join(dest)
        self.expect_folder = b"d" in args
        self.time_proto = b"p" in args
        self.time = 0
        self.recursive = b"r" in args
        if b"f" in args:
            self.from_mode = True
            self.files = []
            self.files += self.ctx.fs.glob(self.dest.decode("utf8"))
            self.dataReceived = self._dataReceived_from
        self.state = 'cmd'

    def connectionMade(self):
        if self.expect_folder and self.dest != b".":
            try:
                fmeta = self.ctx.fs.filemeta(self.dest.decode("utf8"))
                if not fmeta.is_folder():
                    raise IOError("Target path is not a folder")
            except IOError as exc:
                self.transport.write(b"".join((b"\2", bytes(exc), b"\n")))
                return
        self.dest = [self.dest]
        if not self.from_mode:
            self.transport.write(b"\0")

    def _receive_command(self, data):
        idx = data.find(b'\0')
        if not idx:
            return data[1:]
        if idx == -1:
            idx = len(data)
        cmd = data[:idx].split()
        cmd, args = cmd[0][0], [cmd[0][1:]] + cmd[1:]
        if cmd == b'D':
            self.dest.append(args[2])
            fname = b"/".join(self.dest).decode("utf8")
            if not self.ctx.fs.exists(fname):
                try:
                    self.ctx.fs.makedirs(fname)
                    if self.time_proto and self.time:
                        self.ctx.fs.utime(fname, self.time)
                        self.time = 0
                except IOError as exc:
                    self.transport.write(b"".join((b"\2", bytes(exc), b"\n")))
                    return
        elif cmd == b'E' and self.dest:
            self.dest.pop(-1)
        elif cmd == b'C':
            # todo: set xattr[mode] = args[0]
            self.remaining = int(args[1])
            self.fname = b"/".join(self.dest + args[2:]).decode("utf8")
            try:
                self.out = self.ctx.fs.open(self.fname, 'wd')
            except IOError as exc:
                self.transport.write(b"".join((b"\2", bytes(exc), b"\n")))
                return
            if not self.remaining:
                try:
                    self.out.close()
                    if self.time_proto and self.time:
                        self.ctx.fs.utime(self.fname, self.time)
                        self.time = 0
                except IOError as exc:
                    self.transport.write(b"".join((b"\2", bytes(exc), b"\n")))
                    return
                self.out = None
                self.transport.write(b"\0")
            else:
                self.state = 'fdata'
        elif cmd == b'T':
            self.time = float(args[2])
        self.transport.write(b"\0")
        return data[idx:]

    def _receive_file_data(self, data):
        to_save = min(self.remaining, len(data))
        self.remaining -= to_save
        self.out.write(data[:to_save])
        if not self.remaining:
            try:
                self.out.close()
                if self.time_proto and self.time:
                    self.ctx.fs.utime(self.fname, self.time)
                    self.time = 0
            except IOError as exc:
                self.transport.write(b"".join((b"\2", bytes(exc), b"\n")))
                return
            self.transport.write(b"\0")
            self.state = 'cmd'
        return data[to_save:]

    def dataReceived(self, data):
        while data and data != b'\0':
            if self.state == 'cmd':
                data = self._receive_command(data)
            else:
                data = self._receive_file_data(data)

    def _dataReceived_from(self, data):
        if self.state == 'cmd':
            if not self.files:
                self.state = 'done'
                self.transport.write(b"E\n")
                reactor.callLater(0, self.finish_pending)
                return
            next_file = self.files.pop(0)
            if next_file is None:
                # end of folder contents
                self.transport.write(b"E\n")
                return
            fmeta = self.ctx.fs.filemeta(next_file)
            name_enc = fmeta.name.encode("utf8")
            to_send = []
            if self.time_proto:
                dtime = fmeta.dtime
                to_send.append(b"T{} 0 {} 0".format(dtime, dtime))
            if fmeta.is_folder():
                if not self.recursive:
                    self.transport.write((b"\2'{}' is a folder, but "
                                          b"non-recursive mode specified\n")
                                         .format(name_enc))
                    return
                to_send.append(b"D0700 0 " + name_enc)
                self.files = [
                    "/".join((next_file, inner))
                    for inner in self.ctx.fs.listdir(next_file)
                ] + [None] + self.files
            else:
                to_send.append(b"C0600 {} {}".format(fmeta.size, name_enc))
                self.state = 'fdata'
                self.in_ = self.ctx.fs.open(next_file)
            self.transport.write(b"\n".join(to_send) + b"\n")
        elif self.state == 'fdata':
            reactor.callLater(0, self.send_file_data)

    def finish_pending(self):
        if self.transport:
            self.transport.write(b"\0")
            self.transport.loseConnection()

    def send_file_data(self):
        if self.in_ is None:
            return
        buff = self.in_.read(1 << 16)
        self.transport.write(buff)
        if len(buff) == 1 << 16:
            reactor.callLater(0, self.send_file_data)
        else:
            self.transport.write(b"\0")
            self.in_.close()
            self.in_ = None
            self.state = 'cmd'
            self.dataReceived(b"")

    def eofReceived(self, *p):
        self.transport.loseConnection()


registry = [
    (CopyKeys, lambda cmd: b"cat >> ~/.ssh/authorized_keys" in cmd),
    (SecureCopyProtocol, lambda cmd: cmd.startswith(b"scp")),
]
