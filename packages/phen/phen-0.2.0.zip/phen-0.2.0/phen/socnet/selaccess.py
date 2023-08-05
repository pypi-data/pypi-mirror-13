#!/usr/bin/env python
#-*- coding:utf-8 -*-

"""Selective file access through clearance levels."""

import os
import re
import json


class SelectiveAccess:
    def __init__(self, fs, prefix, extension, author=False):
        self.fs = fs
        path = prefix.split("/")
        if len(path) > 1:
            prefix = path[-1]
            path = "/".join(path[:-1])
        else:
            path = "."
        self.path = path
        self.prefix = prefix
        self.extension = extension
        self.uids = {}
        if not author:
            regex = r"^{}\.(\S+)\.{}$".format(re.escape(prefix), extension)
            fn_re = re.compile(regex)
            if not self.fs.exists(path):
                return
            for fname in self.fs.listdir(path):
                m = fn_re.match(fname)
                if m:
                    self.uids[m.group(1)] = m.group(1)
        else:
            try:
                with self.fs.open(self.fullname()) as deffile:
                    self.uids = json.loads(deffile.read())
            except IOError:
                pass

    def add_level(self, label=u'private'):
        if label in self:
            return
        uid = label if label == u'public' else u'private'
        while uid in self.uids:
            uid = os.urandom(4).encode('hex')
        self.uids[uid] = label
        return self.fullname(uid)

    def commit(self):
        tgrp = self.fs.set_creation_groups()
        with self.fs.open(self.fullname(), 'w') as out:
            out.write(json.dumps(self.uids))
        self.fs.set_creation_groups(tgrp)

    def fullname(self, uid=None):
        if uid is None:
            return "{0.path}/{0.prefix}.{0.extension}.def".format(self)
        else:
            return "{0.path}/{0.prefix}.{1}.{0.extension}".format(self, uid)

    def pick_one(self, avoid_public=True):
        if len(self.uids) > 1:
            for uid in self.uids:
                if not avoid_public or uid != u'public':
                    return self.fullname(uid)
        elif len(self.uids):
            return self.fullname(list(self.uids.keys())[0])

    def __contains__(self, label):
        return label in self.uids.values()

    def __len__(self):
        return len(self.uids)

    def __iter__(self):
        for uid, label in self.uids.items():
            yield label, uid, self.fullname(uid)
