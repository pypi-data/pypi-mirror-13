# -*- coding:utf-8 -*-

"""
    Check for operations in sequence before saving folders.
"""

import time
import threading


class DelayedItem(object):
    __slots__ = 'next prev start last folder'.split()

    def __init__(self, folder, next):
        # new items are always placed in the root position
        self.last = self.start = time.time()
        self.prev = None
        self.next = next
        if next:
            next.prev = self
        self.folder = folder

    def delay(self):
        t = time.time()
        if t - self.last > DelayedSave.minThreshold:
            return False
        if t - self.start > DelayedSave.maxThreshold:
            return False
        self.last = t
        return True

    def pick(self, next):
        if self.next:
            self.next.prev = self.prev
        if self.prev:
            self.prev.next = self.next
        self.next = next
        if next:  # moved to the head
            self.prev = None
            next.prev = self
        return self


class DelayedSave:

    minThreshold = 2.5
    maxThreshold = 5
    sleepCycle = 1

    def __init__(self):
        self.lock = threading.RLock()  # reentrant for changelog
        self.to_save = {}
        self.head = None
        self.tail = None
        self.done = True
        self.th = None
        self.tick = threading.Event()

    def start(self):
        self.done = False
        if self.th is None:
            self.tick.clear()
            self.th = threading.Thread(target=self._run, name="dsave")
            self.th.setDaemon(True)
            self.th.start()

    def shutdown(self):
        self.done = True
        self.flush(close=True)
        if self.th is not None:
            self.tick.set()
            self.th.join()
            self.th = None

    def add(self, folder):
        with self.lock:
            if not folder.dirty:  # might have been saved elsewhere
                return False
            if self.done:  # save it right away
                folder.flush()
                return
            item = self.to_save.get(folder.fid_pair)
            if item is None:
                self.head = DelayedItem(folder, self.head)
                if not self.tail:
                    self.tail = self.head
                self.to_save[folder.fid_pair] = self.head
            else:
                if item.delay() and item != self.head:
                    if item == self.tail:
                        self.tail = self.tail.prev
                    self.head = item.pick(self.head)
                else:
                    return False
            return True

    def preempt(self, fid_pair):
        with self.lock:
            item = self.to_save.pop(fid_pair, None)
            if item is None:
                return False
            item.folder.flush()
            if item == self.head:
                self.head = item.next
            if item == self.tail:
                self.tail = item.prev
            item.pick(None)
        return True

    def _check_expirations(self):
        t = time.time()
        item = self.tail
        # check all items older than minThreshold
        while item and t - item.start > DelayedSave.minThreshold:
            if t - item.last > DelayedSave.minThreshold:
                del self.to_save[item.folder.fid_pair]
                item.folder.flush()
                if item == self.head:
                    self.head = None
                    self.tail = None
                    break
                if item == self.tail:
                    self.tail = self.tail.prev
                item.pick(None)
            item = item.prev

    def _run(self):
        while not self.done:
            self.tick.wait(DelayedSave.sleepCycle)
            with self.lock:
                self._check_expirations()

    def flush(self, close=False):
        with self.lock:
            item = self.head
            while item:
                close and item.folder.close_folder() or item.folder.flush()
                item = item.next
            self.head = None
            self.tail = None
            self.to_save = {}
