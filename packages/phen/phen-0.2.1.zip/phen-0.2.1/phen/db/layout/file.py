# -*- coding:utf-8 -*-

from copy import copy
from bisect import bisect_left, insort_left

from .base import Layout, Cursor


class SingleFile(Layout):
    file_based = True

    def __init__(self, parent, path, create=False):
        super(SingleFile, self).__init__(parent, path)
        if self._parent._fs.exists(path):
            self.invalidate()
        else:
            self._data = {}
            if create:
                self._save_data()
            else:
                self._exists = False

    def create(self):
        if not self._exists:
            self._save_data()

    def _save_data(self):
        self._parent._fs.json_write(self._path, self._data)
        self._exists = True

    def invalidate(self):
        self._data = self._parent._fs.json_read(self._path)
        if isinstance(self._data, list):
            # assume it was a SingleFileMultiKey, convert the data
            self._data = dict(self._data)

    def __contains__(self, key):
        return key in self._data

    def __getitem__(self, key):
        return None, self._data[key]

    def insert(self, key, json_data):
        if __debug__:
            if not isinstance(key, basestring):
                raise TypeError("keys must be strings")
        self._data[key] = copy(json_data)
        self._save_data()

    def update(self, old_key, new_key, json_data):
        self._data.pop(old_key)
        self._data[new_key] = copy(json_data)
        self._save_data()
        return None

    def delete(self, key):
        self._data.pop(key)
        self._save_data()

    def cursor(self, key, end=False):
        if key is None:
            if end:
                return Cursor(self, None)
            else:
                return Cursor(self, iter(sorted(self._data)))
        return None  # not implemented


class SingleFileMultiKey(Layout):
    file_based = True

    def __init__(self, parent, path, create=False):
        super(SingleFileMultiKey, self).__init__(parent, path)
        if self._parent._fs.exists(path):
            self.invalidate()
        else:
            self._data = []
            if create:
                self._save_data()
            else:
                self._exists = False

    def create(self):
        if not self._exists:
            self._save_data()

    def _save_data(self):
        self._parent._fs.json_write(self._path, self._data)
        self._exists = True

    def invalidate(self):
        self._data = self._parent._fs.json_read(self._path)
        if isinstance(self._data, dict):
            # assume it was a SingleFile, convert the data
            self._data = list(self._data.items())

    def _key_index(self, key, value=None):
        return bisect_left(self._data, [key, value])

    def _get_item(self, key, value=None):
        if not self._data:
            return None
        idx = self._key_index(key, value)
        if idx == len(self._data) or self._data[idx][0] != key:
            return None
        if value is not None and self._data[idx][1] != value:
            return None
        return idx

    def __contains__(self, key):
        idx = self._get_item(key)
        return idx is not None

    def __getitem__(self, key):
        idx = self._get_item(key)
        if idx is None:
            raise LookupError("key not found")
        return None, self._data[idx][1]

    def insert(self, key, json_data):
        insort_left(self._data, [key, copy(json_data)])
        self._save_data()

    def update(self, old_key, new_key, json_data, old_value=None):
        idx = self._get_item(old_key, old_value)
        if idx is None:
            raise LookupError("key not found")
        if old_key != new_key:
            self._data.pop(idx)
            insort_left(self._data, [new_key, copy(json_data)])
        else:
            self._data[idx][1] = copy(json_data)
        self._save_data()
        return None

    def delete(self, key, value=None):
        idx = self._get_item(key, value)
        if idx is None:
            raise LookupError("key not found")
        self._data.pop(idx)
        self._save_data()

    def cursor(self, key, end=False):
        if key is None:
            if end:
                return Cursor(self, None)
            else:
                return Cursor(self, iter(i[0] for i in self._data))
        return None  # not implemented
