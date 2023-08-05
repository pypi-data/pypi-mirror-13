# -*- coding:utf-8 -*-

import logging

from twisted.internet import reactor, defer
from twisted.internet.protocol import ClientFactory

from .protocol import TCPRequest


log = logging.getLogger(__name__)


class ConnectionMethod:
    def __init__(self, path, name, **kw):
        self.path = path
        self.name = name
        self.method = kw.pop("method", "inet")
        self.proto = kw.pop("proto", "tcp")
        self.host = kw.pop("host", None)
        self.port = kw.pop("port", None)
        if kw:
            log.warn("connection '{}/{}' has unknown parameters '{}'"
                     .format(path, name, repr(kw)))

    @staticmethod
    def from_file(ctx, path, name):
        filepath = ctx.fs.subpath(path, name)
        try:
            return ConnectionMethod(path, name, **ctx.fs.json_read(filepath))
        except Exception:
            log.exception("couldn't read connection config: " + filepath)

    @staticmethod
    def from_device(ctx, devhash):
        """
            Return all connection methods of a device identity
        """
        retv = []
        dirpath = u"/" + devhash
        if not ctx.fs.exists(dirpath):
            return retv
        for fname in ctx.fs.listdir(dirpath):
            if not fname.endswith(".connection"):
                continue
            cm = ConnectionMethod.from_file(ctx, dirpath, fname)
            if cm is None:
                continue
            if cm.method != "inet":
                log.warn("unknown connection method {} ignored in {}"
                         .format(cm.method, fname))
                continue
            retv.append(cm)
        return retv


class TCPReqCliFactory(ClientFactory):
    def __init__(self):
        self.df = defer.Deferred()

    def buildProtocol(self, addr):
        return TCPRequest(addr, True)

    def clientConnectionFailed(self, connector, reason):
        log.info("couldn't connect to {0.host}:{0.port} (tcp)"
                 .format(connector.getDestination()))
        self.df.callback(self)


def connect_to_address(addr, port):
    log.info("directly connecting to {}:{} (tcp)".format(addr, port))
    import phen
    import threading
    factory = TCPReqCliFactory()
    if threading.current_thread() == phen.reactor_thread:
        reactor.connectTCP(addr, port, factory)
    else:
        reactor.callFromThread(reactor.connectTCP, addr, port, factory)


class Connections:
    """Collection of connections to a device."""

    def __init__(self, ctx, did, keep_around=False):
        self.did = did
        self.conn_list = []
        self.keep_around = keep_around
        self.reload_methods(ctx)
        self.req_cnt = 0

    def reload_methods(self, ctx):
        if ctx is None:
            from phen.context import device as ctx
        self.methods = ConnectionMethod.from_device(ctx, self.did)

    def new_connection(self, conn):
        self.conn_list.append((conn.roundtrip, conn))
        if len(self.conn_list) > 1:
            previously_grabbed = self.conn
            self.conn_list.sort()
            self.conn.grab(self.req_cnt)
            previously_grabbed.release(self.req_cnt)
        self.grab()
        reactor.callLater(60, self.release)  # keep alive for at least 1 min

    def connection_closed(self, conn):
        if len(self.conn_list) == 1:
            self.conn_list = []
            if self.keep_around:
                self.schedule_connection()
            return not self.keep_around
        self.conn_list = [(r, c) for r, c in self.conn_list if c != conn]

    def schedule_connection(self, *p):
        reactor.callLater(60, self.connect)
        # reactor.callLater(conf.period + random, self.connect)

    def grab(self):
        if not self.conn_list:
            log.warn("trying to grab device with no connection: {}"
                     .format(self.did))
        else:
            self.req_cnt += 1
            self.conn.grab()

    def release(self):
        if not self.req_cnt:
            log.warn("mismatch in release of device connection: {}"
                     .format(self.did))
        elif self.conn:
            self.req_cnt -= 1
            self.conn.release()

    @property
    def conn(self):
        return self.conn_list and self.conn_list[0][1]

    def do_connect(self, methods, df):
        if not methods:
            df.callback(self)
            return
        conndef = methods[0]
        addr = conndef.host
        port = conndef.port
        if addr and port:
            log.info("connecting to {}:{} (tcp)".format(addr, port))
            factory = TCPReqCliFactory()
            factory.df.addCallback(lambda e: self.do_connect(methods[1:], df))
            reactor.connectTCP(addr, port, factory)

    def connect(self):
        if self.conn_list:
            return None
        df = defer.Deferred()
        self.do_connect(self.methods, df)
        return df
