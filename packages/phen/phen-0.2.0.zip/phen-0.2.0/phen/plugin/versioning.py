# -*- coding:utf-8 -*-

import os
import re
import json
import logging


log = logging.getLogger(__name__)


class Versions:
    version_re = re.compile(r"^(.*)-(\d+)\.(\d+)\.(\d+)((?:-|\+)\S+)?")

    @staticmethod
    def analyse(package_name):
        m = Versions.version_re.match(package_name)
        if m is None:
            return None, None
        name = m.group(1)
        version = [int(m.group(i)) for i in range(2, 5)]
        version.append(m.group(5) or "")  # empty str instead of None
        return name, tuple(version)

    def __init__(self, manager, name, version):
        self.manager = manager
        self.name = name
        self.versions = {version}
        self._selected = None

    def add_version(self, version):
        self.versions.add(version)

    def get_selected(self):
        if self._selected:
            return self._selected
        package_path = os.path.join(self.manager.plugins_path, self.name)
        if not os.path.exists(package_path):
            return None
        actual_path = os.readlink(package_path)
        path, fname = os.path.split(actual_path)
        name, self._selected = self.analyse(fname)
        if name != self.name:
            log.warn("plugin '{}' is actually '{}'".format(self.name, fname))
        return self._selected

    def set_selected(self, version):
        self._selected = version
        package_path = os.path.join(self.manager.plugins_path, self.name)
        if os.path.exists(package_path):
            os.unlink(package_path)
        if version is None:
            return
        source_path = "{}/{}-{}.{}.{}{}".format(
            self.manager.versions_path, self.name, *version
        )
        os.symlink(source_path, package_path)

    def downgrade(self):
        version = self.get_selected()
        sorted_versions = sorted(self.versions, reverse=True)
        if version is None:
            idx = 0
        else:
            idx = sorted_versions.index(version) + 1
        version = None if idx == len(self.versions) else sorted_versions[idx]
        self.set_selected(version)

    def load(self, child):
        from .wrapper import Wrapper
        version = self.get_selected()
        if version is None:
            self.downgrade()  # pick the latest version
        fail_cnt = 3
        while fail_cnt and self._selected is not None:
            log.debug("trying {} version {}".format(self.name, self._selected))
            wrapper = Wrapper(
                self.manager, self.name,
                watch="-dev" in self._selected or self.manager.watch,
                child=child
            )
            if wrapper.plugin:
                return wrapper
            fail_cnt -= 1
            self.downgrade()
        return

    def get_version(self, name, version, path=None):
        if path is None:
            path = "{}/{}-{}.{}.{}{}".format(
                self.packages_path, name, *version
            )
        try:
            with open(path + "/plugin.json") as infile:
                info = json.load(infile)
        except IOError:
            self.mark_failure(name, version, "couldn't open plugin.json")
            return
        except ValueError:
            self.mark_failure(name, version, "syntax error in plugin.json")
            return
        pkg = info.get("packages")
        pkg = pkg and pkg[0]
        if not pkg:
            return
        pkgdir = info.get("package_dir", {})
        subpath = pkgdir[pkg] if pkg in pkgdir else pkg.replace(".", "/")
        return os.path.join(path, subpath), version, info

    def mark_failure(self, name, version, reason, retry=False):
        log.debug("Failed to load {} version {}: {}"
                  .format(name, version, reason))
