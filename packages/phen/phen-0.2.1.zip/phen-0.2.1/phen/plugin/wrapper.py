# -*- coding:utf-8 -*-

import os
import json
import logging
import importlib

from types import ModuleType


log = logging.getLogger(__name__)


def recursive_reload(module, base):
    retv = False
    for key in dir(module):
        attr = getattr(module, key)
        if isinstance(attr, ModuleType):
            if not getattr(attr, "__file__", "").startswith(base):
                continue
            retv |= recursive_reload(attr, base)
    try:
        if hasattr(importlib, "reload"):
            importlib.reload(module)
        else:
            reload(module)
    except ImportError:
        log.warn("couldn't reload '{}'".format(module))
        return False
    return True


class Wrapper:
    def __init__(self, manager, name, internal=False,
                 system_wide=False, watch=False, child=None):
        self.manager = manager
        self.name = name
        self.internal = internal
        self.system_wide = system_wide
        self.module = None
        self.plugin = None
        self.children = []
        if child is not None:
            self.add_child(child)
        self.read_info()
        self.load()
        self.watch = self.setup_watch() if watch else None
        self.timer = None
        self.changes = set()

    def add_child(self, child):
        if isinstance(child, Wrapper):
            if child not in self.children:
                self.children.append(child)
        else:
            log.warn("'{}' tried to add non Wrapper child {}"
                     .format(self.name, repr(child)))

    def read_info(self):
        info_path = os.path.join(
            self.manager.plugins_path, self.name, "plugin.json"
        )
        if not os.path.exists(info_path):
            self.info = None
            self.requirements = set()
            self.complements = set()
            if not self.internal:
                log.warn("plugin {} didn't provide info".format(self.name))
            return
        try:
            with open(info_path) as infile:
                self.info = json.load(infile)
        except IOError:
            log.error(
                "plugin '{}': couldn't open plugin.json".format(self.name)
            )
            return
        except ValueError:
            log.error(
                "plugin '{}': syntax error in plugin.json".format(self.name)
            )
            return
        self.requirements = set(self.info.get("phen_requires", []))
        self.complements = set(self.info.get("phen_complements", []))

    def load_requirements(self):
        log.debug("{} requires: {}".format(
            self.name, ", ".join(self.requirements)
        ))
        for name in self.requirements:
            if not self.manager.load(name, child=self):
                log.debug("{} unmet requirement '{}'".format(self.name, name))
                return False
        return True

    def load(self):
        if self.requirements and not self.load_requirements():
            return False
        base = "plugins" if self.system_wide else "phen.plugins"
        try:
            self.module = importlib.import_module("." + self.name, base)
            self.plugin = self.module.Plugin(self.manager)
            self.complements.update(
                attr[11:] for attr in dir(self.plugin)
                if attr.startswith("complement_")
            )
            self.call("update_info", self)
            for parent in self.complements:
                if parent in self.manager.plugins:
                    self.manager[parent].add_child(self)
            log.info("loaded plugin '{}'".format(self.name))
            self.call("initialize")
            return True
        except:
            import traceback
            log.warn("could not load plugin '{}'".format(self.name))
            for line in traceback.format_exc().splitlines():
                log.debug(line)
        return False

    def link_dependencies(self):
        for parent in self.complements.union(self.requirements):
            if parent in self.manager:
                self.call("complement_" + parent, self.manager[parent])

    def setup_watch(self):
        try:
            from watchdog.observers import Observer
        except ImportError:
            return
        path = os.path.realpath(
            os.path.join(self.manager.plugins_path, self.name)
        )
        if not os.path.isdir(path):
            return
        log.debug("setting up watch @ {}".format(path))
        watch = Observer()
        watch.schedule(self, path, recursive=True)
        watch.start()
        return watch

    # watchdog.events.FileSystemEventHandler interface
    def dispatch(self, event):
        if event.src_path.endswith((".pyc", ".pyo")):
            return
        if self.timer is not None:
            self.timer.cancel()
        from threading import Timer
        self.changes.add(event.src_path)
        self.timer = Timer(.5, self.changes_detected)
        self.timer.start()

    def changes_detected(self):
        self.timer = None
        sources = [
            fname for fname in self.changes
            if fname.endswith(".py")
        ]
        data = self.changes - set(sources)
        if sources:
            self.reload(data)
        else:
            self.call("data_changed", data)
        self.changes.clear()

    def reload(self, data):
        """
        Reload the plugin, calling its method `reloaded` with the set
        of data (non-source) files that changed.
        """
        try:
            recursive_reload(
                self.module, os.path.join(self.manager.plugins_path, self.name)
            )
            log.debug("plugin '{}' reloaded".format(self.name))
        except:
            import traceback
            log.warn("could not reload plugin '{}'".format(self.name))
            for line in traceback.format_exc().splitlines():
                log.debug(line)
        last = self.plugin
        self.plugin = self.module.Plugin(self.manager)
        if not self.call("reloaded", last, data):
            self.call("initialize")
        for parent in self.requirements.union(self.complements):
            if parent in self.manager:
                self.manager[parent].call("child_reloaded", self)
        self.link_dependencies()
        for child in self.children:
            child.call("parent_reloaded", self)
        meth = getattr(last, "shutdown", None)
        if meth:
            meth()

    def unload(self):
        self.shutdown()
        self.module = None  # can't unload a Python module (2015, 3.4)

    def call(self, method, *params):
        meth = getattr(self.plugin, method, None)
        if meth is None:
            return False
        try:
            meth(*params)
        except:
            log.exception("calling {}.{}".format(self.name, method))
        return True

    def shutdown(self):
        self.call("shutdown")
        if self.watch is not None:
            log.debug("shutting down watch for '{}'".format(self.name))
            self.watch.stop()
            self.watch.join()
