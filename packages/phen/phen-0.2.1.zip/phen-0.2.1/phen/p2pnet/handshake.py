# -*- coding:utf-8 -*-

import time
import struct

from Crypto import Random
from Crypto.Cipher import AES
from Crypto.Util import Counter

from io import BytesIO
from twisted.internet import reactor

from .protocol import rh, ldbg
from phen.event import Event
from phen.util import is_idhash


handshake_successful = Event()
ip_address_reported = Event()


@rh.request(0)
def identification(conn, data=None):
    if hasattr(conn, "id_sent"):
        # rh.ban(conn)
        conn.disconnect()
    conn.id_sent = True
    __debug__ and ldbg(conn, "id requested")
    return (rh.ctx.cidhash + " " + conn.addr.host).encode("latin1")


@rh.response(0)
def r_identification(conn, data):
    data = data.decode("latin1").split(" ")
    if len(data) != 2:
        return conn.disconnect()
    idhash, conn.reported_address = data
    # todo: check if idhash is what we expected... if not disconnect
    if not is_idhash(idhash):
        __debug__ and ldbg(conn, "invalid peer id")
        return conn.disconnect()
    conn.informed_idhash = idhash
    try:
        from phen.socnet.peer import Peer
        peer = Peer(rh.ctx, conn.informed_idhash)
        conn.pubkey = peer.get_pubkey()
    except IOError:
        conn.pubkey = None
    if conn.pubkey is not None:
        conn.sync_dev_folder = True
        rng = Random.new()
        conn.nonce = rng.read(8)
        key = rng.read(16)
        ctr = Counter.new(128)
        conn.encode_cipher = AES.new(key, AES.MODE_CTR, counter=ctr)
        return authentication.req_id, conn.nonce + conn.pubkey.encrypt(key)
    else:
        conn.sync_dev_folder = False
        return essentials.req_id, b''


@rh.request(1)
def essentials(conn, data):
    __debug__ and ldbg(conn, "essentials requested")
    io = BytesIO()
    from phen.filesystem.io import export_essentials
    if not data:
        export_essentials(rh.ctx.fs, io, rh.ctx.cidhash)
    else:
        export_essentials(rh.ctx.fs, io, str(data))
    return io.getvalue()


@rh.response(1)
def r_essentials(conn, data):
    __debug__ and ldbg(conn, "got essentials")
    io = BytesIO(data)
    from phen.filesystem.io import import_from_zipfile
    try:
        if conn.idhash is None:
            import_from_zipfile(rh.ctx.fs, io, conn.informed_idhash)
        else:
            pass
            # gotta check
            # df.callback()
            # import_from_zipfile(rh.ctx.fs, io)
    except ValueError:
        __debug__ and ldbg(conn, "invalid essentials")
        conn.disconnect()
    if conn.idhash is None:
        return r_identification(
            conn, conn.informed_idhash.encode("latin1") + b" "
        )


@rh.request(2)
def authentication(conn, data):
    __debug__ and ldbg(conn, "auth requested")
    try:
        key = rh.ctx.cid.pk.decrypt(bytes(data[8:]))
        ctr = Counter.new(128)
        conn.decode_cipher = AES.new(key, AES.MODE_CTR, counter=ctr)
    except Exception:
        __debug__ and ldbg(conn, "public key not mine")
        conn.disconnect()
    nonce = bytes(data[:8])
    return rh.ctx.cid.sign(nonce).encode("latin1")


@rh.response(2)
def r_authentication(conn, signature):
    try:
        # todo: rewrite the code bellow properly (encodings, exceptions)
        if not conn.pubkey.verify(conn.nonce, signature.decode("latin1")):
            raise Exception()
    except Exception:
        from traceback import print_exc
        print_exc()
        # ban some minutes
        # rh.ban(conn)
        __debug__ and ldbg(conn, "peer auth failed")
        conn.disconnect()
        return
    __debug__ and ldbg(conn, "peer auth ok")
    conn.idhash = conn.informed_idhash
    if conn.reported_address:
        ip_address_reported(conn.reported_address, conn.idhash)
    del conn.informed_idhash
    conn.state = 2
    if not conn.initiator:
        return identification(conn, '')  # my turn to let you know who I am
    conn.times = []
    # auth done, start pings
    return latency.req_id, struct.pack("!dd", 0.0, time.time())


@rh.request(3)
def latency(conn, peer_time):
    mine, peer = struct.unpack("!dd", peer_time)
    if mine == 0.0:
        conn.times = []
        return struct.pack("!dd", time.time(), peer)
    else:
        conn.times.append((mine, peer))
    if len(conn.times) == 7:
        process_times(conn)
        __debug__ and ldbg(conn, "peer roundtrip {}, offset {}"
                                 .format(conn.roundtrip, conn.offset))
        __debug__ and ldbg(conn, "conn state {}".format(conn.state))
        if conn.state == 2:
            handshake_successful(conn)
            conn.state = 3
            if conn.sync_dev_folder:
                reactor.callInThread(sync_dev_folder, conn)
    return struct.pack("!dd", time.time(), conn.times[-1][1])


@rh.response(3)
def r_latency(conn, peer_time):
    mine, peer = struct.unpack("!dd", peer_time)
    conn.times.append((mine, peer))
    if len(conn.times) < 8:
        return 3, struct.pack("!dd", conn.times[-1][1], time.time())
    process_times(conn)
    __debug__ and ldbg(conn, "peer roundtrip {}, offset {}"
                             .format(conn.roundtrip, conn.offset))
    __debug__ and ldbg(conn, "conn state {}".format(conn.state))
    if conn.state == 2:
        handshake_successful(conn)
        conn.state = 3
        if conn.sync_dev_folder:
            reactor.callInThread(sync_dev_folder, conn)


def process_times(conn):
    """Calculate latency and time difference."""
    diff = [
        (t1[0] - t0[0], t1[1] - t0[1])
        for t0, t1 in zip(conn.times[:-1], conn.times[1:])
    ]
    delays = [sum(d[i] for d in diff) / len(diff) for i in (0, 1)]
    conn.roundtrip = sum(delays) / 2
    conn.offset = conn.times[0][1] - conn.times[0][0] - conn.roundtrip / 2


def sync_dev_folder(conn):
    from .synchronizer import SyncFromDevice
    sfn = SyncFromDevice(conn, rh.ctx.fs)
    sfn.sync_folder(conn.idhash, "root")
    ldbg(conn, "peer's device folder synced")
