# -*- coding:utf-8 -*-

import logging
from twisted.internet import reactor, threads, defer

import phen.context
from .adapters import Adapters
from .requests import rh, download
from .filexchg import download_mgr
# from .synchronizer import Synchronizer

from phen.util import fid2name


log = logging.getLogger(__name__)


def request_fid(self, fid_pair):
    import phen
    import threading
    if threading.current_thread() == phen.reactor_thread:
        log.error("must not request a download from the reactor thread")
        return
    if download_mgr.already_requested(fid_pair):
        log.error("concurrent request for " + fid2name(fid_pair))
        return
    log.info("file system request for " + fid2name(fid_pair))
    dl, dl_fid_pair, mtime = threads.blockingCallFromThread(
        reactor, download,
        fid_pair, timeout=5,
    )
    return dl, dl_fid_pair, mtime


class Plugin:
    def __init__(self, manager):
        self.manager = manager
        self.adapters = None
        from phen.filesystem.filesystem import FileSystem
        FileSystem.request = request_fid
        __debug__ and defer.setDebugging(True)

    def reloaded(self, last, data):
        log.warm("reload: not sure what will happen to current connections")

    def shutdown(self):
        if self.adapters is not None:
            self.adapters.shut_down()

    def device_loaded(self):
        rh.ctx = phen.context.device
        self.adapters = Adapters()
        self.adapters.start_up()
        # self.synchronizer = Synchronizer()

    def complement_shell(self, wrapper):
        from .shell import Shell
        wrapper.plugin.attach(Shell)

    complement_ssh = complement_shell
