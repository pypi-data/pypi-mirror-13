# -*- coding:utf-8 -*-

"""
    Filesystem change logging.
"""

import logging


log = logging.getLogger(__name__)


class ChangeLog:
    def __init__(self, parent, time_span=30 * 60):
        self.logger = parent
        self.start = None
        self.time_span = time_span
        self.fids = {}
        self.next = None

    def check(self, folder):
        if self.start is None:
            self.start = folder.mtime
            self.fpath = "/".join((self.logger.clog_path, str(self.start)))
        # first modification?
        if folder.fid not in self.fids:
            # is the change not within our time window?
            if folder.mtime > self.start + self.time_span:
                self.forward(folder)
            else:
                self.add(folder)
        else:
            # has the first modification expired?
            if folder.mtime > self.fids[folder.fid] + self.time_span:
                self.forward(folder)
        # should we expect more modifications?
        if folder.mtime > self.start + self.time_span * 2:
            return self.next
        return self

    def forward(self, folder):
        if self.next is None:
            self.next = ChangeLog(self.logger, self.time_span)
        self.next.check(folder)

    def add(self, folder):
        from .traverse import FilemetaCache
        from .operations import _open as fop_open
        self.fids[folder.fid] = folder.mtime
        name = str(self.start)
        fmeta = self.logger.clog_folder.filemeta(name, no_error=True)
        trav = [FilemetaCache(fmeta, self.logger.clog_folder)]
        with fop_open(self.logger.ctx, self.fpath[1:], trav[-1], 'a') as out:
            if folder.idhash == self.logger.ctx.cidhash:
                out.write(folder.fid.encode("ascii") + b"\n")
            else:
                out.write("{} {}\n"
                          .format(folder.fid, folder.idhash).encode("ascii"))


class ChangeLogger:
    def __init__(self, ctx):
        self.ctx = ctx
        self.ctx.fs.folder_modified.subscribe(self.modified)
        self.ignore = []
        self.log = None
        self.clog_folder = None

    def setup(self):
        # devices don't need logging
        if self.ctx.cidhash == self.ctx.device.cidhash:
            return
        if self.clog_folder and not self.clog_folder.is_closed:
            raise RuntimeError("ChangeLogger was not properly shutdown")
        self.log = None
        device = self.ctx.device
        if not device or not device.cidhash:
            self.ignore = []
            return
        sn_path = self.ctx.cid.subpath("system/devices", device.cidhash)
        self.clog_path = sn_path + "/changelog"
        # retrieve or create the log folder
        clog_exists = self.ctx.fs.exists(self.clog_path)
        if clog_exists:
            if clog_exists.is_folder:
                self.clog_folder = clog_exists
            else:
                log.error("{} is not a folder, changelog disabled"
                          .format(self.clog_path))
                self.clog_folder = None
                return
        else:
            with self.ctx.groups():
                self.clog_folder = self.ctx.fs.makedirs(self.clog_path)
                self.clog_folder.notif_tag = 'ignore'
                self.clog_folder.set_modified()
        self.ignore = [self.ctx.fs.filemeta(p).fid
                       for p in (sn_path, self.clog_path)]
        self.clog_folder.no_bulk_save = True

    def shutdown(self):
        self.ignore = []
        self.clog_folder and self.clog_folder.close_folder(True)
        self.clog_folder = None

    def modified(self, folder, tag, external=False):
        if tag == 'ignore':
            return
        if external or not self.ignore or folder.fid in self.ignore:
            return
        if self.log is None:
            self.log = ChangeLog(self)
        self.log = self.log.check(folder)
