#!/usr/bin/env python
#-*- coding:utf-8 -*-

"""
    Client/Server Control of the Folder Access Semaphore
"""

import logging
from collections import deque

from twisted.internet import reactor, defer
from twisted.protocols.basic import LineReceiver
from twisted.internet.protocol import Factory, ClientFactory

from .accsem import ClientBase, fidf


log = logging.getLogger(__name__)

# note: all references to `fid` bellow actually mean idhash + fid
FIDSIZE = 43 * 2


# -=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=:[ server side

class NetClientHandler(LineReceiver, ClientBase):
    def __init__(self, accsem, addr):
        ClientBase.__init__(self, accsem)
        self.addr = addr

    def connectionMade(self):
        #log.debug("[server] new tcp connection from " + self.addr.host)
        self.sendLine(b'phen')

    def connectionLost(self, reason):
        #log.debug("[server] disconnected from " + self.addr.host)
        self.accsem.clear_locks(self)
        #__debug__ and log.debug(reason)

    def lineReceived(self, line):
#        print ">srv", line
        if not line:
            return True  # disconnect
        line = line.decode("ascii")

        cmd, fid, oid = line[0], line[1:1 + FIDSIZE], line[1 + FIDSIZE:]

        # subscribe to change notifications
        if cmd == 's':
            self.accsem.subscribe(fid, (self, oid))
        # unsubscribe
        elif cmd == 'U':
            self.accsem.unsubscribe(fid, (self, oid))
        # lock
        elif cmd == 'l':
            self.accsem.lock(fid, (self, oid))
        # partial lock - interruptible
        elif cmd == 'i':
            self.accsem.partial_lock(fid, (self, oid))
        # unlock
        elif cmd == 'u':
            mtime, oid = oid.split()
            if mtime != '-':
                mtime = float(mtime)
            self.accsem.unlock(fid, mtime, (self, oid))
        # wrong command, disconnect
        else:
            return True

    def send(self, params):
        reactor.callFromThread(self.sendLine, "".join(params).encode("ascii"))
#        print "srv>", params

    def folder_changed(self, oid, fid, mtime):
        """
            folder changed
        """
        self.send(('n', fid, repr(mtime), " ", oid))

    def lock_granted(self, oid, fid, inc=True):
        """
            lock granted
        """
        if inc:
            self.fids[fid] += 1
        self.send(('l', fid, oid))

    def flush_requested(self, oid, fid):
        """
            flush requested
        """
        self.send(('f', fid, oid))


class NetAccessServer(Factory):
    def __init__(self, accsem):
        import weakref
        self.accsem = accsem
        self.clients = weakref.WeakSet()

    def buildProtocol(self, addr):
        retv = NetClientHandler(self.accsem, addr)
        self.clients.add(retv)
        return retv

    def shutdown(self):
        self.listener.stopListening()
        for client in self.clients:
            reactor.callFromThread(client.transport.loseConnection)

    @staticmethod
    def setup(accsem, host, port):
        retv = NetAccessServer(accsem)
        retv.listener = reactor.listenTCP(port, retv, interface=host)
        return retv


# -=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=:[ client side

class NetClient(LineReceiver):
    def __init__(self, store, addr, connected_df):
        self.store = store
        self.addr = addr
        self.df = connected_df
        self.state = 0
        self.deferred_locks = {}

    def connectionMade(self):
        #log.debug("[client] new tcp connection from " + self.addr.host)
        self.df.callback(self)
        del self.df

    def connectionLost(self, reason):
        #log.debug("[client] disconnected from " + self.addr.host)
        #log.debug(reason)
        self.store.access_semaphore_down()

    def send(self, line):
#        print "cli>", line
        if isinstance(line, tuple):
            line = "".join(line)
        # we assume the reactor thread is not the current one
        # todo: test if it works with a single thread
        reactor.callFromThread(self.sendLine, line.encode("ascii"))

    def lineReceived(self, line):
#        print ">cli", line
        if not self.state:
            if line != b'phen':  # magic id
                return self.transport.loseConnection()
            self.state = 1
            return
        if not line:
            return self.transport.loseConnection()
        line = line.decode("ascii")

        cmd, fid, oid = line[0], line[1:1 + FIDSIZE], line[1 + FIDSIZE:]

        # notification
        if cmd == 'n':
            mtime, oid = oid.split()
            self.store.folder_changed(int(oid), fid, float(mtime))
        # lock granted
        elif cmd == 'l':
            if (oid, fid) not in self.deferred_locks:
                log.error("unrequested grant received to lock " + fidf(fid))
                return
            df = self.deferred_locks[(oid, fid)].popleft()
            df.callback((oid, fid))
        # flush request
        elif cmd == 'f':
            self.store.flush_requested(int(oid), fid)
        # wrong command
        else:
            self.transport.loseConnection()

    def subscribe(self, fid, oid):
        self.send(('s', fid, str(oid)))

    def unsubscribe(self, fid, oid):
        self.send(('U', fid, str(oid)))

    def lock(self, fid, interruptible, oid):
        self.send((('i' if interruptible else 'l'), fid, str(oid)))
        if interruptible:
            return
        df = defer.Deferred()
        self.deferred_locks.setdefault((str(oid), fid), deque()).append(df)
        return df

    def unlock(self, fid, mtime, oid):
        if mtime != '-':
            mtime = repr(mtime)
        self.send(("u", fid, mtime, ' ', str(oid)))

    @staticmethod
    def connect(store, host, port):
        log.debug("connecting to access semaphore @ {}:{}".format(host, port))
        factory = NetClientFactory(store)
        reactor.connectTCP(host, port, factory)
        return factory.df


class NetClientFactory(ClientFactory):
    def __init__(self, store):
        self.df = defer.Deferred()
        self.store = store

    def buildProtocol(self, addr):
        return NetClient(self.store, addr, self.df)

    def clientConnectionFailed(self, connector, reason):
        log.error("couldn't connect to {0.host}:{0.port} (tcp)"
                  .format(connector.getDestination()))
        self.df.callback(None)
