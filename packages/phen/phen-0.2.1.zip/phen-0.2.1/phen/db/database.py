# -*- coding:utf-8 -*-

from .collection import Collection
from .layout import SingleFile


class Database(Collection):

    class State:
        NEW = 1             # not created yet
        OK = 2              # ready for use, may be newer
        OLDER = 3           # data must be upgraded before use
        INCOMPATIBLE = 4    # newer version cannot be parsed

    version = 1
    compatible = 1
    ext = "db"
    key = "version"
    layout = SingleFile

    def __init__(self, fs, path, name=None):
        self._fs = fs
        self._path = path
        if name is None:
            # e.g. ExampleDB -> example.db
            name = self.__class__.__name__.lower()
            if name.endswith("db"):
                name = name[:-2]
        self._singleton = None
        super(Database, self).__init__(fs, None, path, name=name)

    def get_state(self):
        if not self.exists():
            return self.State.NEW
        try:
            self.stored_version = self["current"].current
        except (LookupError, AttributeError):
            return self.State.INCOMPATIBLE
        if self.stored_version == self.version:
            return self.State.OK
        if self.version < self.stored_version:
            info = self[self.stored_version]
            if self.version < info.compatible:
                return self.State.INCOMPATIBLE
            return self.State.OK
        return self.State.OLDER

    def startup(self):
        """Grab event listeners"""

    def shutdown(self):
        """Release event listeners"""

    def create(self):
        if self.exists():
            return False
        self.new(version="current", current=self.version).commit()
        self.new(
            version=str(self.version),
            compatible=self.compatible,
            schema=self.dump_schema(),
        ).commit()
        return True

    def upgrade(self):
        migrations = getattr(self, "migrations", None)
        ver_info = self["current"]
        self.stored_version = ver_info.current
        if self.stored_version >= self.version:
            return
        if migrations is None:
            raise NotImplementedError("cannot upgrade, not implemented")
        migrations(self.stored_version)
        self.new(
            version=str(self.version),
            compatible=self.compatible,
            schema=self.dump_schema(),
        ).commit()
        ver_info.current = self.version
        ver_info.commit()

    def __getattr__(self, attr):
        children = super(Database, self).__getattribute__("_children")
        if attr == "_children":
            return children
        if attr in children:
            if self._singleton is None:
                self._singleton = self["current"]
            return getattr(self._singleton, attr)
        return super(Database, self).__getattribute__(attr)
