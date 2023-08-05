# -*- coding:utf-8 -*-

from copy import copy
from .base import Layout, Cursor


def create_file(fs, path, init_json=None, init_data=None):
    if init_json is None and init_data is None:
        init_data = b""
    if init_json is not None:
        return fs.json_write(path, init_json)
    with fs.open(path, 'w') as out:
        return out.write(init_data)


def create_folder(fs, path):
    return fs.mkdir(path)


class SingleFolder(Layout):
    def __init__(self, parent, path, init=create_file):
        super(SingleFolder, self).__init__(parent, path)
        self._init = init
        # _index maps keys to file names inside path
        self.invalidate()

    def create(self):
        if not self._exists:
            self._parent._fs.makedirs(self._path)
            self._exists = True

    def _load_index(self):
        for fname in self._parent._fs.listdir(self._path):
            path = "/".join((self._path, fname))
            xattr = self._parent._fs.xattr(path)
            if "a" not in xattr:
                continue
            try:
                self._next_idx = max(self._next_idx, int(fname) + 1)
            except:
                pass
            key = self._parent.key_from_json(xattr["a"])
            if key is None:
                raise ValueError("Invalid null key")
            self._index[key] = fname

    def invalidate(self):
        self._index = {}
        self._next_idx = 0
        if self._parent._fs.exists(self._path):
            self._load_index()
            self._exists = True
        else:
            self._exists = False

    def __contains__(self, key):
        return key in self._index

    def __getitem__(self, key):
        path = "/".join((self._path, self._index[key]))
        return path, copy(self._parent._fs.xattr(path)["a"])

    def insert(self, key, json_data, **kw):
        if not self._exists:
            self._parent._fs.makedirs(self._path)
            self._exists = True
        if key in self:
            return None
        while True:
            fname = str(self._next_idx)
            path = "/".join((self._path, fname))
            self._next_idx += 1
            if not self._parent._fs.exists(path):
                break
        self._index[key] = fname
        self._init(self._parent._fs, path, **kw)
        self._parent._fs.xattr(path, {"a": copy(json_data)})
        return path

    def update(self, old_key, new_key, json_data):
        fname = self._index.pop(old_key)
        self._index[new_key] = fname
        path = "/".join((self._path, fname))
        self._parent._fs.xattr(path, {"a": copy(json_data)})
        return path

    def delete(self, key):
        fname = self._index.pop(key)
        path = "/".join((self._path, fname))
        if self._init == create_file:
            self._parent._fs.unlink(path)
        else:
            self._parent._fs.rmtree(path)

    def cursor(self, key, end=False):
        if key is None:
            if end:
                return Cursor(self, None)
            else:
                return Cursor(self, iter(sorted(self._index)))
        return None  # not implemented
