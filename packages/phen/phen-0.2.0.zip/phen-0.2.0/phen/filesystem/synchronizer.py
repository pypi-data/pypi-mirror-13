# -*- coding:utf-8 -*-

import time
import logging

from tempfile import NamedTemporaryFile

from phen import storage
from phen.util import fid2name


log = logging.getLogger(__name__)


class SyncBase:
    def __init__(self, fs):
        self.fs = fs
        self.retriever = self.retrieve()
        next(self.retriever)

    def retrieve(self):
        dl_fid_pair, mtime = None, True
        while True:
            fid_pair, folder = yield dl_fid_pair, mtime
            # retrieve fid_pair
            raise NotImplementedError

    def sync_folder(self, idhash, fid=None, apply_accepted=True):
        if fid is None:
            # idhash is assumed to be a path
            fid = self.fs.filemeta(idhash).fid
            __debug__ and fid2name((self.fs.ctx.cidhash, fid), idhash)
            idhash = self.fs.ctx.cidhash
        fid_pair = idhash, fid
        existed = storage.store.is_available(fid_pair)
        dl_fid_pair, modified = self.retriever.send((fid_pair, existed))
        if not existed:
            if not dl_fid_pair:
                return False
            folder = self.fs.open_folder(fid_pair, None, None)
            results = [list(folder.fid_dict.keys()), []]
        else:
            if not dl_fid_pair:
                return modified is False
            results = self.fs.sync(fid_pair, dl_fid_pair, modified)
        if apply_accepted:
            for deletion in results[1]:
                storage.store.remove((idhash, deletion))
            for addition in results[0]:
                fid_pair = idhash, addition
                if not storage.store.is_available(fid_pair):
                    self.retriever.send((fid_pair, False))
        return True

    def sync(self, src_did=None, stime=None):
        self.sync_folder("system/devices")
        for did in self.fs.cid.device_list(False):
            self.sync_folder("system/devices/" + did)
        self.fs.cid.load_sync_status()
        for did in self.fs.cid.device_list(False):
            if self.sync_folder("system/devices/{}/changelog".format(did)):
                self.sync_changelog(did)
        if src_did is not None:
            self.fs.cid.update_sync_status(src_did, stime)

    def sync_changelog(self, did):
        log.info("syncing with changelogs of '{}'".format(did))
        clog_path = "system/devices/{}/changelog".format(did)
        last_sync = self.fs.cid.last_sync(did)
        sync_period = 30 * 60  # todo: cfg.sync_period
        try:
            files = [fname for fname in self.fs.listdir(clog_path)
                     if float(fname) >= last_sync - sync_period]
        except ValueError:
            log.error("invalid changelog file name for '{}'".format(did))
            return
        log.info("{} changelogs to compile".format(len(files)))
        to_sync = set()
        for fname in files:
            with self.fs.open("/".join((clog_path, fname))) as clog:
                to_sync.update(clog.read().splitlines())
        log.info("{} folders changed since {}"
                 .format(len(to_sync), time.ctime(last_sync)))
        for entry in to_sync:
            entry = entry.split()
            if len(entry) == 2:
                fid, idhash = entry
            else:
                idhash, fid = self.fs.ctx.cidhash, entry[0]
            self.sync_folder(idhash, fid)


class SyncFromZipFile(SyncBase):
    def __init__(self, infile, fs):
        import zipfile
        if not isinstance(infile, zipfile.ZipFile):
            infile = zipfile.ZipFile(infile)
        self.infile = infile
        SyncBase.__init__(self, fs)

    def retrieve(self):
        dl_fid_pair, mtime = None, None
        entries = self.infile.namelist()
        store = storage.store
        while True:
            fid_pair, folder = yield dl_fid_pair, mtime
            log.info("retrieving {} from zip".format(fid2name(fid_pair)))
            entry = "/".join(fid_pair)
            if entry not in entries:
                log.warn(fid2name(fid_pair) + " extraction failed")
                dl_fid_pair, mtime = None, True
                continue
            # info = self.infile.getinfo(entry)
            if store.is_available(fid_pair):
                if not folder:
                    log.info(fid2name(fid_pair) + " already in fs")
                    dl_fid_pair = None
                    continue
            from phen.util import hex_suffix
            dl_fid_pair = fid_pair[0], hex_suffix(fid_pair[1])
            with self.infile.open(entry) as zinf:
                with store.store(dl_fid_pair) as out:
                    # filename = out.name
                    data = True
                    while data:
                        data = zinf.read(1 << 16)
                        out.write(data)
            log.info(fid2name(fid_pair) + " extraction succeeded")

    def sync_devices(self):
        for did in self.fs.cid.device_list():
            self.sync_folder(did, "root")


class SyncToZipFile:
    def __init__(self, out, fs):
        from phen.util import cvt_to_zipfile
        self.out = cvt_to_zipfile(out)
        self.fs = fs

    def pack(self, fid_pair):
        if storage.store.is_available(fid_pair):
            with storage.store.load(fid_pair) as infile:
                if hasattr(infile, "name"):
                    self.out.write(infile.name, "/".join(fid_pair))
                else:
                    with NamedTemporaryFile() as out:
                        while True:
                            data = infile.read(1 << 16)
                            if not data:
                                break
                            out.write(data)
                        out.flush()
                        self.out.write(out.name, "/".join(fid_pair))
            return True
        else:
            log.debug(fid2name(fid_pair) + " not available")
            return False

    def pack_folder(self, idhash, fid=None):
        if fid is None:
            # idhash is assumed to be a path
            fid = self.fs.filemeta(idhash).fid
            __debug__ and fid2name((self.fs.ctx.cidhash, fid), idhash)
            idhash = self.fs.ctx.cidhash
        fid_pair = (idhash, fid)
        if not self.pack(fid_pair):
            return
        folder = self.fs.open_folder(fid_pair, None, None)
        for fid in folder.fid_dict:
            self.pack((idhash, fid))

    def sync(self, dest_did=None):
        curdir = self.fs.chdir()
        self.pack_folder("system/devices")
        self.fs.cid.load_sync_status()
        if dest_did and dest_did in self.fs.cid.inverse_sync_status:
            last_sync = self.fs.cid.inverse_sync_status[dest_did]
        else:
            last_sync = self.fs.cid.oldest_sync
        to_sync = set()
        total = 0
        for did in self.fs.cid.device_list():
            self.pack_folder("system/devices/" + did)
            if did == dest_did:
                continue
            clog_path = "system/devices/{}/changelog".format(did)
            self.pack_folder(clog_path)
            sync_period = 30 * 60  # todo: cfg.sync_period
            try:
                files = [fname for fname in self.fs.listdir(clog_path)
                         if float(fname) >= last_sync - sync_period]
            except ValueError:
                log.error("invalid changelog file name for '{}'".format(did))
                files = []
            log.info("{} changelogs to compile from {}"
                     .format(len(files), did))
            total += len(files)
            for fname in files:
                path = "/".join((clog_path, fname))
                with self.fs.open(path) as clog:
                    to_sync.update(clog.read().splitlines())
        log.info("{} changelogs compiled".format(total))
        log.info("{} folders changed since {}"
                 .format(len(to_sync), time.ctime(last_sync)))
        for entry in to_sync:
            entry = entry.split()
            if len(entry) == 2:
                fid, idhash = entry
            else:
                idhash, fid = self.fs.ctx.cidhash, entry[0]
            self.pack_folder(idhash, fid)
        self.fs.chdir(curdir)

    def sync_devices(self):
        for did in self.fs.cid.device_list():
            self.pack_folder(did, "root")
