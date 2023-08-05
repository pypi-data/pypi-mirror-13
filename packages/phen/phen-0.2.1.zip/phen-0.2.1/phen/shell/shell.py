# -*- coding:utf-8 -*-

import os

try:
    import readline
except ImportError:
    readline = None

from phen.context import Context

from .base import ProtectedSubCmd, shlexed
from .files import FileCommands
from .folders import FolderCommands

from .groups import Groups
from .content import Content
from .account import Accounts
from .identity import Identities


class Shell(ProtectedSubCmd, FileCommands, FolderCommands):
    intro = "Phen command shell.\n"
    subcmds = [Accounts, Content, Groups, Identities]
    restart = False

    @staticmethod
    def attach_subcmd(subcmd):
        for cls in Shell.subcmds[:]:
            if subcmd.cmdname == cls.cmdname:
                Shell.subcmds.remove(cls)
        Shell.subcmds.append(subcmd)

    def __init__(self, *p, **kw):
        self.ctx = kw.pop("ctx", None)
        if self.ctx is None:
            self.ctx = Context.get_admin()
            self.ctx.load_default()
        ProtectedSubCmd.__init__(self, *p, **kw)
        self.hist_path = None
        if "stdin" in kw or "stdout" in kw:
            self.use_rawinput = False
        else:
            self.read_history()
        self.update_prompt()
        for cls in Shell.subcmds:
            subcmd = cls(self, *p, **kw)
            self.attach(subcmd, cls.cmdname)
        if self.ctx.account.is_admin and not self.ctx.cid:
            self.onecmd("id load device")

    def read_history(self):
        from phen.storage import store
        if readline:
            self.hist_path = os.path.join(store.root.path, "shell-history")
            if os.path.exists(self.hist_path):
                readline.read_history_file(self.hist_path)

    def possubcmd(self):
        self.update_prompt()

    def update_prompt(self):
        if self.color:
            pfmt = "\x1b[1;32m{}:{}\x1b[0m:\x1b[1;34m{}\x1b[0m$ "
        else:
            pfmt = "{}:{}:{}$ "
        if not self.ctx.cid:
            uname = "-=-=-"
        else:
            uname, name = self.ctx.pim.get_names(self.ctx.cidhash)
            if uname == "nobody":
                uname = self.ctx.cidhash[:5]
        from phen.util import shorten_hashes
        curdir = shorten_hashes(self.ctx.fs.curdir)
        self.prompt = pfmt.format(self.ctx.account.name, uname, curdir)

    def do_obscure(self, line):
        """obscure <secret>

        Makes it a bit harder to retrieve pass-phrases from configuration
        files where they have to be stored unprotected. Useful against
        malicious people who might gain temporary visual access to the
        sensitive contents. Note: this command is not kept in the history.

        """
        if readline and self.hist_path:
            x = readline.get_current_history_length()
            readline.remove_history_item(x - 1)
        from phen.util import obscure
        self.send(obscure(line.strip()))
        # NOTE: don't ask for a `clarify` command; such feature would
        # only help malicious people on opportunistic attacks

    def do_sha256(self, line):
        """sha256 <secret>

        Applies the SHA256 hashing algorithm over the secret text, returning
        its hexadecimal representation. Useful for configuration files.
        Note: this command is not kept in the history.

        """
        if readline and self.hist_path:
            x = readline.get_current_history_length()
            readline.remove_history_item(x - 1)
        import hashlib
        self.send(hashlib.sha256(line.strip()).hexdigest())

    @shlexed
    def do_exec(self, args):
        """exec <script-file> [admin-authorization]

        Executes the given script. Note: it is not currently possible
        to import other scripts from the internal filesystem.

        """
        if not args:
            return self.do_help("exec")
        try:
            with self.ctx.fs.open(args[0]) as src:
                code = src.read()
            from phen.context import device
            if not self.ctx.account.is_admin:
                if len(args) < 2:
                    self.send("Supply the authorization signature")
                    return self.do_help("exec")
                user_cmd = self.ctx.cidhash + code
                if not device.cid.verify(user_cmd, args[1]):
                    self.send("Script not authorized, please ask the admin")
                    return
            exec code in dict(shell=self, ctx=self.ctx, device=device)
        except Exception as exc:
            self.send("Error: " + str(exc))
        self.update_prompt()

    do_python = do_exec
    complete_exec = FileCommands.complete_cat
    complete_python = FileCommands.complete_cat

    def do_exit(self, line):
        """Exits the shell. (Shortcut: control+d)"""
        self.send("\nThank you, come again.\n")
        if readline and self.hist_path:
            readline.write_history_file(self.hist_path)
        return True

    do_EOF = do_exit

    def emptyline(self):
        pass
