# -*- coding:utf-8 -*-

from copy import copy


class Item(object):
    _is_index_key = False

    def __init__(self, parent, path=None, data=None, new=True):
        self._parent = parent  # Storage that contains this Item
        self._path = path
        self._new = new
        if data is not None:
            self._data = data
            if not new:
                self._stored_data = copy(data)

    def commit(self, **kw):
        key = self._parent.key_from_json(self._data)
        if not self._new:
            if self._data != self._stored_data:
                old_key = self._parent.key_from_json(self._stored_data)
                self._path = self._parent._update(old_key, key, self._data)
                if not self._is_index_key:
                    self._parent._update_indices(self._data, old_key, key)
        else:
            self._path = self._parent._insert(key, self._data, **kw)
            if not self._is_index_key:
                self._parent._insert_indices(self._data, key)
        self._stored_data = copy(self._data)
        self._new = False
        return self

    def delete(self):
        key = self._parent.key_from_json(self._data)
        del self._parent[key]
