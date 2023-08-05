# -*- coding:utf-8 -*-

import logging

from .connection import Connections
from .requests import handshake_successful, disconnected
from phen.event import Event
from phen.util import is_idhash
from phen.context import Context, device


log = logging.getLogger(__name__)


class Routes:
    """Manager of connections to devices of an identity."""

    def __init__(self, idhash):
        self.idhash = idhash
        self.ctx = Context.clone_identity_context(idhash) or device
        # if we have a loaded identity, try to connect to all its devices
        self.keep_all_up = self.ctx.cidhash == idhash
        self.connections = {}
        self.indirect = []
        self.load_contact_info()
        log.info("new route to {} with devices {}"
                 .format(self.idhash, self.devhashes))
        self.alt_route_available = Event()
        self.route_available = Event()
        self.route_closed = Event()
        # priority requesters count
        self.req_low = 0
        self.req_high = 0

    def load_contact_info(self):
        try:
            path = self.ctx.fs.subpath(self.idhash, u"system/devices")
            files = self.ctx.fs.listdir(path)
            if not files:
                raise IOError  # assume the identity is from a device
        except IOError:
            # probably trying to route directly to a device
            self.devhashes = set([self.idhash])
            return
        # consider any file that looks like an idhash as a contact device
        self.devhashes = set(
            did for did in files
            if is_idhash(did) and did != device.cidhash  # except ourselves
        )
        # then read all `.idlist` files as idhash lists
        for fname in files:
            if fname.endswith(".idlist"):
                with self.ctx.fs.open(fname) as lstf:
                    self.devhashes.update(lstf.read().split())

    def subscribe(self, conn_cback, alt_cback=False, disconn_cback=None):
        """Register callbacks to the (de)activation events, calling
        them if there are already routes available.
        Note that alt_callback must be False to avoid registration,
        if it is None the value for the regular callback will be used."""
        if conn_cback:
            connected_dids = list(self.connections.keys())
            self.route_available.subscribe(conn_cback)
            if connected_dids:
                conn_cback(self, self.connections[connected_dids[0]])
            if alt_cback is None:
                alt_cback = conn_cback
            if alt_cback:
                self.alt_route_available.subscribe(conn_cback)
                for did in connected_dids[1:]:
                    conn_cback(self, self.connections[did])
        if disconn_cback:
            self.route_closed.subscribe(disconn_cback)

    def unsubscribe(self, conn_cback, alt_cback=False, disconn_cback=None):
        if conn_cback:
            # connected_dids = list(self.connections.keys())
            self.route_available.unsubscribe(conn_cback)
            if alt_cback is None:
                alt_cback = conn_cback
            if alt_cback:
                self.alt_route_available.unsubscribe(conn_cback)
        if disconn_cback:
            self.route_closed.unsubscribe(disconn_cback)

    def new_connection(self, conn):
        if conn.did in self.devhashes:
            self.connections[conn.did] = conn
            if self.req_high:
                conn.grab()
            if len(self.connections) + len(self.indirect) == 1:
                self.route_available(self, conn)
            else:
                self.alt_route_available(self, conn)
            return True
        return False

    def connection_closed(self, conn):
        if conn.did in self.devhashes:
            if self.req_high:
                conn.release()
            if self.keep_all_up:
                df = conn.connect()
                if df:
                    df.addCallback(conn.schedule_connection)
            else:
                self.connections.pop(conn.did)
            if len(self.connections) + len(self.indirect) == 0:
                self.route_closed(self)

    def release(self, priority):
        if priority:
            if not self.req_high:
                log.warn("mismatch in priority of route release [high]: {}"
                         .format(self.idhash))
            else:
                self.req_high -= 1
            if not self.req_high:
                for conn in self.connections:
                    conn.release()
        else:
            if not self.req_low:
                log.warn("mismatch in priority of route release [low]: {}"
                         .format(self.idhash))
            else:
                self.req_low -= 1

    def connect(self):
        if not self.devhashes:
            log.warn("can't connect: identity {} has no routes"
                     .format(self.idhash))
            return
        if self.keep_all_up:
            log.info("trying to connect to all devices of " + self.idhash)
            for did in self.devhashes:
                df = idrouter.make_connections(self.ctx, did)
                if df:
                    df.addCallback(lambda conn: conn.schedule_connection())
        else:
            log.info("trying to connect to any device of " + self.idhash)

            def do_connect(devhashes):
                df = idrouter.make_connections(self.ctx, devhashes[0])
                if df and len(devhashes) > 1:
                    df.addErrback(lambda e: do_connect(devhashes[1:]))

            do_connect(list(self.devhashes))


class IdentityRouter:
    def __init__(self):
        self.connections = {}
        self.routes = {}
        handshake_successful.subscribe(self.new_connection)
        disconnected.subscribe(self.connection_closed)

    def make_connections(self, ctx, did):
        if did in self.connections:
            return None
        self.connections[did] = Connections(ctx, did)
        return self.connections[did].connect()

    def new_connection(self, conn):
        did = conn.idhash
        if did not in self.connections:
            self.connections[did] = Connections(None, did)
        conns = self.connections[did]
        conns.new_connection(conn)
        if did not in self.routes:
            # route directly to device
            self.routes[did] = Routes(did)
        for route in self.routes.values():
            route.new_connection(conns)

    def connection_closed(self, conn):
        did = conn.idhash
        if did not in self.connections:
            log.warn("untracked connection to {} was closed".format(did))
        else:
            conns = self.connections[did]
            for route in self.routes.values():
                route.connection_closed(conns)
            if conns.connection_closed(conn) and not conns.keep_around:
                self.connections.pop(did)

    def request_route(self, idhash, priority=0):
        if idhash not in self.routes:
            route = self.routes[idhash] = Routes(idhash)
            have_conn = False
            for conns in self.connections.values():
                have_conn |= route.new_connection(conns)
            if not have_conn:
                if True:    # if priority or not have indirect:
                    route.connect()
        else:
            route = self.routes[idhash]
        if priority:
            route.req_high += 1
        else:
            route.req_low += 1
        return route

    def release_route(self, idhash, priority=0):
        if idhash not in self.routes:
            log.warn("trying to release a route that wasn't requested: {}"
                     .format(idhash))
            return
        route = self.routes[idhash]
        route.release(priority)


idrouter = IdentityRouter()
