# -*- coding:utf-8 -*-

import logging
from twisted.internet import reactor

from .common import rh, block_size, block_data
from phen.storage import store
from phen.util import fid2name


log = logging.getLogger(__name__)


def ldbg(conn, msg):
    """Log a debug message identifying the connection."""
    log.debug("[{}] {}".format(conn.idhash[:5], msg))


class BlockUploader:
    packet_size = (1 << 14) - 3

    def __init__(self, uid, conn, fid_pair):
        self.uid = uid
        self.conn = conn
        self.infile = store.load(fid_pair)
        self.partial = store.is_available(fid_pair, True) == 'partial'
        self.fid_pair = fid_pair
        self.remaining = 0
        if self.partial:
            store.open_blocks(fid_pair)

    def block_request(self, blk_id):
        # log.info("block_req {} {}".format(self.fid_pair, blk_id))
        if self.partial:
            t_blk_id = store.get_next_block(self.fid_pair, blk_id)
            if t_blk_id != blk_id:
                return t_blk_id
        pos = blk_id * block_size
        self.infile.seek(pos)
        if pos == self.infile.tell():
            self.remaining = block_size
            reactor.callInThread(self.send_block_data)
            return blk_id
        return -1

    def send_block_data(self):
        if not self.remaining:
            return
        to_send = min(self.remaining, self.packet_size)
        data = self.infile.read(to_send)
        # log.info("send data " + str(len(data)))
        rh.send(self.conn, block_data.req_id, self.uid.encode("latin1") + data)
        self.remaining -= len(data)
        if self.remaining and len(data) == to_send:
            reactor.callLater(0, self.send_block_data)


class UploadManager:
    def __init__(self):
        self.uploads = {}

    def setup(self, conn, uid, fid_pair):
        self.uploads[conn.idhash + uid] = BlockUploader(uid, conn, fid_pair)

    def file_request(self, conn, data):
        try:
            did, idhash, fid, mtime = data.decode("latin1").split(" ")
        except ValueError:
            ldbg(conn, "malformed file request received")
            return
        fid_pair = idhash, fid
        available = store.is_available(fid_pair, True)
        if not available:
            ldbg(conn, "requested '{}' not found".format(fid2name(fid_pair)))
            return " ".join([did, "404"]).encode("latin1")
        if available == 'partial':
            size = "-"
        else:
            size = str(store.size(fid_pair))
        if mtime != "-":
            try:
                folder = rh.ctx.fs.open_folder(fid_pair, None, None)
                local_mtime = repr(folder.mtime)
            except IOError:
                local_mtime = "-"
            if mtime == local_mtime:
                ldbg(conn, "peer requested '{}', but not modified"
                           .format(fid2name(fid_pair)))
                return " ".join([did, "304"]).encode("latin1")
        else:
            local_mtime = "-"
        ldbg(conn, "serving '{}'".format(fid2name(fid_pair)))
        self.setup(conn, did, fid_pair)
        return " ".join([did, "200", size, local_mtime]).encode("latin1")

    def block_request(self, conn, data):
        try:
            uid, blk_id = data.decode("latin1").split(" ")
        except ValueError:
            ldbg(conn, "malformed block request received")
            return
        if (conn.idhash + uid) not in self.uploads:
            ldbg(conn, "received response for unsent block request")
        else:
            try:
                blk_id = int(blk_id)
            except ValueError:
                ldbg(conn, "invalid block request")
                return
            retv = self.uploads[conn.idhash + uid].block_request(blk_id)
            return " ".join([uid, str(retv)]).encode("latin1")


upload_mgr = UploadManager()
