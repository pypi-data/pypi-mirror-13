# -*- coding:utf-8 -*-

import logging

from twisted.internet.protocol import Protocol
from twisted.internet import reactor

from phen.event import Event


log = logging.getLogger(__name__)
disconnected = Event()


VERSION = b'\0'


def shid(obj):
    return repr(obj)[-4:]


def ldbg(conn, msg):
    """Log a debug message identifying the connection."""
    cid = conn.idhash[:5] if conn.idhash else repr(conn)[-9:-2]
    log.debug("[{}] {}".format(cid, msg))


def from_int(num):
    buff = bytearray(b'' if num else b'\0')
    while num:
        buff.append((0x80 | num & 0xff) if num & ~0x7f else num)
        num >>= 7
    return buff


def to_int(buff):
    idx = 0
    num = buff[idx] & 0x7f
    while buff[idx] & 0x80 and idx < len(buff) - 1:
        idx += 1
        num |= (buff[idx] & 0x7f) << (idx * 7)
    num |= (buff[idx] & 0x80) << (idx * 7)
    return num, idx + 1


class TCPRequest(Protocol):
    def __init__(self, addr, initiator=False):
        self.addr = addr
        self.initiator = initiator
        self.idhash = None
        self.encode_cipher = self.decode_cipher = None
        self.in_use = 0
        self.peer_using = True

    def grab(self, count=1):
        warn = count > 0 and not self.in_use
        self.in_use += count
        if warn == 1:
            rh.send(self, in_use.req_id, b"1")

    def release(self, count=1):
        self.in_use -= min(count, self.in_use)
        if not self.in_use:
            if not self.peer_using:
                self.disconnect()
            rh.send(self, in_use.req_id, b"0")

    def connectionMade(self):
        log.info("new tcp connection from " + self.addr.host)
        self.transport.write(b'phen' + VERSION)
        self.state = 0
        self.size = 0
        self.buffer = bytearray()
        self.dataReceived = self._handshake_received

    def _handshake_received(self, data):
        if data[:4] != b'phen':  # magic number / id
            self.transport.loseConnection()
        else:
            self.version = min(ord(VERSION), data[4])
            if self.initiator:
                rh.handshake(self)
        self.state = 1
        self.dataReceived = self._data_received
        self._data_received(data[5:])

    def _data_received(self, data):
        self.buffer += bytearray(data)
        while len(self.buffer) > self.size:
            if not self._process_buffer():
                break
            self.buffer = self.buffer[self.size:]
            self.size = 0

    def _process_buffer(self):
        if not self.size:
            # 14 bits max = 16K - 1
            self.size, off = to_int(self.buffer[:2])
            if not self.size:
                __debug__ and ldbg(self, "empty packet")
                self.transport.loseConnection()
                return False
            self.buffer = self.buffer[off:]
        if self.size <= len(self.buffer):
            data = self.buffer[:self.size]
            if self.decode_cipher is not None:
                data = bytearray(self.decode_cipher.decrypt(bytes(data)))
            rh.handle(self, data)
            return True
        return False

    def sendData(self, data):
        if __debug__:
            import phen
            import threading
            if threading.current_thread() != phen.reactor_thread:
                raise SystemError("trying to send data from a thread")
        if self.state > 1 and self.encode_cipher is not None:
            data = self.encode_cipher.encrypt(bytes(data))
        size = len(data)
        if size > (1 << 14) - 1:
            log.error("packet size larger than maximum permitted, dropped")
        else:
            self.transport.write(bytes(from_int(size)) + bytes(data))

    def disconnect(self):
        self.transport.loseConnection()

    def connectionLost(self, reason):
        disconnected(self)
        log.info("disconnected from " + self.addr.host)
        __debug__ and log.debug(reason)


class RequestHandler:
    _requests = {}
    _responses = {}

    def handle(self, conn, data):
        req_type = data[0] & 0x7f
        restricted = conn.state < 2  # before handshake
        # during handshake only handshake requests are allowed (3=latency)
        if req_type not in self._requests or (restricted and req_type > 3):
            return conn.transport.loseConnection()
        is_response = bool(data[0] & 0x80)
        if is_response:
            handler = RequestHandler._responses[req_type]
        else:
            handler = RequestHandler._requests[req_type]
        if handler:
            handler(conn, data[1:])

    def send(self, conn, req_id, data, resp=False):
        assert isinstance(data, bytes)
        reactor.callFromThread(
            conn.sendData,
            bytearray([(0x80 if resp else 0) | req_id]) + data
        )

    def request(self, req_id):
        def req_decorator(func):
            def decorated(conn, data):
                retv = func(conn, data)
                if retv is None:
                    return
                # send response
                rh.send(conn, req_id, retv, resp=True)
            RequestHandler._requests[req_id] = decorated
            decorated.req_id = req_id
            return decorated
        return req_decorator

    def response(self, req_id):
        def resp_decorator(func):
            def decorated(conn, data):
                retv = func(conn, data)
                if retv is None:
                    return
                # send new request
                req_id, data = retv
                rh.send(conn, req_id, data)
            RequestHandler._responses[req_id] = decorated
            decorated.req_id = req_id
            return decorated
        return resp_decorator

    def handshake(self, conn):
        RequestHandler._requests[0](conn, '')


rh = RequestHandler()


@rh.request(0x7f)
def in_use(conn, data):
    if data == b"0":
        conn.peer_using = False
        if not conn.in_use:
            ldbg(conn, "connection not in use, disconnecting")
            conn.disconnect()
    else:
        conn.peer_using = True
