# -*- coding:utf-8 -*-

import logging
from twisted.internet import reactor, threads

from phen.util import fid2name
from phen.filesystem.synchronizer import SyncBase

from .idrouter import idrouter
from .protocol import rh


log = logging.getLogger(__name__)


# @rh.request(7)
# def notify_request(conn, data):
#    idhash, fid = data.split()


@rh.request(8)
def push_request(conn, data):
    try:
        idhash, fid, rmtime = tuple(str(data).split())
        mtime = None if rmtime == '-' else float(rmtime)
    except TypeError:
        return
    fid_pair = idhash, fid
    log.info("received push request: {} {}".format(fid2name(fid_pair), rmtime))
    try:
        if rh.ctx.fs.store.is_available(fid_pair):
            folder = rh.ctx.fs.open_folder(fid_pair)
        else:
            folder = None
    except IOError:
        log.error("push request of non-folder " + fid2name(fid_pair))
        return
    if folder and folder.mtime == mtime:
        log.debug("modification time match, request ignored")
        return
    # todo: rewrite the following
    # # if containing folder belongs to a serviced identity, try to sync it
    # ctx = ctxmgr.service_contexts.get(idhash, None)
    # if not ctx:
    #     # not in the loaded identities, let's try known devices
    #     for ctx in ctxmgr.service_contexts.values():
    #         if ctx.cid.last_sync(conn.idhash):  # peer is a device
    #             break
    #     else:
    #         log.error("push request by peer not known to be a device")
    #         return
    # log.debug("accepted push request")
    # sync_from_device = SyncFromDevice(conn, ctx.fs)
    # reactor.callInThread(sync_from_device.sync_folder, idhash, fid)


def notify_change(conn, fid_pair, mtime='-'):
    if not conn:
        return
    payload = " ".join(fid_pair + (mtime,))
    log.info("sending push request: {} {}".format(fid2name(fid_pair), mtime))
    reactor.callLater(0, rh.send, conn, push_request.req_id, str(payload))


class SyncFromDevice(SyncBase):
    def __init__(self, conn, fs, dev_folder_fidpair=None):
        SyncBase.__init__(self, fs)
        self.conn = conn
        self.ignore_dev_folder = dev_folder_fidpair

    def retrieve(self):
        from .requests import download
        dl_fid_pair, mtime = None, None
        while True:
            fid_pair, folder = yield dl_fid_pair, mtime
            log.info("retrieving " + fid2name(fid_pair))
            if fid_pair == self.ignore_dev_folder:
                dl_fid_pair = None
                mtime = False
                log.info(fid2name(fid_pair) + " already updated")
                continue
            dl, dl_fid_pair, mtime = threads.blockingCallFromThread(
                reactor, download,
                fid_pair, folder=folder, sources=[self.conn],
            )
            if not dl_fid_pair and mtime:
                log.warn(fid2name(fid_pair) + " download failed")
            if mtime is False:
                log.info(fid2name(fid_pair) + " is up-to-date")
            elif dl_fid_pair:
                log.info(fid2name(fid_pair) + " download succeeded")


class Synchronizer:
    def __init__(self, sync_period=60):
        # self.active = [] # weakrefs
        self.sync_period = sync_period
        self.df_sync = None
        # self.sync_now()
        self.setup_idsync()

    def service_context_added(self, ctx):
        ctx.route = idrouter.request_route(ctx.cidhash, 1)
        ctx.route.subscribe(self.sync_identity, None)

    def setup_idsync(self):
        """for ctx in ctxmgr.service_contexts.values():
            self.service_context_added(ctx)"""

    def sync_identity(self, route, conn):
        return
        # todo:
        # fidpair = self.introduce_to_device(route, conn)
        # ctx = ctxmgr.service_contexts[route.idhash]
        # sync_from_device = SyncFromDevice(conn.conn, ctx.fs, fidpair)
        # reactor.callInThread(sync_from_device.sync, conn.conn.idhash)
        # buffer_changes = {}
        #
        # def notify_from_buffer():
        #     # we could limit the number of notifications per second
        #     while buffer_changes:
        #         fid_pair, time = buffer_changes.popitem()
        #         notify_change(conn.conn, fid_pair, time)
        #
        # def instant_change_notif(folder, tag, external):
        #     if tag != 'ignore':
        #         time = repr(folder.store_mtime if external else folder.mtime)
        #         if not buffer_changes:
        #             reactor.callFromThread(reactor.callLater, 1,
        #                                    notify_from_buffer)
        #         buffer_changes[folder.fid_pair] = time
        #
        # ctx.fs.folder_modified.subscribe(instant_change_notif)
        # # df = threads.deferToThread(sync_from_device.sync, conn.conn.idhash)
        # # df.addCallback(lambda: )
        # # todo: add to self.active

    def introduce_to_device(self, route, conn):
        return
        # todo:
        # log.info("introducing myself to the fellow device")
        # ctx = ctxmgr.service_contexts[route.idhash]
        # fid = ctx.fs.filemeta("system/devices").fid
        # fid_pair = route.idhash, fid
        # notify_change(conn.conn, fid_pair)
        # return fid_pair

    def sync_contact(self, route, conn):
        #    Subscriptions
        #        SyncContact(route, conn)
        pass

    def schedule_sync(self):
        self.df_sync = reactor.callLater(self.sync_period, self.sync)

    def sync_now(self):
        if self.df_sync:
            self.df_sync.cancel()
            self.df_sync = None
        self.sync()

    def sync(self):
        self.schedule_sync()
