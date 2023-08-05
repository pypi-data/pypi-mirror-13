# -*- coding:utf-8 -*-

"""
    FileSystem management classes.
"""

import logging

from phen import storage
from phen.event import Event
from .folder import Folder
from .operations import Operations


log = logging.getLogger(__name__)


class FileSystem(Operations):
    """
        Main class for encrypted file operations.
    """
    def __init__(self, ctx):
        self.ctx = ctx
        super(FileSystem, self).__init__()
        self.folder_modified = Event()
        self.entry_added = Event()
        self.entry_deleted = Event()

    def __repr__(self):
        from phen.util import shorten_hashes
        return u"<fs {}>".format(shorten_hashes(self.curdir))

    def rescan_tables(self):
        for folder in self.cache:
            folder.rescan_tables()

    def startup(self):
        if not storage.store.is_available((self.ctx.cidhash, 'root')):
            raise RuntimeError("Identity's root folder unavailable")
        super(FileSystem, self).startup()
        self.chdir()

    def create_identity_root(self, device=False):
        """
            Create the identity's main folder.
        """
        # if the private key is pure password based (ECC) the
        # identity folder may already exist in the filesystem
        idhash = self.ctx.cidhash
        if storage.store.is_available((idhash, None)):
            return True  # exists
        folder, fid = Folder.new(self, idhash, idhash, None, None)
        with storage.store.store((idhash, "public.key")) as out:
            self.ctx.cid.pub.save(out)
        self.add_to_folder_cache(folder)
        self.chdir()
        with self.ctx.groups(u'public'):
            self.mkdir(u"system")
            if not device:
                self.mkdir(u"system/devices", notif_tag='ignore')
        if not device:
            with self.ctx.groups():
                self.mkdir(u"system/config")
        return False  # doesn't exist - needs to be populated

    def request(self, fid_pair):
        """
            To be overridden by the communication module.
        """

    def export_fid_list(self, out, idhash, fid_list):
        """
            Add the files in the list to the zipfile.
        """
        from tempfile import NamedTemporaryFile
        self.flush_cache()
        for fid in fid_list:
            with NamedTemporaryFile() as tout:
                with storage.store.load((idhash, fid)) as infile:
                    data = True
                    while data:
                        data = infile.read(1 << 16)
                        tout.write(data)
                tout.flush()
                out.write(tout.name, "/".join((idhash, fid)))

    def sync(self, fid_pair, dl_fid_pair, mtime):
        """
            Syncronize the folder with its remote counterpart,
            supplied as an external file, and set the modification
            time to whichever is more recent.
        """
        from phen.util import fid2name
        log.debug("syncing {} {}".format(fid2name(fid_pair), mtime))
        if fid_pair == dl_fid_pair:
            log.error("trying to syncing oneself")
            return [], [], [], []
        local = self.open_folder(fid_pair, None, None)
        remote = Folder.load(self, dl_fid_pair, local.path,
                             None, local.key, sync=True)
        if remote.mtime == local.mtime:
            log.debug("mtime {} match, no sync needed".format(local.mtime))
            return [], [], [], []
        storage.store.lock(local, fid_pair)
        if local.store_mtime != local.modified_time:
            local._load_from_store()
        oldest_sync = self.ctx.cid.oldest_sync
        results = local.sync(self.ctx.cid, fid_pair[0] + fid_pair[1], remote,
                             self.ctx.groups, oldest_sync)
        local.set_modified(mtime)
        storage.store.remove(dl_fid_pair)
        return results
