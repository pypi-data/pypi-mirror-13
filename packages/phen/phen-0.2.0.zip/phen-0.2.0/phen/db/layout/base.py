# -*- coding:utf-8 -*-


class Cursor:
    def __init__(self, parent, doc_it):
        self.parent = parent
        self.doc_it = doc_it
        self.key = next(doc_it) if doc_it is not None else None

    def next(self):
        try:
            self.key = next(self.doc_it) if self.doc_it is not None else None
        except StopIteration:
            self.key = None


class Layout(object):
    file_based = False

    def __init__(self, parent, path):
        self._parent = parent
        self._path = path
        self._exists = True

    def create(self):
        """Create an empty storage point if it does not exist yet"""

    def invalidate(self):
        """Discard any cached value and reload data from storage"""

    def __contains__(self, key):
        """Assert if the key belongs to this collection"""

    def __getitem__(self, key):
        """Return the data associated to this key"""

    def insert(self, key, json_data):
        """Associate the data to the specified key"""

    def update(self, old_key, new_key, json_data):
        """Update the data associated to the key"""

    def delete(self, key):
        """Remove the key and its data from this collection"""

    def cursor(self, key, end=False):
        """Build a cursor to iterate over the specified range"""
