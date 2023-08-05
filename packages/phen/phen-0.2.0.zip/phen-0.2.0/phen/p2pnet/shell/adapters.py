# -*- coding:utf-8 -*-

from phen.shell.base import ProtectedSubCmd, shlexed, protected


class Adapters(ProtectedSubCmd):
    """
        Manage the network adapter definitions.
    """
    cmdname = "adapters"

    def __init__(self, parent, *p, **kw):
        ProtectedSubCmd.__init__(self, *p, **kw)
        self.parent = parent
        from phen.plugin import Manager
        self.adapters = Manager.singleton["p2pnet"].plugin.adapters
        self.ctx = parent.ctx

    def preloop(self):
        self.update_prompt()

    def update_prompt(self):
        if self.color:
            pfmt = "\x1b[1;32mnet>adapters\x1b[0m$ "
        else:
            pfmt = "net>adapters$ "
        self.prompt = pfmt

    def do_exit(self, args):
        self.send("\n")
        return True

    do_EOF = do_exit

    @protected
    def do_status(self, args):
        """status

        Show network adapters' status

        """
        adapters = self.adapters.adapters
        if not adapters:
            return self.send("adapters: none found, create one with "
                             "new <adapter-name>")
        self.send("adapters:")
        for ad in adapters.values():
            self.send("  * " + str(ad))

    do_list = do_status

    @shlexed
    @protected
    def do_new(self, args):
        """new <adapter-name>

        Create a new network adapter definition.
        Note: the created adapter should be manually commited to persist.

        """
        if not args:
            return self.do_help("new")
        if self.adapters.new(args[0]):
            return self.send(
                "adapter {} created (commit it to persist)\n{}"
                .format(args[0], self.adapters.adapters[args[0]])
            )
        return self.send("adapter {} already exists".format(args[0]))

    @shlexed
    @protected
    def do_commit(self, args):
        """commit <adapter-name>

        Save any changes to the specified network adapter definition.

        """
        if not args:
            return self.do_help("commit")
        self.adapters.commit(args[0])
        return self.send("adapter {} committed".format(args[0]))

    @shlexed
    @protected
    def do_start(self, args):
        """start (<adapter-name> | *)

        Start listening to all (*) or the specified network adapter.

        """
        if not args:
            return self.do_help("start")
        name = args[0]
        try:
            self.adapters.start_up(name=None if name == "*" else name)
        except Exception as exc:
            self.send(exc)
        # [del | rename | set | start | stop]
