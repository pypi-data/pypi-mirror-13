# -*- coding:utf-8 -*-

import six
import cmd
import sys
from functools import wraps


class SubCmd(cmd.Cmd):
    """
        Command interpreter with sub interpreters.
    """
    def __init__(self, *p, **kw):
        if "stdin" in kw or "stdout" in kw:
            self.use_rawinput = False
        self.color = kw.pop("color", None)
        cmd.Cmd.__init__(self, *p, **kw)
        if self.color is None and self.use_rawinput:
            self.color = not sys.platform.startswith("win")
        self._subcmds = []

    def precmd(self, line):
        return line if six.PY3 else line.decode("utf8")

    def get_names(self):
        return [k for k in dir(self) if k != "do_EOF"]

    def attach(self, sub, cmdname=None):  # noqa - complex but readable
        self._subcmds.append(sub)
        if cmdname is None:
            import re
            cmdname = re.sub("[A-Z]+", lambda m: "-" + m.group(0).lower(),
                             sub.__class__.__name__)
            if cmdname.startswith("-"):
                cmdname = cmdname[1:]

        def do_command(line):
            if line:
                sub.onecmd(line)
            else:
                sub.cmdloop()
            if hasattr(self, "possubcmd"):
                self.possubcmd()

        def help_command():
            self.stdout.write(getattr(sub, "__doc__", "") + "\n")
            sub.do_help("")

        def complete_command(text, wholeline, begidx, endidx):
            cmd, args, dummy = self.parseline(wholeline)
            assert cmd == cmdname
            cmd, args, dummy = self.parseline(args)
            boundary = wholeline[endidx - 1] == " "
            if cmd is None or not (args or boundary):
                return sub.completenames(cmd or "", "", 0, 0)
            else:
                compfunc = getattr(sub, 'complete_' + cmd, sub.completedefault)
                return compfunc(args, " ".join((cmd, args)), 0, 0)

        if getattr(sub, "__doc__", None):
            do_command.__doc__ = sub.__doc__

        setattr(self, "do_" + cmdname, do_command)
        setattr(self, "help_" + cmdname, help_command)
        setattr(self, "complete_" + cmdname, complete_command)

    def do_exit(self, line):
        """Exits to the previous shell level. (Shortcut: control+d)"""
        self.send("\n")
        return True

    do_EOF = do_exit

    def emptyline(self):
        pass

    def send(self, *p, **kw):
        lf = "" if kw.get("nolf") else "\n"
        self.stdout.write(" ".join(str(i) for i in p) + lf)
        if not lf:
            self.stdout.flush()

    def set_stdin(self, stdin):
        self.stdin = stdin
        for subcmd in self._subcmds:
            subcmd.set_stdin(stdin)


class ProtectedSubCmd(SubCmd):
    """
        Interpreter that verifies if the command is allowed.
    """
    def get_names(self):
        admin = hasattr(self, "ctx") and self.ctx.account.is_admin
        return [
            k for k in dir(self)
            if k.startswith("do_") and k != "do_EOF" and (
                admin or not getattr(getattr(self, k), "__admin__", None)
            )
        ]


def protected(func):
    @wraps(func)
    def decorated(self, *p, **kw):
        if not hasattr(self, "ctx") or not self.ctx.account.is_admin:
            self.send("Command requires admin privileges")
            return
        return func(self, *p, **kw)
    decorated.__admin__ = True
    return decorated


def requires_cid(func):
    @wraps(func)
    def decorated(self, *p, **kw):
        if not hasattr(self, "ctx") or not self.ctx.cid:
            return self.send("No identity currently in use")
        return func(self, *p, **kw)
    return decorated


def shlexed(func):
    @wraps(func)
    def decorated(self, line):
        import shlex
        if six.PY3:
            args = shlex.split(line)
        else:
            args = shlex.split(line.encode("utf8"))
            args = [arg.decode("utf8") for arg in args]
        return func(self, args)
    return decorated
