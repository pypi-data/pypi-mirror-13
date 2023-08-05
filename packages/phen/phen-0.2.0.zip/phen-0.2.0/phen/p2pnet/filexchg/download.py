# -*- coding:utf-8 -*-

import six
import logging
from twisted.internet import reactor

from .common import rh, block_size, file_request, block_request
from ..idrouter import idrouter, Routes
from phen.storage import store
from phen.util import fid2name


log = logging.getLogger(__name__)


def ldbg(conn, msg):
    """Log a debug message identifying the connection."""
    log.debug("[{}] {}".format(conn.idhash[:5], msg))


class BlockDownloader:
    def __init__(self, download, conn):
        conn.grab()
        self.download = download
        self.conn = conn
        self.did = download_mgr.new_did(self, conn)
        self.blk_id = None
        self.size = None
        self.state = 0
        self.out = store.store(self.download.fid_pair, mode='r+b')

    def release(self):
        if self.state < 0:
            return
        self.state = -1
        download_mgr.remove_did(self, self.conn)
        self.conn.release()
        self.out.close()

    def request_file(self):
        # todo: keep a list of recently referred idhashes (per connection)
        # to shorten the payload
        self.state = 1
        mtime = self.download.mtime and repr(self.download.mtime)
        fid_pair = self.download.dl_fid_pair
        payload = " ".join(
            [self.did, fid_pair[0], fid_pair[1], mtime or '-']
        ).encode("latin1")
        ldbg(self.conn, "requesting file " + fid2name(fid_pair))
        rh.send(self.conn, file_request.req_id, payload)

    def r_file_request(self, data):
        data = data.split(b" ")
        if not len(data) or data[0] not in (b"200", b"304", b"404"):
            ldbg(self.conn, "malformed response for file request")
            return
        if data[0] == b"200":
            self.download.ready(self, data[1:])
        else:
            self.release()
            self.download.not_ready(self, data[0])

    def request_block(self, blk_id, size=None):
        self.blk_id = blk_id
        self.size = size or block_size
        ldbg(self.conn, "{}: req block {}/{}, size {}".format(ord(self.did),
             self.blk_id + 1, self.download.last_block + 1, self.size))
        payload = " ".join([self.did, str(blk_id)]).encode("latin1")
        rh.send(self.conn, block_request.req_id, payload)

    def r_block_request(self, data):
        try:
            r_blk_id = int(data)
        except ValueError:
            ldbg(self.conn, "malformed response for file request")
            return
        ldbg(
            self.conn, "r_block_request {} == {}?"
            .format(r_blk_id, self.blk_id)
        )
        if r_blk_id != self.blk_id:
            self.download.block_unavailable(self, r_blk_id)
        else:
            self.state = 2
            self.out.seek(self.blk_id * block_size)

    def r_block_data(self, data):
        if self.state != 2:
            ldbg(
                self.conn,
                "received unexpected block data, state={} size={}"
                .format(self.state, len(data))
            )
            return
        if len(data) > self.size:
            ldbg(self.conn, "received block data of unexpected size")
            return
        self.size -= len(data)
        self.out.write(data)
        if not self.size:
            self.state = 1
            self.out.flush()
            self.download.block_completed(self)


class DownloadInitFailure(RuntimeError):
    """Could not negotiate the download"""


class Download:
    def __init__(self, fid_pair, deferred, **kw):
        self.expecting_route = []
        if "timeout" in kw:
            reactor.callLater(kw["timeout"], self.timeout)
        self.size = kw.get('size', None)
        self.deferred = [deferred]
        self.block_downloaders = []
        self.dl_fid_pair = fid_pair
        self._define_destination(fid_pair, kw)
        self._setup_destination_blocks()
        self._setup_sources(kw)
        # if this is a folder request, must get it from a single source
        self.request_next(self.is_folder)

    def _define_destination(self, fid_pair, kw):
        self.is_folder = kw.get('folder', False)
        if self.is_folder:
            self.mtime = rh.ctx.fs.open_folder(fid_pair, None, None).mtime
            from phen.util import hex_suffix
            self.fid_pair = fid_pair[0], hex_suffix(fid_pair[1])
        else:
            self.fid_pair = fid_pair
            self.mtime = None

    def _setup_destination_blocks(self):
        if not store.is_available(self.fid_pair, True):
            store.store(self.fid_pair).close()  # create it empty
            self.blocks = store.open_blocks(self.fid_pair, 'w+b')
            self.next_block = None
            self.remaining = None
            self.last_block = None
        else:
            self.blocks = store.open_blocks(self.fid_pair, restart=True)
            if self.blocks == 'done':
                log.warn("expected existing blocks file, but it was not found")
                raise DownloadInitFailure
            start_block = self.blocks.get_next(blk_type=b'0')
            self.next_block = max(start_block, 0)
            self.remaining, self.last_block = self.blocks.remaining()
        self.last_size = None

    def _setup_sources(self, kw):
        sources = [self.fid_pair[0]] if "sources" not in kw else kw["sources"]
        for source in sources:
            if isinstance(source, six.string_types):
                route = idrouter.request_route(source, 1)
                route.subscribe(self.route_available, None)
                self.expecting_route.append(route)
            elif isinstance(source, Routes):
                for conns in source.connections:
                    for conn in conns.conn_list:
                        bdl = BlockDownloader(self, conn[1])
                        self.block_downloaders.append(bdl)
            else:
                self.block_downloaders.append(BlockDownloader(self, source))

    def request_next(self, one=True):
        """
            Start downloading from one or all available sources.
        """
        for bdl in self.block_downloaders:
            if not bdl.state:
                bdl.request_file()
                if one:
                    return True

    def route_available(self, route, conn):
        """
            Setup a new BlockDownloader for the newly opened route.
        """
        if route in self.expecting_route:
            route.unsubscribe(self.route_available, None)
            self.expecting_route.remove(route)
        self.block_downloaders.append(BlockDownloader(self, conn.conn))
        self.request_next()

    def timeout(self):
        """
            Cancel the download due to the timeout.
        """
        self.shutdown()
        log.debug("timeout downloading " + fid2name(self.dl_fid_pair))
        for df in self.deferred:
            if not df.called:
                df.callback((self, None, True))

    def not_ready(self, bdl, code):
        """
            Process a negative peer response.
        """
        if code == b"304":
            if not self.is_folder:
                ldbg(bdl.conn, "'unmodified' response for non folder request")
            if not self.request_next(True) and not self.expecting_route:
                self.shutdown()
                # no other source available
                for df in self.deferred:
                    df.callback((self, None, False))
        else:
            if not self.request_next(True) and not self.expecting_route:
                self.shutdown()
                ldbg(bdl.conn, "requested file not found in any source")
                for df in self.deferred:
                    df.callback((self, None, True))

    def _check_data(self, bdl, data):
        self.remote_mtime = data[1] != b'-' and float(data[1])
        if data[0] != '-':
            if self.size is None:
                # if size is None that means we're retrieving a folder
                # so it is reasonable to accept this as true
                self.size = int(data[0])
            elif self.size != int(data[0]):
                # note: size will be a multiple of 16 due to encryption padding
                ldbg(bdl.conn, "unexpected file size announced")
                bdl.release()
                self.request_next()
                return False
        if not self.size:
            ldbg(bdl.conn, "folder requested, but peer has incomplete data")
            for df in self.deferred:
                df.callback((self, None, True))
            return False
        else:
            ldbg(bdl.conn, "{}: {} bytes to be transferred"
                 .format(ord(bdl.did), self.size))
        return True

    def ready(self, bdl, data):
        """
            Start downloading blocks from the available peer.
        """
        if not self._check_data(bdl, data):
            return
        if self.last_block is None:
            self.last_block = float(self.size) / block_size
            if int(self.last_block) == self.last_block:
                self.last_size = block_size
                self.last_block -= 1
            self.next_block = 0
            self.last_block = int(self.last_block)
            self.remaining = self.blocks.adjust(self.last_block + 1)
        if self.last_block < 0:
            self.last_block = 0
            self.remaining = 1
        if self.last_size is None:
            self.last_size = self.size % block_size
        self.alloc_block(bdl)

    def alloc_block(self, bdl):
        """
            Request a block from a peer, marking it for exclusive access.
        """
        if self.next_block > self.last_block:
            ldbg(bdl.conn, "tried to allocate block past last {}: next {}"
                           .format(self.last_block, self.next_block))
            return
        size = None if self.next_block != self.last_block else self.last_size
        bdl.request_block(self.next_block, size)
        self.next_block = self.blocks.alloc(self.next_block)

    def block_unavailable(self, bdl, blk_id):
        """
            Deal with the response of an unavailable block.
        """
        self.blocks.mark(self.bdl.blk_id, b'0')
        # if the next block is ahead of the one that just
        # failed, rewind to it
        if self.next_block > self.bdl.blk_id:
            self.next_block = self.bdl.blk_id
        # try to alloc the block that the peer has
        t_blk_id = self.blocks.alloc(blk_id, check_first=True)
        if t_blk_id is not None:
            size = None if blk_id != self.last_block else self.last_size
            bdl.request_block(blk_id, size)
        else:
            # wait a bit hoping the peer will retrieve more data
            reactor.callLater(30, lambda: self.alloc_block(bdl))

    def block_completed(self, bdl):
        """
            Request a new block, or shutdown if it was the last one.
        """
        if not self.remaining:
            raise ValueError("unexpected block completed")
        self.blocks.mark(bdl.blk_id, b'1')
        self.remaining -= 1
        if not self.remaining:
            self.shutdown(True)
            for df in self.deferred:
                df.callback((self, self.fid_pair, self.remote_mtime))
            return
        self.alloc_block(bdl)

    def shutdown(self, remove_blocks=False):
        """
            Clean up the download.
        """
        download_mgr.remove(self.dl_fid_pair)
        for route in self.expecting_route:
            route.unsubscribe(self.route_available, None)
        self.expecting_route = []
        for bdl in self.block_downloaders:
            bdl.release()
        self.block_downloaders = []
        store.close_blocks(self.fid_pair, remove_blocks)


class DownloadManager:
    def __init__(self):
        self.downloads = {}
        self.by_fid_pair = {}

    def already_requested(self, pair):
        return pair in self.by_fid_pair

    def remove(self, pair):
        if not self.already_requested(pair):
            log.error("trying to remove inexistent download " + fid2name(pair))
            return
        self.by_fid_pair.pop(pair)

    def new_did(self, blk_dl, conn):
        did = (getattr(conn, "download_id", -1) + 1) & 0xff
        if did == 32:  # skip space, the field separator
            did += 1
        conn.download_id = did
        self.downloads[conn.idhash + chr(did)] = blk_dl
        return chr(did)

    def remove_did(self, blk_dl, conn):
        did_full = conn.idhash + blk_dl.did
        assert did_full in self.downloads
        self.downloads.pop(did_full)

    def _check_reponse(self, conn, data, reqt, skip=2):
        full_id = conn.idhash + data[:1].decode("latin1")
        if not data or full_id not in self.downloads:
            ldbg(
                conn, "received response for "
                "unsent {} request: {}".format(reqt, data)
            )
            print(self.downloads)
            return None, None
        return full_id, data[skip:]

    def r_file_request(self, conn, data):
        full_id, data = self._check_reponse(conn, data, "file")
        if full_id is not None:
            self.downloads[full_id].r_file_request(data)

    def r_block_request(self, conn, data):
        full_id, data = self._check_reponse(conn, data, "block")
        if full_id is not None:
            self.downloads[full_id].r_block_request(data)

    def r_block_data(self, conn, data):
        full_id, data = self._check_reponse(conn, data, "block data", 1)
        if full_id is not None:
            self.downloads[full_id].r_block_data(data)


download_mgr = DownloadManager()
