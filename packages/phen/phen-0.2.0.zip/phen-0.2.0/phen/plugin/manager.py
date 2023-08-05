# -*- coding:utf-8 -*-

import os
import sys
import phen
import logging

from .wrapper import Wrapper
from .versioning import Versions


log = logging.getLogger(__name__)


class Manager(object):
    def __init__(self, plugins_path=None):
        Manager.singleton = self
        if plugins_path is None:
            self.plugins_path = os.path.join(phen.phen_path, "plugins")
        else:
            self.plugins_path = plugins_path
        self.versions_path = os.path.join(self.plugins_path, ".versions")
        self.init_path()
        self.versions = {}
        self.plugins = {}
        self.excluded = []
        self.watch = False

    def init_path(self):
        if not os.path.exists(self.plugins_path):
            os.mkdir(self.plugins_path)
            os.mkdir(self.versions_path)
            initpy = os.path.join(self.plugins_path, "__init__.py")
            with open(initpy, 'w') as out:
                out.write("# managed plugins folder\n")
            phen.chown(self.plugins_path)
            phen.chown(self.versions_path)
            phen.chown(initpy)
        self.phen_plugins = set()
        internal_path = os.path.join(phen.phen_path, "plugins")
        internal_plugins = os.listdir(internal_path)
        self.system_wide = self.plugins_path != internal_path
        if not self.system_wide:
            from phen import plugins  # noqa - python3 requires the parent
            for path in internal_plugins:
                fname, ext = os.path.splitext(path)
                if fname != "__init__" and ext in ("", ".py", ".pyc", ".pyo"):
                    self.phen_plugins.add(fname)
            return
        else:
            sys.path.insert(0, os.path.split(self.plugins_path)[0])
            import plugins  # noqa
        self._link_systemwide_noninternal(internal_path, internal_plugins)
        self._link_current_internal()

    def _link_systemwide_noninternal(self, path, plugins):
        """
        link all system-wide installed non-internal plugins
        """
        for plugin in plugins:
            if "." in plugin:  # only folder modules allowed
                continue
            self.phen_plugins.add(plugin)
            dest = os.path.join(self.plugins_path, plugin)
            # ignore if already linked (might be an upgraded version)
            if not os.path.exists(dest):
                os.symlink(os.path.join(path, plugin), dest)
                phen.chown(dest)

    def _link_current_internal(self):
        """
        make sure links point to the correct versions of the internal
        plugins (the ones bundled, regardless of phen core upgrades)
        """
        for plugin in "shell ssh p2pnet http".split():
            src = os.path.join(phen.phen_path, plugin)
            dest = os.path.join(self.plugins_path, plugin)
            if os.path.exists(dest):
                import stat
                is_link = stat.S_ISLNK(os.stat(dest).st_mode)
                if is_link and os.readlink(dest) == src:
                    continue
                os.unlink(dest)  # should raise exception if folder
            os.symlink(src, dest)
            phen.chown(dest)
            self.phen_plugins.add(plugin)

    def exclude(self, excluded):
        """
            Deny loading the specified plugins
        """
        self.excluded = [] if excluded is None else excluded

    def refresh_versions(self):
        for package_name in os.listdir(self.versions_path):
            name, version = Versions.analyse(package_name)
            vv = self.versions.get(name)
            if vv is None:
                vv = self.versions[name] = Versions(self, name, version)
            else:
                vv.add_version(version)

    def documentation(self, name):
        return "plugin doc not implemented yet"

    def bulk_load(self, list):
        retv = [self.load(name) for name in list]
        for name in self:
            self[name].link_dependencies()
        return all(retv)

    def load(self, name, child=None):
        wrapper = self.plugins.get(name)
        if wrapper is not None:
            wrapper.add_child(child)
            return True
        if name in self.excluded:
            return False
        if not self.versions:
            self.refresh_versions()
        if name in self.versions:
            wrapper = self.versions[name].load(child)
            if wrapper:
                self.plugins[name] = wrapper
                return True
        try:
            wrapper = Wrapper(
                self, name, internal=name in self.phen_plugins,
                system_wide=self.system_wide, watch=self.watch, child=child
            )
            if wrapper.plugin:
                self.plugins[name] = wrapper
                return True
        except:
            pass
        log.warn("could not load plugin " + name)
        return False

    def __contains__(self, key):
        return key in self.plugins

    def __getitem__(self, key):
        return self.plugins[key]

    def __iter__(self):
        return iter(self.plugins)

    def broadcast(self, method, interrupt=None, first_only=False):
        """
            Call the given method of all plugins (or the first one
            that has said method if desired), interrupting if the
            given function returns True.
            Return True if at least one method was called, but that
            value may be overridden in case the interrupt function
            was satisfied.
        """
        retv = False
        for plugin in self.plugins.values():
            if plugin.call(method):
                retv = True
                if first_only:
                    break
            if interrupt is not None and interrupt():
                return False
        return retv

    def shutdown(self):
        for plugin in self.plugins.values():
            plugin.shutdown()
