#!/usr/bin/env python
#-*- coding:utf-8 -*-

"""
    Folder Access Semaphore
"""

# note: all references to `fid` bellow actually mean idhash + fid

import logging
from collections import deque, Counter


log = logging.getLogger(__name__)

LOCKED = 1
INTERRUPTIBLE = 2


def fidf(fid_flat):
#    return (fid_flat[:5] + b"::" + fid_flat[43:48]).decode("ascii")
    return (fid_flat[:5] + "::" + fid_flat[43:48])


class AccessSemaphore:
    def __init__(self):
        self.locks = {}
        self.notifications = {}

    def subscribe(self, fid, client):
        """
            subscribe to change notifications
        """
        self.notifications.setdefault(fid, set()).add(client)

    def unsubscribe(self, fid, client):
        """
            unsubscribe
        """
        notif_set = self.notifications.setdefault(fid, set())
        if client in notif_set:
            notif_set.remove(client)
        else:
            log.warn("client was not subscribed to folder " + fidf(fid))
        return

    def lock(self, fid, client):
        """
            lock a folder
        """
        queue = self.locks.setdefault(fid, deque())
        # is no one using the folder?
        if not queue:
            # grant the exclusive use
            queue.append([LOCKED, client])
            client[0].lock_granted(client[1], fid)
            return
        # is the client the one that has just partially released it?
        if queue[0] == [INTERRUPTIBLE, client]:
            # grant the exclusive use
            queue[0][0] = LOCKED
            client[0].lock_granted(client[1], fid, False)
            return
        # queue the request for exclusive access
        queue.append([LOCKED, client])
        # if current lock is interruptible, ask for flush/unlock
        if queue[0][0] == INTERRUPTIBLE:
            oclient = queue[0][1]
            oclient[0].flush_requested(oclient[1], fid)

    def partial_lock(self, fid, client):
        """
            partial folder lock - interruptible
        """
        queue = self.locks.setdefault(fid, deque())
        if not queue or queue[0][1] != client:
            log.error("ignoring misplaced partial unlock for " + fidf(fid))
            return False
        # are there more locks waiting?
        if len(queue) > 1:
            # if not from the same client, ask for immediate flush/unlock
            if queue[1][1] != client:
                client[0].flush_requested(client[1], fid)
            # same, so just lock it
            else:
                queue.popleft()
                client[0].lock_granted(client[1], fid, False)
                return True
        # mark it as interruptible
        queue[0][0] = INTERRUPTIBLE
        return True

    def unlock(self, fid, mtime, client):
        """
            unlock a folder
        """
        queue = self.locks.setdefault(fid, deque())
        if not queue or queue[0][1] != client:
            log.error("ignoring misplaced unlock for " + fidf(fid))
            return False
        if queue[0][0] != INTERRUPTIBLE and mtime != '-':
            log.warn("folder didn't go through partial lock: " + fidf(fid))
        queue.popleft()
        if mtime != '-' and fid in self.notifications:
            for notif_cli in list(self.notifications[fid]):
                if notif_cli != client:
                    notif_cli[0].folder_changed(notif_cli[1], fid, mtime)
        if queue:
            client = queue[0][1]
            client[0].lock_granted(client[1], fid)
        return True

    def clear_locks(self, client):
        """
            remove all references to an obsoleted client
        """
        for fid in client.fids:
            if not client.fids[fid]:
                continue
            queue = self.locks.setdefault(fid, deque())
            for e in list(queue):
                if e[1][0] == client:
                    queue.remove(e)


class ClientBase:
    def __init__(self, accsem):
        self.accsem = accsem
        self.fids = Counter()

    def folder_changed(self, oid, fid, mtime):
        """
            folder changed
        """
        raise NotImplementedError

    def lock_granted(self, oid, fid, inc=True):
        """
            lock granted
        """
        raise NotImplementedError
#        if inc:
#            self.fids[fid] += 1

    def flush_requested(self, oid, fid):
        """
            flush requested
        """
        raise NotImplementedError

    def subscribe(self, fid):
        raise NotImplementedError
        #self.accsem.subscribe(fid, (self, oid))

    def unsubscribe(self, fid):
        raise NotImplementedError
#        self.accsem.unsubscribe(fid, (self, oid))

    def lock(self, fid, interruptible=False):
        raise NotImplementedError
#        if not interruptible:
#            self.accsem.lock(fid, (self, oid))
#        else:
#            self.accsem.partial_lock(fid, (self, oid))

    def unlock(self, fid, mtime):
        raise NotImplementedError
#        if self.accsem.unlock(fid, mtime, (self, oid)):
#            self.fids[fid] -= 1
