# -*- coding:utf-8 -*-

import logging
from copy import copy


log = logging.getLogger("db.Storage")


class StorageBase(object):
    _has_children = False
    _children = []
    _indices = []

    def __init__(self, fs, parent=None, path=None, **kw):
        self._fs = fs
        self._parent = parent  # Item that contains this Storage
        self._name = kw.pop("name", getattr(self, "name", "storage"))
        ext = kw.pop("ext", getattr(self, "ext", "data"))
        self._fname = ".".join((self._name, ext))
        self._flat = kw.pop("flat", getattr(self, "flat", False))
        self._path = path if path is not None else (
            parent._path or parent._parent._path
        )
        if not self._flat:
            self._path = "/".join((self._path, self._fname))
        self.__setup_key(kw)
        self.__setup_layout(kw)
        self._initialized = False
        if kw:
            log.warn("unused parameters - " + ", ".join(kw))

    def key_from_json(self, json_data):
        return json_data.get(self.key)

    def __setup_key(self, kw):
        self.key = kw.pop("key", getattr(self, "key", None))
        kfj = kw.pop("key_from_json", None)
        if kfj is not None:
            self.key_from_json = kfj
        else:
            if self.key_from_json == StorageBase.key_from_json:
                if self.key is None:
                    raise RuntimeError("db.Storage without key")

    def __setup_layout(self, kw):
        from ..layout import SingleFolder, SingleFile, create_folder
        layout = kw.pop("layout", getattr(self, "layout", None))
        params = []
        if layout is None:
            layout = SingleFolder if self._has_children else SingleFile
        elif isinstance(layout, tuple):
            layout, params = layout[0], layout[1:]
        if self._has_children and layout.file_based:
            self._allow_diving = False
        if not params and self._has_children and not layout.file_based:
            # default initialization for storage with children must be mkdir
            params = [create_folder]
        self._layout = layout and layout(self, self._path, *params)

    def exists(self):
        return self._layout._exists

    def create(self):
        self._layout.create()

    def drop(self):
        if not self._flat and self._fs.exists(self._path):
            self._fs.rmtree(self._path)
        else:
            raise NotImplementedError(
                "dropping flat collections not supported yet"
            )

    def invalidate(self):
        self._layout.invalidate()

    def select(self, begin=None, end=None, filter_func=None):
        # todo: interruptible, and may yield partial results before
        # expensive operations (loading a btree node)
        cursor = self._layout.cursor(begin)
        end_doc = self._layout.cursor(end, end=True)
        while cursor.key is not None and cursor.key != end_doc.key:
            doc = self[cursor.key]
            if filter_func is None or filter_func(doc):
                yield doc
            cursor.next()

    def new(self, **kw):
        default = copy(self.default) if hasattr(self, "default") else {}
        if kw:
            default.update(kw)
        return self.Item(self, data=default)

    def insert(self, **kw):
        return self.new(**kw).commit()

    def insert_many(self, doc_list):
        return [
            getattr(self.new(**kw).commit(), self.key)
            for kw in doc_list
        ]

    def find(self, **kw):
        for doc in self.select():
            if all(getattr(doc, key, None) == kw[key] for key in kw):
                yield doc

    def find_one(self, **kw):
        for doc in self.find(**kw):
            return doc

    def __contains__(self, key):
        return key in self._layout

    __iter__ = select

    def __getitem__(self, key):
        path, data = self._layout[key]
        return self.Item(self, path, data, new=False)

    def __delitem__(self, key):
        self.delete(key)

    def _insert(self, key, json_data, **kw):
        return self._layout.insert(key, json_data, **kw)

    def _update(self, old_key, new_key, json_data):
        return self._layout.update(old_key, new_key, json_data)

    def delete(self, key):
        json_data = self[key]
        self._layout.delete(key)
        self._delete_indices(json_data, key)

    def _insert_indices(self, json_data, key):
        for name in self._indices:
            idx = getattr(self, name)
            if hasattr(idx, "_idx_insert"):
                idx._idx_insert(json_data, key)

    def _update_indices(self, json_data, old_key, key):
        for name in self._indices:
            idx = getattr(self, name)
            if hasattr(idx, "_idx_update"):
                idx._idx_update(json_data, old_key)

    def _delete_indices(self, json_data, key):
        for name in self._indices:
            idx = getattr(self, name)
            if hasattr(idx, "_idx_delete"):
                idx._idx_delete(json_data, key)
