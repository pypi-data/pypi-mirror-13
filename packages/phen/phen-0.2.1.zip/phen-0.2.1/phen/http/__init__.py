# -*- coding:utf-8 -*-

from .server import Server


class Plugin:
    def __init__(self, manager):
        self.manager = manager
        self.running = False
        self.server = None

    # def load_device(self):
    #     self.server = Server()
    #     self.server.setup_device_page()
    #
    def device_loaded(self):
        if self.running:
            return
        self.running = True
        if self.server:
            self.server.shutdown()
        self.server = Server()
        self.server.setup()

    def shutdown(self):
        if self.server:
            self.server.shutdown()
