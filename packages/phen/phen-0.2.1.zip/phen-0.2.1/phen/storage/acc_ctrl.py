# -*- coding:utf-8 -*-

import os
import sys
import time
import weakref
import logging

from threading import Semaphore

from twisted.internet import reactor, threads
from twisted.internet.error import CannotListenError

from .root import RootFolder
from .accsem import AccessSemaphore
from .netsem import NetClient, NetAccessServer, fidf


log = logging.getLogger(__name__)
log.setLevel(logging.WARNING)


def ldbg(conn, msg):
    """Log a debug message identifying the connection."""
    cid = repr(conn)[-9:-2] if conn else "=local="
    log.debug(u"[{}] {}".format(cid, msg))


class AccessController:
    def __init__(self, root_path, net_addr=None, lock=True):
        self.net_addr = net_addr  # "127.0.0.1", 2000
        self.active = False
        self.netsem = None
        self.netsrv = None
        self.root = RootFolder(root_path)
        self.fid_partial = {}
        self.fid_notif = {}
        self.fid_sems = {}
        self.oids = weakref.WeakValueDictionary()
        if lock:
            self.lock_filesystem()

    def lock_filesystem(self):
        """
            Claim responsibility over the filesystem access control
        """
        if self.net_addr is not None:
            host, port = self.net_addr
        else:
            host, port = None, None
        exclusive = "exclusive {}".format(os.getpid())
        if host is None:
            content = exclusive
        else:
            content = "tcp {} {}".format(host, port)
        existing = self.root.lock(content)
        if self.root.lock_owner:
            log.info("secured exclusive access")
        existing = self._is_exclusive_lock(existing)
        self._try_existing_lock(existing, host)
        if self.netsem is None:
            self._bind_semaphore(existing, content, exclusive, host, port)
        self.active = True

    def _is_exclusive_lock(self, existing):
        if existing is not None and existing.startswith("exclusive"):
            proc = existing.split()
            stale = len(proc) < 2
            if not stale and not sys.platform.startswith("win"):
                try:
                    # on windows this will kill the process - not posix
                    os.kill(int(proc[1]), 0)
                except OSError:
                    stale = True
                except ValueError:
                    stale = True
            if not stale:
                raise RuntimeError("filesystem is locked for exclusive access")
            return None
        return existing

    def _try_existing_lock(self, existing, host):
        if existing is None:
            return
        addr = existing.split()
        try:
            eport = int(addr[2])
        except ValueError:
            addr[0] = None
        except IndexError:
            addr[0] = None
        if addr[0] != "tcp":
            raise RuntimeError("unknown filesystem locking mechanism")
        cnt = 0
        while not self.netsem and cnt < 3:
            self.netsem = threads.blockingCallFromThread(
                reactor, NetClient.connect, self, addr[1], eport)
            if not self.netsem and cnt < 2:
                time.sleep(.1)
            cnt += 1
        if self.netsem and host is None:
            log.warn("exclusive access requested but could not be granted")

    def _bind_semaphore(self, existing, content, exclusive, host, port):
        self.accsem = AccessSemaphore()
        not_bound = host is not None
        cnt = 0
        try_cnt = 3
        stale = False
        while not_bound and cnt < 10:
            try:
                srv = NetAccessServer.setup(self.accsem, host, port + cnt)
                not_bound = False
                if existing is not None or cnt > 0 or stale:
                    # must update contact information
                    content = "tcp {} {}".format(host, port + cnt)
                    self.root.lock(content, force=True)
                self.netsrv = srv
            except CannotListenError:
                try_cnt -= 1
                time.sleep(.2)
                if not try_cnt:
                    cnt += 1
                    try_cnt = 3
        if host is not None:
            if not_bound:
                log.error("could not bind access semaphore to {}:{}..{}"
                          .format(host, port, port + 9))
                log.warn("falling back to exclusive access")
                host = None
                stale = True
            else:
                log.info("access semaphore bound to {}:{}"
                         .format(host, port + cnt))
        if host is None and stale:
            self.root.lock(exclusive, force=True)
            log.info("secured exclusive access")

    def access_semaphore_down(self):
        if not self.active:
            return
        log.warn("semaphore server down, will try to claim root ownership")
        self.lock_filesystem()  # try to claim root ownership

    def shutdown(self):
        if not self.active:
            return
        self.active = False
        self.root.unlock()
        if self.netsrv:
            self.netsrv.shutdown()
            self.netsrv = None
        if self.netsem:
            self.netsem.transport.loseConnection()
            self.netsem = None

    def folder_changed(self, oid, fid, mtime):
        folder = self.oids.get(oid)
        if folder is None:
            log.debug("folder obsolete, unsubbing: " + fidf(fid))
            if self.netsem:
                self.netsem.unsubscribe(fid, oid)
            else:
                self.accsem.unsubscribe(fid, (self, oid))
        else:
            folder.external_modification(mtime)

    def lock_granted(self, oid, fid, inc=False):
        if fid in self.fid_sems:
            self.fid_sems[fid].release()
        else:
            log.error("received erroneous lock grant for " + fidf(fid))

    def flush_requested(self, oid, fid):
        __debug__ and log.debug("flush {}".format(fidf(fid)))
        if fid not in self.fid_partial:
            log.error("received erroneous flush request for " + fidf(fid))
            return
        self.fid_partial[fid].flush()

    def subscribe(self, folder, lock=False):
        if lock:
            self.lock(folder)
        self.oids[id(folder)] = folder
        fid = "".join(folder.fid_pair)
        log.debug(u"subscribing {} to {}".format(folder, fidf(fid)))
        if self.netsem:
            self.netsem.subscribe(fid, id(folder))
        else:
            self.accsem.subscribe(fid, (self, id(folder)))
        self.fid_notif.setdefault(fid, weakref.WeakSet()).add(folder)

    def lock(self, folder, interruptible=False):
        """
            Mark folder for exclusive use.
        """
        if folder.store_lock and not interruptible:
            return  # already locked
        __debug__ and ldbg(self.netsem, u"lock {} {}"
                           .format('i' if interruptible else ' ', folder))
        fid = "".join(folder.fid_pair)
        if fid not in self.fid_sems:
            self.fid_sems[fid] = Semaphore(0)
        if self.netsem:
            if interruptible:
                self.fid_partial[fid] = folder
                return self.netsem.lock(fid, True, id(folder))
            threads.blockingCallFromThread(
                reactor, self.netsem.lock, fid, False, id(folder))
        else:
            if interruptible:
                self.fid_partial[fid] = folder
                return self.accsem.partial_lock(fid, (self, id(folder)))
            self.accsem.lock(fid, (self, id(folder)))
            self.fid_sems[fid].acquire()  # blocks until it has access
        folder.store_lock = True

    def unlock(self, folder, mtime):
        """
            Release folder from exclusive use.
        """
        if not folder.store_lock:
            ldbg(self.netsem, u"{} was not locked?".format(folder))
        folder.store_lock = False
        __debug__ and ldbg(self.netsem, u"unlock {} {}".format(folder, mtime))
        fid = "".join(folder.fid_pair)
        if fid in self.fid_partial:
            self.fid_partial.pop(fid)
        if self.netsem:
            self.netsem.unlock(fid, mtime, id(folder))
        else:
            self.accsem.unlock(fid, mtime, (self, id(folder)))
