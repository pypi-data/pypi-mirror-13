# -*- coding:utf-8 -*-

"""
    Folder abstraction classes.
"""

import os
import zlib
import json
import time
import errno
import threading

from base64 import b64encode as b64e, b64decode as b64d

from phen.util import shorten_hashes, fill_io_error
from phen import storage

from .filemeta import Metadata, fm_json_load
from .contents import Contents
from . import filemeta


def ensure_updated(method):
    import functools

    @functools.wraps(method)
    def decorated(self, *p, **kw):
        if self.store_mtime != self.modified_time:
            self._load_from_store()
        return method(self, *p, **kw)
    return decorated


class Folder(Contents):
    """
        The main folder management class.
    """
    is_folder = True
    delay_save = True

    def __init__(self, fs, fid_pair, path,
                 parent, key, is_remote=False):
        Contents.__init__(self)
        if path is None and fid_pair[1] == "root":
            path = fid_pair[0]
        if __debug__ and path and path[0] == '/':
            raise RuntimeError("Folder.path must be absolute: " + path)
        self.path = path
        self.opened_by = fs.ctx.cidhash
        self.cache = {}
        self.fs = fs
        self._parent = parent
        self.key = key
        self.idhash, self.fid = fid_pair
        self.is_remote = is_remote
        self.is_closed = False
        self.no_bulk_save = False
        self.save_lock = threading.Lock()
        self.dirty = False
        self.cache_serial = 0
        self.modified_time = 0
        self.store_mtime = 0  # if != modified_time, data must be reloaded
        self.store_lock = False
        if not self.fs.ctx.cid:
            return
        l_fid = storage.store.local_data_fid(fid_pair, self.fs.ctx.cid, "key")
        if not storage.store.is_available(l_fid):
            with storage.store.store(l_fid, self.fs.ctx.cid, 'wt') as out:
                json.dump([path, key], out)

    def __repr__(self):
        path = shorten_hashes(self.path[43:] if self.path else "****")
        dty = '*' if self.dirty else ''
        return u"<%s%x[%s::%s] %s>" % (
            dty, id(self), self.idhash[:5], self.fid[:5], path
        )

    @staticmethod
    def calculate_fid(idhash, parent_fid, nonce=None):
        from hashlib import sha256
        from phen.util import bin2idhash
        sha = sha256((idhash + parent_fid).encode("ascii"))
        if nonce is None:
            nonce = b64e(os.urandom(6)).decode("ascii")
        sha.update(nonce.encode("ascii"))
        fid = bin2idhash(sha.digest())
        return fid, nonce

    @staticmethod
    def new(fs, idhash, path, parent, key, **kw):
        if not fs.ctx.cid:
            raise ValueError("Current identity not set")
        if parent:
            p_def = parent.fid, parent.key
            nonce = kw.get("nonce")  # recovery from backup
            fid, nonce = Folder.calculate_fid(idhash, p_def[0], nonce)
        else:
            p_def = "", ""
            fid, nonce = "root", ""
        fid_pair = (idhash, fid)
        if storage.store.is_available(fid_pair):
            fill_io_error(errno.EEXIST, *fid_pair)
        folder = Folder(fs, fid_pair, path, parent, key)
        storage.store.lock(folder)
        folder.metadata = {
            "author": fs.ctx.cidhash,
            "fid": fid,
            "nonce": nonce,
            "origParent": p_def,
            "curParent": p_def,
            "tags": kw.get("tags", []),
        }
        notif_tag = kw.get("notif_tag", False)
        if notif_tag:
            folder.notif_tag = notif_tag
        keep_history = kw.get("keep_history", False)
        if keep_history:
            folder.keep_history = keep_history
        folder.set_modified()
        return folder, fid

    @property
    def parent(self):
        if self._parent is None:
            fid, key = self.metadata.get("curParent", (None, None))
            if not fid:
                return None
            path = "/".join(self.path.split("/")[:-1]) if self.path else None
            self._parent = self.fs.open_folder((self.idhash, fid), path, key)
            if not self.path and self._parent and self._parent.path:
                # todo: should take multis in consideration
                self.path = "/".join((self._parent.path, self.name))
        return self._parent

    @parent.setter
    def parent(self, new_parent):
        storage.store.lock(self)
        fmeta = new_parent.folder_fmeta
        p_def = (fmeta.fid, fmeta.key) if fmeta else ("root", None)
        self.metadata["curParent"] = p_def
        if "signature" in self.metadata:
            del self.metadata["signature"]
        self._parent = new_parent

    @property
    def folder_fmeta(self):
        if self.parent is None:
            return None
        # retrieve the fmeta from the parent's contents (real, not multi)
        return self.parent.get_filemeta(fid=self.fid)

    @property
    def name(self):
        fmeta = self.folder_fmeta
        # retrieve the name from the parent's contents (real, not multi)
        return "root" if not fmeta else fmeta.name

    @property
    def fid_pair(self):
        return (self.idhash, self.fid)

    @property
    def author(self):
        return self.metadata['author']

    @property
    def metadata_mtime(self):
        self.apply_update()
        return self.metadata['mtime']

    @property
    def mtime(self):
        self.apply_update()
        return self.modified_time

    @property
    def notif_tag(self):
        return self.metadata.get("notif_tag", None)

    @notif_tag.setter
    def notif_tag(self, tag):
        storage.store.lock(self)
        self.metadata["notif_tag"] = tag
        if "signature" in self.metadata:
            del self.metadata["signature"]

    @property
    def keep_history(self):
        return self.metadata.get("keep_history", False)

    @keep_history.setter
    def keep_history(self, active):
        storage.store.lock(self)
        self.metadata["keep_history"] = active
        if "signature" in self.metadata:
            del self.metadata["signature"]

    # -=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=:[ Loading

    @staticmethod
    def load(fs, fid_pair, path, parent, key, sync=False):
        if sync:
            from phen.util import strip_hex_suffix
            actual_fid_pair = (fid_pair[0], strip_hex_suffix(fid_pair[1]))
            folder = Folder(fs, actual_fid_pair, path,
                            parent, key, is_remote=True)
            with storage.store.load(fid_pair) as infile:
                folder._load_data(infile)
        else:
            folder = Folder(fs, fid_pair, path, parent, key)
            storage.store.subscribe(folder, lock=True)
            try:
                folder._load_from_store()
            finally:
                storage.store.unlock(folder, '-')
        return folder

    def _load_from_store(self):
        fid_pair = self.idhash, self.fid
        if not storage.store.is_available(fid_pair):
            self.fs.request(fid_pair)
            if not storage.store.is_available(fid_pair):
                raise fill_io_error(errno.EAGAIN, *fid_pair)
        self._load_cache(fid_pair)
        with storage.store.load(fid_pair) as infile:
            self._load_data(infile)
        if self.fs.ctx.cid:
            self._save_cache(fid_pair)

    def _load_cache(self, fid_pair):
        self.cache = {}
        if not self.fs.ctx.cid:
            return
        cache_fid = storage.store.local_data_fid(
            fid_pair, self.fs.ctx.cid, "cache",
        )
        if not storage.store.is_available(cache_fid):
            return
        try:
            with storage.store.load(cache_fid, self.fs.ctx.cid) as infile:
                self.cache = json.load(infile)
        except IOError:
            self.cache = {}

    def _load_data(self, infile):
        try:
            if self.key:
                from phen.crypto import sym
                ivec = infile.read(16)
                dec = sym.Decryptor(infile, b64d(self.key), ivec, False)
                compressed = dec.read()
            else:
                compressed = infile.read()
            data = zlib.decompress(compressed).decode("utf8")
        except zlib.error:
            raise TypeError("Corrupted data: {0.idhash}/{0.fid}".format(self))
        self.size = len(data)
        try:
            self._from_json(data)
        except ValueError:
            raise TypeError("Not a folder: {0.idhash}/{0.fid}".format(self))

    def _from_json(self, code):
        """
            Load the data from the json code.
        """
        json_s = json.loads(code, object_hook=fm_json_load)
        required_kws = ('version', 'contents', 'metadata')
        if any(kw not in json_s for kw in required_kws):
            raise TypeError("Not a folder")
        self.metadata = json_s["metadata"]
        self.store_mtime = self.modified_time = json_s.get("mtime", 0)
        if not self.fs.ctx.cid:
            self.from_dict(json_s, self.idhash + self.fid, None)
        else:

            def pkgetter(idhash):
                from phen.socnet.peer import Peer
                return Peer(None, idhash).get_pubkey()

            self.from_dict(
                json_s, self.idhash + self.fid,
                self.fs.ctx.cid and self.fs.ctx.groups,
                self.is_remote and pkgetter  # only verify data if remote
            )

    def rescan_tables(self):
        Contents.rescan_tables(self, self.fs.ctx.groups)

    def apply_update(self):
        """
            Apply any pending external changes.
        """
        if self.store_mtime != self.modified_time:
            self._load_from_store()

    # -=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=:[ Saving

    def external_modification(self, mtime):
        """
            Mark the folder as externally changed - data obsolete.
        """
        if self.is_closed:
            return
        self.store_mtime = mtime
        self.cache_serial += 1
        self.fs.folder_modified(self, self.notif_tag, True)

    def set_modified(self, mtime=None):
        """
            Mark folder to be saved.
        """
        if self.opened_by != self.fs.ctx.cidhash:
            msg = "m: Id changed ({}-> {}), folder {} should have been closed."
            fmtd = msg.format(self.opened_by, self.fs.ctx.cidhash, self.path)
            raise RuntimeError(shorten_hashes(fmtd))
        if self.is_closed:
            raise RuntimeError("Attempting to write on a closed folder" +
                               self.path)
        storage.store.lock(self, interruptible=True)
        self.sync_mtime = mtime and max(self.modified_time, mtime)
        self.store_mtime = self.modified_time = time.time()
        self.cache_serial += 1
        if not self.delay_save:
            return self._save()
        self.dirty = True
        self.fs.dsave.add(self)

    def close_folder(self, force=False):
        if not force and (self.is_closed or self.no_bulk_save):
            return True
        self.flush()
        self.is_closed = True
        self.contents = None
        return True

    def flush(self):
        """
            Write any pending operation.
        """
        with self.save_lock:
            if self.dirty:
                self._save()

    def _save(self):
        """
            Update the folder storage, in response to a set_modified call.
            Note: the modified_lock must be locked prior to calling this.
        """
        self.dirty = False
        if self.opened_by != self.fs.ctx.cidhash:
            msg = "Id changed ({}-> {}), folder {} should have been closed."
            fmtd = msg.format(self.opened_by, self.fs.ctx.cidhash, self.path)
            raise RuntimeError(shorten_hashes(fmtd))
        if self.sync_mtime:
            self.modified_time = self.sync_mtime
            self.sync_mtime = 0
        fid_pair = self.idhash, self.fid
        compressed = zlib.compress(self._to_json().encode("utf8"), 9)
        ciphered = compressed
        if self.key:
            from phen.crypto import sym
            ciphered = ivec = os.urandom(16)
            ciphered += sym.encrypt(compressed, b64d(self.key), ivec, False)
        with storage.store.store(fid_pair, folder=True) as out:
            out.write(ciphered)
        storage.store.unlock(self, self.modified_time, self.keep_history)
        self._save_cache(fid_pair)
        self.fs.folder_modified(self, self.notif_tag, False)

    def _save_cache(self, fid_pair):
        cache_fid = storage.store.local_data_fid(
            fid_pair, self.fs.ctx.cid, "cache",
        )
        if not self.cache:
            if storage.store.is_available(cache_fid):
                storage.store.remove(cache_fid)
            return
        with storage.store.store(cache_fid, self.fs.ctx.cid) as out:
            out.write(json.dumps(self.cache))

    def _to_json(self, enc=True):
        """
            Generate a json representation of the folder contents.
        """
        stru = self.to_dict(self.fs.ctx.cid, self.idhash + self.fid)
        stru["version"] = 0
        if "signature" not in self.metadata:
            if self.fs.ctx.cidhash != self.metadata["author"]:
                raise ValueError("Only the author may change folder metadata.")
            self.metadata["mtime"] = time.time()
            to_sign = json.dumps(self.metadata, sort_keys=True,
                                 separators=(',', ':')).encode("utf8")
            self.metadata["signature"] = self.fs.ctx.cid.sign(to_sign)
        stru["metadata"] = self.metadata
        stru["mtime"] = self.modified_time
        if enc:
            return json.dumps(stru)
        return json.dumps(stru, sort_keys=True, indent=4,
                          separators=(',', ': '))

    # -=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=:[ Folder Manipulation

    def check_access(self, fmeta, add=True):
        return self.access_control.check(self.fs.ctx.cid, add, fmeta)

    def add_file(self, fmeta, group_ids=None, touch=True):
        """
            Add or update a file to the folder.
        """
        storage.store.lock(self)
        if self.store_mtime != self.modified_time:
            self._load_from_store()
        author_id = self.fs.ctx.cid
        group_mgr = self.fs.ctx.groups
        if touch:
            fmeta.touch()
        if not group_ids:
            group_ids = group_mgr.initial_groups
        try:
            Contents.add_file(self, author_id, fmeta, group_ids, group_mgr)
        except:
            storage.store.unlock(self, '-')
            raise
        self.set_modified()  # increment cache_serial
        if len(self.file_dict[fmeta.name]) == 1:
            self.fs.update_cache_item(
                "/".join((self.path, fmeta.name)), self.idhash, fmeta, self
            )
        self.fs.entry_added(self, fmeta)

    def delete_file(self, fmeta, group_ids=None, keep_file=False):
        """
            Remove the file from the folder.
        """
        storage.store.lock(self)
        if self.store_mtime != self.modified_time:
            self._load_from_store()
        author_id = self.fs.ctx.cid
        group_mgr = self.fs.ctx.groups
        timestamp = 0 if keep_file else time.time()
        try:
            Contents.delete_file(self, author_id, fmeta, timestamp,
                                 group_ids, group_mgr)
        except:
            storage.store.unlock(self, '-')
            raise
        self.set_modified()
        if not fmeta.is_file():
            self.fs.update_cache_item("/".join((self.path, fmeta.name)))
        if not keep_file and not self.keep_history:
            storage.store.remove((self.idhash, fmeta.fid))
        self.fs.entry_deleted(self, fmeta)

    @ensure_updated
    def exists(self, name, any_authors=True):
        """
            Check existence of the specified file/folder, optionally
            restricting to only entries owned by the current identity.
        """
        if name not in self.file_dict:
            return False
        cid = self.fs.ctx.cidhash
        return any_authors or cid in self.file_dict[name]

    @ensure_updated
    def is_multi(self, name):
        """
            Return true if the specified file/folder is a multientry.
        """
        if name not in self.file_dict:
            raise fill_io_error(errno.ENOENT, name)
        return len(self.file_dict[name]) > 1

    @ensure_updated
    def listdir(self):
        """
            Return the current list of entries of the folder.
        """
        return list(self.file_dict.keys())

    @ensure_updated
    def list_multi(self, name):
        """
            Return the list of entries in the specified multi.
        """
        if not self.is_multi(name):
            raise fill_io_error(errno.ENOTDIR, name)
        return list(self.file_dict[name].keys())

    @ensure_updated
    def filemeta(self, name, multi=None, no_error=False):
        """
            Return the metadata that describes the path.
        """
        if multi is not None:
            if multi not in self.file_dict:
                raise fill_io_error(errno.ENOENT, multi)
            if name not in self.file_dict[multi]:
                if no_error:
                    return Metadata(name=name, type=filemeta.INVALID)
                else:
                    raise fill_io_error(errno.ENOENT, multi, name)
            return self.file_dict[multi][name]
        if name in self.file_dict:
            if len(self.file_dict[name]) > 1:
                return Metadata(name=name, type=filemeta.MULTI)
            return list(self.file_dict[name].values())[0]
        if no_error:
            return Metadata(name=name, type=filemeta.INVALID)
        raise fill_io_error(errno.ENOENT, name)

    @ensure_updated
    def mkdir(self, name, path, **kw):
        fmeta = Metadata(name=name, type=filemeta.FOLDER)
        from phen.crypto import random_key
        fmeta.key = random_key()
        folder, fmeta.fid = Folder.new(self.fs, self.idhash,
                                       path, self, fmeta.key, **kw)
        self.add_file(fmeta)
        self.fs.add_to_folder_cache(folder)
        return folder

    @ensure_updated
    def _close(self, tcf, oldfmeta):
        """
            Close the previously opened file, updating the folder listing.
            Note: this is not called when file is only in reading mode.
        """
        if oldfmeta.fid is not None:
            old_groups = self.get_groups(oldfmeta)
            self.delete_file(oldfmeta)
            self.add_file(tcf.filemeta, old_groups)
        else:
            self.add_file(tcf.filemeta)
