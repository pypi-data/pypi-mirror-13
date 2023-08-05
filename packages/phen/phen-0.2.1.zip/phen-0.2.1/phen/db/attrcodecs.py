# -*- coding:utf-8 -*-

import dateutil.parser
from datetime import datetime

from .composable import AttributeCodec


class AutoIncrement(AttributeCodec):
    def __init__(self, name):
        self.name = name

    def __get__(self, obj, objtype):
        return obj._data.get(self.name)

    def __set__(self, obj, val):
        if val is None:
            obj._data[self.name] = obj._parent.auto_increment(self.name)
        else:
            obj._data[self.name] = val


class EpochAttribute(AttributeCodec):
    def __init__(self, name, fmt=None):
        self.name = name
        self.fmt = fmt

    def __get__(self, obj, objtype):
        return datetime.utcfromtimestamp(obj._data.get(self.name))

    def __set__(self, obj, val):
        from time import mktime, gmtime
        obj._data[self.name] = mktime(val.utctimetuple() if val else gmtime())


class DateTimeAttribute(AttributeCodec):
    def __init__(self, name, fmt=None):
        self.name = name
        self.fmt = fmt

    def __get__(self, obj, objtype):
        if self.fmt is not None:
            return datetime.strptime(obj._data.get(self.name), self.fmt)
        return dateutil.parser.parse(obj._data.get(self.name))

    def __set__(self, obj, val):
        if self.fmt is not None:
            obj._data[self.name] = val.strftime(self.fmt)
        obj._data[self.name] = val.isoformat()


class DateAttribute(AttributeCodec):
    def __init__(self, name, fmt=None):
        self.name = name
        self.fmt = fmt or "%Y-%m-%d"

    def __get__(self, obj, objtype):
        return datetime.strptime(obj._data.get(self.name), self.fmt).date()

    def __set__(self, obj, val):
        obj._data[self.name] = val.strftime(self.fmt)


class LabeledValue(AttributeCodec):
    def __init__(self, name, collection=None):
        self.name = name
        self.collection = collection or (name + "s")

    def __get__(self, obj, objtype):
        val = obj._data.get(self.name)
        collection = getattr(obj._parent._parent, self.collection)
        return collection[val].label

    def __set__(self, obj, label):
        collection = getattr(obj._parent._parent, self.collection)
        doc = collection.find_one(label=label)
        if doc is None:
            from phen.util.metric import list_similarity
            labels = [d.label for d in collection.find()]
            sim = list_similarity(3, label, labels)
            if not sim or not sim[0][0]:
                raise KeyError("invalid label - no suggestion", None, labels)
            raise KeyError("invalid label", sim[0][1], labels)
        obj._data[self.name] = doc.value
