# -*- coding:utf-8 -*-


class Plugin:
    def __init__(self, manager):
        self.devsetup = None
        from phen.shell.shell import Shell
        self.shell_cls = Shell

    def load_device(self):
        from phen.shell.device import DeviceSetup
        self.devsetup = DeviceSetup()
        self.devsetup.setup()

    def device_loaded(self):
        from .setup import setup
        setup()

    def attach(self, sub_shell_cls):
        """Attach commands from a child plugin"""
        self.shell_cls.attach_subcmd(sub_shell_cls)
