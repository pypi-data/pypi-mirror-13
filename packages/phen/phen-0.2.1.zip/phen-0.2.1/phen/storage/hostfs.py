# -*- coding:utf-8 -*-

"""
    Storage in the Host OS Filesystem
"""

import os
import phen
from .acc_ctrl import AccessController


class HostFS(AccessController):
    def __init__(self, device_key, root_path, net_addr=None):
        AccessController.__init__(self, root_path, net_addr, lock=False)
        self.lookup_cache = (None, None), None
        self.dev_key = device_key
        self.blocks = {}
        self.set_owner = phen.cfg.get("user") != 0

    def device_key(self, data=None):
        path = os.path.join(self.root.path, self.dev_key)
        if data is None:
            if os.path.exists(path):
                with open(path, 'rt') as kfile:
                    return kfile.read()
        else:
            with open(path, 'wb') as out:
                out.write(data)
            if self.set_owner:
                phen.chown(path)

    def list_root(self):
        from phen.util import is_idhash
        return [idhash for idhash in os.listdir(self.root.fs)
                if is_idhash(idhash)]

    def identity_folder(self, fid_pair, create=False):
        """
            Return a path based on the identity hash and
            file identifier, hashing into subfolders.
        """
        if not create and self.lookup_cache[0] == fid_pair:
            return self.lookup_cache[1]
        idhash, fid = fid_pair
        if fid:
            folder = os.path.join(self.root.fs, idhash, fid[:2])
        else:
            folder = os.path.join(self.root.fs, idhash)
        if create and not os.path.exists(folder):
            if fid:
                idfolder = os.path.join(self.root.fs, idhash)
                if not os.path.exists(idfolder):
                    os.mkdir(idfolder)
                    if self.set_owner:
                        phen.chown(idfolder)
            os.mkdir(folder)
            if self.set_owner:
                phen.chown(folder)
        retv = os.path.join(folder, fid[2:]) if fid else folder
        self.lookup_cache = fid_pair, retv
        return retv

    def is_available(self, fid_pair, partial=False):
        """
            Check the availability of a file.
        """
        path = self.identity_folder(fid_pair)
        if os.path.exists(path + ".blocks"):
            return partial and 'partial'
        return os.path.exists(path)

    def local_data_fid(self, fid_pair, identity, description):
        """
            Transform a genuine fid into one for local data storage.
        """
        from phen.util import bin2idhash
        from hashlib import sha256
        code = "".join(fid_pair + (identity.hash, description))
        h = sha256(code.encode("utf8"))
        return ("local", bin2idhash(h.digest()))

    def size(self, fid_pair):
        path = self.identity_folder(fid_pair)
        if os.path.exists(path):
            return os.stat(path).st_size
        return -1

    def load(self, fid_pair, identity=None):
        # if identity:
        #     decrypt
        path = self.identity_folder(fid_pair)
        return open(path, 'rb')

    def store(self, fid_pair, identity=None, mode='wb', folder=False):
        # if identity:
        #     encrypt
        path = self.identity_folder(fid_pair, True)
        if folder:
            path += ".tmp"
        retv = open(path, mode)
        if self.set_owner:
            phen.chown(path)
        return retv

    def unlock(self, folder, mtime, keep_history=False):
        """
            Release folder from exclusive use.
        """
        if mtime == '-':
            AccessController.unlock(self, folder, mtime)
            return
        path = self.identity_folder(folder.fid_pair)
        if keep_history and os.path.exists(path):
            dpath = path + "." + repr(mtime)
            import shutil
            with open(path, 'rb') as fsrc:
                with open(dpath, 'wb') as fdst:
                    shutil.copyfileobj(fsrc, fdst)
            if self.set_owner:
                phen.chown(dpath)
        os.rename(path + ".tmp", path)
        AccessController.unlock(self, folder, mtime)

    def remove(self, fid_pair):
        path = self.identity_folder(fid_pair)
        if os.path.exists(path):
            os.unlink(path)

    def new_tempfile(self):
        from tempfile import NamedTemporaryFile
        return NamedTemporaryFile(dir=self.root.fs, delete=False)

    def store_tempfile(self, tempfile, fid_pair):
        path = self.identity_folder(fid_pair, True)
        os.rename(tempfile.name, path)
        if self.set_owner:
            phen.chown(path)

    def open_blocks(self, fid_pair, mode='r+b', restart=False):
        from .blocks import BlocksManager
        if fid_pair in self.blocks:
            return self.blocks[fid_pair]
        try:
            path = self.identity_folder(fid_pair) + ".blocks"
            blocks = open(path, mode)
            if self.set_owner:
                phen.chown(path)
        except IOError:
            return 'done'
        self.blocks[fid_pair] = BlocksManager(blocks, path, restart)
        return self.blocks[fid_pair]

    def close_blocks(self, fid_pair, remove):
        if fid_pair not in self.blocks:
            return False
        self.blocks.pop(fid_pair).finished(remove)
