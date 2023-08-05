# -*- coding:utf-8 -*-

import weakref


def split_method(callback):
    if hasattr(callback, "__self__"):
        return (weakref.ref(callback.__self__), callback.__func__.__name__)
    else:
        return (callback, None)


class Event:
    def __init__(self):
        self.subscribers = set()

    def subscribe(self, callback):
        self.subscribers.add(split_method(callback))

    def unsubscribe(self, callback):
        self.subscribers.discard(split_method(callback))

    def call(self, *args, **kargs):
        """Call all callbacks, return whether chain was interrupted."""
        for ref in self.subscribers:
            if ref[1] is None:
                callback = ref[0]
            else:
                deref = ref[0]()
                if deref is None:
                    continue
                callback = getattr(deref, ref[1])
            stop = callback(*args, **kargs)
            if stop:
                return True
        return False

    __call__ = call


class OrderedEvent:
    def __init__(self):
        self.subscribers = []

    def subscribe(self, callback, priority=0):
        self.subscribers.append((-priority, callback))
        self.subscribers.sort(key=lambda o: o[0])

    def unsubscribe(self, callback):
        for priority, cback in self.subscribers:
            if callback == cback:
                self.subscribers.remove((priority, callback))

    def call(self, *args, **kargs):
        """Call all callbacks, return whether chain was interrupted."""
        for priority, callback in self.subscribers:
            stop = callback(*args, **kargs)
            if stop:
                return True
        return False

    __call__ = call
