#!/usr/bin/env python
#-*- coding:utf-8 -*-

from __future__ import print_function
import weakref


class CacheItem(object):
    __slots__ = 'next prev key value ref'.split()

    def __init__(self, key, value, next):
        # new items are always placed in the root position
        self.prev = None
        self.next = next
        if next:
            next.prev = self
        self.key = key
        self.value = value
        self.ref = weakref.ref(value)

    def pick(self, next):
        if self.next:
            self.next.prev = self.prev
        if self.prev:
            self.prev.next = self.next
        self.prev = None
        self.next = next
        if next:
            next.prev = self
        return self

    def show(self):
        from phen.util import shorten_hashes
        v = self.ref()
        r = "*" if self.value is not None else "-"
        p = 'root' if not self.prev else self.prev.key
        print(shorten_hashes(u"({}) {}{} ({})>>"
                             .format(p, v, r, self.key)), end="")
        if self.next:
            self.next.show()


class Cache:
    def __init__(self, maxitems, factory, reset=None):
        self.cache = {}
        self.root = None
        self.boundary = None
        self.maxitems = maxitems
        self.factory = factory
        self.reset = reset

    def show(self):
        print("::", end="")
        if self.root:
            self.root.show()
        print("::")

    def receed_boundary(self):
        self.boundary.value = None  # release strong reference
        self.boundary = self.boundary.prev

    def get(self, key):
        """
            Retrieve the value, instantiating if not already in cache.
        """
        if key not in self.cache:
            return self.add(key, create=True)
        item = self.cache[key]
        wval = item.ref()
        if item.value is None:  # item is post-boundary
            if wval is None:
                item.pick(None)
                self.cache.pop(key)
                return self.add(key, create=True)
            self.receed_boundary()
            item.value = wval
        else:
            if item == self.boundary and item != self.root:
                self.receed_boundary()
        retv = wval
        if self.root != item:
            self.root = item.pick(self.root)  # MRU
        if self.reset:
            self.reset(retv)
        return retv

    def add(self, key, value=None, create=False):
        """
            Add the key-value pair to the cache.
        """
        if create:
            value = self.factory(key)
        else:
            assert value is not None
        if key in self.cache:
            # update the value
            item = self.cache[key]
            item.value = value
            item.ref = weakref.ref(value)
            return value
        self.cache[key] = self.root = item = CacheItem(key, value, self.root)
        if not self.boundary:
            self.boundary = item
        if len(self.cache) > self.maxitems:
            self.receed_boundary()
        if len(self.cache) > 2 * self.maxitems:
            self.collect()
        return value

    def remove(self, key):
        if key not in self:
            return
        item = self.cache.pop(key)
        if item == self.boundary or item.value:
            if self.boundary.next:
                self.boundary = self.boundary.next
                self.boundary.value = self.boundary.ref()
            elif item == self.boundary:
                self.boundary = self.boundary.prev
        if item == self.root:
            self.root = item.next
        item.pick(None)

    def collect(self):
        node = self.boundary.next
        cnt = self.maxitems
        # remove all expired items
        while node and cnt:
            if node.ref() is None:
                self.cache.pop(node.key)
                next = node.next
                node.pick(None)
                node = next
            else:
                node = node.next
            cnt -= 1
        if not node:
            return
        # remove anything after 2 * maxitems
        node.prev.next = None
        while node:
            self.cache.pop(node.key)
            node = node.next

    def clear(self):
        """
            Clear the cache.
        """
        self.cache.clear()
        self.root = None
        self.boundary = None

    def __contains__(self, key):
        return key in self.cache and self.cache[key].ref() is not None

    def __iter__(self):
        node = self.root
        while node:
            item = node.ref()
            if item:
                yield item
            node = node.next

    def __getitem__(self, key):
        return self.get(key)

    def __setitem__(self, key, value):
        return self.add(key, value)

    def __delitem__(self, key):
        self.remove(key)
