# -*- coding:utf-8 -*-

from phen.shell.base import ProtectedSubCmd, shlexed

from .adapters import Adapters


class Shell(ProtectedSubCmd):
    """
        P2P network management.
    """
    cmdname = "net"
    subcmds = [Adapters]

    def __init__(self, parent, *p, **kw):
        ProtectedSubCmd.__init__(self, *p, **kw)
        self.parent = parent
        from phen.plugin import Manager
        self.plugin = Manager.singleton["p2pnet"].plugin
        self.ctx = parent.ctx
        for cls in Shell.subcmds:
            subcmd = cls(self, *p, **kw)
            self.attach(subcmd, cls.cmdname)

    def preloop(self):
        self.update_prompt()

    def update_prompt(self):
        if self.color:
            pfmt = "\x1b[1;32mnet\x1b[0m$ "
        else:
            pfmt = "net$ "
        self.prompt = pfmt

    def do_status(self, args):
        """status

        Displays the status of all subsystems.

        """
        self.do_dht("status")
        self.onecmd("adapters status")

    def do_dht(self, args):
        """dht [status]

        Manage the Distributed Hash Table.

        """
        if args != "status":
            self.send("dht: unknown command")
        else:
            self.send("dht: not implemented yet")

    @shlexed
    def do_connect(self, args):
        """connect <address> <port>

        Directly connect to a (possibly yet unknown) device.

        """
        if len(args) < 2:
            self.do_help("connect")
        from ..connection import connect_to_address
        connect_to_address(args[0], int(args[1]))
