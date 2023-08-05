# -*- coding:utf-8 -*-

from phen.hub import interrupt


class Plugin:
    def __init__(self, manager):
        self.manager = manager
        self.shell = None
        self.shell_cls = None
        self.main_loop = self

    def initialize(self):
        import phen.context
        from .shell import Shell
        self.shell_cls = Shell
        phen.context.device_loaded.subscribe(self.device_loaded)
        self.devsetup = None

    def reloaded(self, last, data):
        self.main_loop = last.main_loop
        self.initialize()
        self.restart()

    def restart(self):
        if self.main_loop.shell:
            self.main_loop.shell.send("[plugin updated, restarting shell]")
            self.main_loop.shell.restart = True
        interrupt()

    def shutdown(self):
        import phen.context
        phen.context.device_loaded.unsubscribe(self.device_loaded)

    def load_device(self):
        from phen.shell.device import DeviceSetup
        self.devsetup = DeviceSetup()
        self.devsetup.setup()

    def device_loaded(self):
        # interrupt pending user input - not needed anymore
        if self.devsetup and self.devsetup.state == 'load-dev':
            interrupt()

    def attach(self, sub_shell_cls):
        """Attach commands from a child plugin"""
        self.shell_cls.attach_subcmd(sub_shell_cls)

    def child_reloaded(self, child):
        self.restart()

    def main(self):
        # this code is executed in its closure and can't be updated
        # when the plugin is reloaded
        self.shell = self.shell_cls()
        while True:
            try:
                self.shell.cmdloop()
                break
            except KeyboardInterrupt:
                if self.shell.restart:
                    self.shell = self.shell_cls(ctx=self.shell.ctx)
                self.shell.intro = None
                print("")
        self.shell.ctx.cid and self.shell.ctx.unload_identity()
