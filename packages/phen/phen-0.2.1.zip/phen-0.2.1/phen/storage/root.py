#!/usr/bin/env python
#-*- coding:utf-8 -*-

"""
    Phen Root Folder Manager
"""

import os

import phen
from phen.util.filelock import Filelock


class RootFolder:
    def __init__(self, path):
        self.path = path
        self.fs = os.path.join(path, "filesystem")
        if not os.path.exists(self.fs):
            self.initialize_root()
        self.lock_owner = False

    def lock(self, contents, force=False):
        fname = os.path.join(self.path, "in-use")
        with Filelock(fname):
            if not force and os.path.exists(fname):
                with open(fname) as lock_file:
                    return lock_file.read()
            else:
                with open(fname, 'w') as lock_file:
                    lock_file.write(contents)
                    self.lock_owner = True
                phen.chown(fname)

    def unlock(self):
        if not self.lock_owner:
            return
        self.lock_owner = False
        fname = os.path.join(self.path, "in-use")
        with Filelock(fname):
            if os.path.exists(fname):
                os.unlink(fname)

    def initialize_root(self):
        """
            initialize phen's root with some default data
        """
        if not os.path.exists(self.path):
            os.makedirs(self.path)
            phen.chown(self.path)
        if os.path.exists(self.fs):
            return
        src_path = os.path.join(phen.phen_path, "data", "filesystem")
        if os.path.exists(src_path):
            import shutil
            shutil.copytree(src_path, self.fs)
        else:
            os.makedirs(self.fs)
        phen.chown(self.fs)
