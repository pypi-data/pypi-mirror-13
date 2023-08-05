# -*- coding:utf-8 -*-

"""

Meta-class magic for building the hierarchy with lazy-loaders.

"""

from .item import Item
from .base import StorageBase


class AttributeCodec(object):
    """Base class for encoding and decoding attributes for storage"""


class StorageGetter(object):
    """Lazy-loader for nested Storages"""

    def __init__(self, name, child, kw, is_idx):
        self.name = "_cs_" + name
        self.is_idx = is_idx
        if "name" not in kw and not hasattr(child, "name"):
            kw["name"] = name
        self.dive = kw.pop("dive", getattr(child, "dive", None))
        self.child = child
        self.kw = kw

    def __get__(self, obj, objtype):
        inst = getattr(obj, self.name, None)
        if inst is not None:
            return inst
        if not self.is_idx and getattr(obj, "_new", True):
            raise RuntimeError("not commited yet, child not allowed")
        allow_diving = not self.is_idx and getattr(
            obj._parent, "_allow_diving", True
        )
        dive = allow_diving if self.dive is None else self.dive
        if self.is_idx:
            fs = obj._fs
            path = obj._path
            if not dive:
                path = path[:path.rfind("/")]
        else:
            fs = obj._parent._fs
            path = obj._path if dive else obj._parent._path
            # if parent is SingleFile we must strip the filename
            if obj._path is None and not dive:
                path = path[:path.rfind("/")]
        obj._dive = dive
        inst = self.child(fs, obj, path, **self.kw)
        setattr(obj, self.name, inst)
        return inst


class StorageMetaClass(type):
    def __init__(cls, class_name, bases, namespace):
        if "Item" in namespace:
            item = namespace["Item"]
        else:
            # no explicitly specified Item, gotta make a new one
            item = getattr(cls, "Item", None)
            if item is None:
                b_items_g = (getattr(base, "Item", None) for base in bases)
                base_items = [base for base in b_items_g if base is not None]
                item = Item if not base_items else base_items[-1]
            item = type(class_name + "Item", (item,), {})
        setattr(cls, "Item", item)
        for key in namespace:
            attr = namespace[key]
            cls.attach_descriptors(key, attr, namespace, item)

    def _expand_attribute(cls, attr):
        if isinstance(attr, tuple):
            if not len(attr):
                return
            ccls = attr[0]
            params = attr[1] if len(attr) > 1 else {}
            self_ref = len(attr) > 2 and attr[2] == 1 and ccls is Storage
            return cls if self_ref else ccls, params
        else:
            return attr, {}

    def attach_descriptors(cls, key, attr, namespace, item):
        """attach descriptors to the Item and Storage classes"""
        ccls, params = cls._expand_attribute(attr)
        if not hasattr(ccls, "name"):
            if isinstance(params, dict) and "name" not in params:
                params["name"] = key
        if isinstance(ccls, type):
            if issubclass(ccls, Storage):
                cls.__process_storage(key, ccls, params, item)
            if issubclass(ccls, AttributeCodec):
                if not isinstance(params, dict):
                    raise TypeError("AttributeCodec parameter must be a dict")
                setattr(item, key, ccls(**params))
        elif isinstance(ccls, AttributeCodec):
            setattr(item, key, ccls)

    def __process_storage(cls, key, ccls, params, item):
        if not isinstance(params, dict):
            raise TypeError("db.Storage expected a parameter dict")
        is_idx = key.startswith("by_")
        lazy_loader = StorageGetter(key, ccls, params, is_idx)
        if is_idx:
            # attach a lazy-loader for the index
            setattr(cls, key, lazy_loader)
            # make sure we don't modify an ancestor class's indices
            cls._indices = cls._indices[:]
            cls._indices.append(key)
        else:
            # attach a lazy-loader for the inner Storage
            setattr(item, key, lazy_loader)
            delattr(cls, key)
            # make sure we don't modify an ancestor class's children
            cls._children = cls._children[:]
            cls._children.append(key)
        cls._has_children = True


Storage = StorageMetaClass("Storage", (StorageBase,), {})
