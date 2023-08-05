# -*- coding:utf-8 -*-

import os
from copy import copy
from base64 import urlsafe_b64encode as b64e

from . import composable


def gen_rid(size):
    """
        Generate a random id with the given size.
    """
    return str(b64e(os.urandom(size)))


class DocumentNotBoundToPath(RuntimeError):
    """The doc has not been commited yet, or the layout is file based"""
    def __init__(self):
        RuntimeError.__init__(self, DocumentNotBoundToPath.__doc__)


class Document(composable.Storage.Item):
    def __init__(self, parent, path=None, data=None, new=True):
        self._data = data
        super(Document, self).__init__(parent, path, data, new)

    def commit(self, **kw):
        tdata = copy(self._data)
        super(Document, self).commit(**kw)
        self._data = tdata
        self._stored_data = copy(self._data)
        return self

    def __getattr__(self, attr):
        """
            Accessor for the doc's attributes and for
            the doc methods defined in the Collection object.
        """
        if attr[0] == "_" or attr in dir(self):
            return super(Document, self).__getattribute__(attr)
        data = super(Document, self).__getattribute__("_data")
        if attr in data:
            return data.get(attr)
        parent = super(Document, self).__getattribute__("_parent")
        obj = getattr(parent, attr, None)
        if obj is not None:
            from functools import partial
            return partial(obj, self)
        raise AttributeError("no attribute or method named " + attr)

    def __setattr__(self, attr, val):
        """
            Accessor for the doc's attributes.
        """
        if attr[0] == "_" or attr in dir(self):
            super(Document, self).__setattr__(attr, val)
        else:
            self._data[attr] = val

    @property
    def data(self):
        """Return the file bound to the doc as a byte string."""
        if self._path is None:
            raise DocumentNotBoundToPath()
        with self._parent._fs.open(self._path, 'rd') as inf:
            return inf.read()

    @property
    def json(self):
        """Return the file bound to the doc as a JSON object."""
        if self._path is None:
            raise DocumentNotBoundToPath()
        return self._parent._fs.json_read(self._path)

    def open(self, name=None, mode='rd'):
        """Open the file path bound to the doc or a subpath."""
        if self._path is None:
            raise DocumentNotBoundToPath()
        path = self._path
        if name is not None:
            path = "/".join((path, name))
        return self._parent._fs.open(path, mode)

    def write(self, json_data=None, data=None):
        """Write either a JSON object or a byte string"""
        if self._path is None:
            raise DocumentNotBoundToPath()
        if json_data is not None:
            return self._parent._fs.json_write(self._path, json_data)
        with self._parent._fs.open(self._path, 'w') as out:
            return out.write(data)

    def convert(self, fname):
        """
            Convert the path into a folder, moving the current contents
            into the specified inner file.
        """
        if self._path is None:
            raise DocumentNotBoundToPath()
        xattr = self._parent._fs.xattr(self._path)
        tmp_path = self._path + ".tmp"
        self._parent._fs.rename(self._path, tmp_path)
        self._parent._fs.mkdir(self._path)
        self._parent._fs.rename(tmp_path, "/".join((self._path, fname)))
        self._parent._fs.xattr(self._path, xattr)


class Collection(composable.Storage):
    rid_size = 0  # times 3
    ext = "docs"
    Item = Document

    def __init__(self, fs, parent=None, path=None, **kw):
        if parent is None and "name" not in kw and not hasattr(self, "name"):
            kw["name"] = self.__class__.__name__.lower()
        if not (hasattr(self, "key") and "key" not in kw):
            self.key = "rid"
            if not self.rid_size:
                self.rid_size = 2  # 1/2^48 chance of collision
        super(Collection, self).__init__(fs, parent, path, **kw)

    def new(self, **kw):
        item = super(Collection, self).new(**kw)
        if self.rid_size and "rid" not in item._data:
            item._data["rid"] = gen_rid(self.rid_size * 3)
        return item

    def dump_schema(self):
        retv = {
            k: getattr(self, k, None)
            for k in "ext _name rid_size key default _flat _dive".split()
        }
        # todo: if _has_children dump their schema, and indices'
        return retv

    def auto_increment(self, kwid, only_check=False, bump=None):
        try:
            xattr = self._fs.xattr(self._path)
        except IOError:
            self.create()
            xattr = self._fs.xattr(self._path)
        ais = xattr.setdefault("ais", {})
        val = ais.setdefault(kwid, 0)
        if not only_check:
            val = max(val, bump)
            if ais[kwid] <= val:
                val += 1
                ais[kwid] = val
                self._fs.xattr(self._path, xattr)
        return val


class LabeledValues(Collection):
    default = {
        "value": "0",
        "label": ""
    }
    key = "value"

    def insert_labels(self, labels, start=0):
        return self.insert_many(
            dict(value=str(v), label=l)
            for v, l in enumerate(labels, start)
        )
