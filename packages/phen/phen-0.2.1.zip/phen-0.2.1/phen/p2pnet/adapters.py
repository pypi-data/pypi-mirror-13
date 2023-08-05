# -*- coding:utf-8 -*-

import json
import logging

from twisted.internet import reactor
from twisted.internet.protocol import Factory
from twisted.internet.error import CannotListenError

from .protocol import TCPRequest


log = logging.getLogger(__name__)


def is_ipv4_addr(ip):
    return ip.count(".") == 3 and ip.replace(".", "").isdigit()


class TCPRequestFactory(Factory):
    def buildProtocol(self, addr):
        return TCPRequest(addr)


class Adapter:
    def __init__(self, name, **kw):
        self.name = name
        self.method = kw.pop("method", "inet")
        self.auto = kw.pop("auto", True)
        self.proto = kw.pop("proto", "tcp")
        self.host = kw.pop("host", "0.0.0.0")
        self.port = kw.pop("port", 42519)
        self.use_upnp = kw.pop("use_upnp", False)
        if kw:
            log.warn("adapter '{}' has unknown parameters '{}'"
                     .format(name, repr(kw)))
        self.listener = None

    def __repr__(self):
        return "[{}: {}:{} ({}) {}, {}]".format(
            self.name, self.host, self.port, self.proto,
            "auto" if self.auto else "manual",
            "off" if self.listener is None else "on"
        )

    def listen(self):
        if self.proto != "tcp":
            log.warn("adapter '{}' - only TCP implemented (not {})"
                     .format(self.name, self.proto))
        if self.use_upnp:
            from .upnp import upnp
            if upnp.get_state():
                if upnp.external_ip and upnp.external_ip != self.current_ipv4:
                    self.update_connections_ip(upnp.external_ip)
                upnp.forward(self.port, self.proto)
        try:
            self.listener = reactor.listenTCP(
                self.port, TCPRequestFactory(), interface=self.host
            )
            log.info("listening to TCP port {}".format(self.port))
        except CannotListenError:
            log.warn("could not listen - adapter '{}' - TCP port {}"
                     .format(self.name, self.port))

    def stopListening(self):
        if self.listener is not None:
            self.listener.stopListening()
            self.listener = None

    @staticmethod
    def from_file(ctx, dirpath, name):
        filepath = u"/".join((dirpath, name))
        try:
            return Adapter(name[:-8], **ctx.fs.json_read(filepath))
        except Exception:
            log.error("couldn't read connection config: " + filepath)

    def commit(self, dirpath):
        from phen.context import device as ctx
        filepath = u"/".join((dirpath, self.name + ".adapter"))
        ctx.fs.json_write(filepath, {
            k: v for k, v in self.__dict__.items()
            if k in "method auto proto host port use_upnp".split()
        })

    def rename(self, dirpath, new_name):
        from phen.context import device as ctx
        old_path = u"/".join((dirpath, self.name + ".adapter"))
        new_path = u"/".join((dirpath, new_name + ".adapter"))
        self.name = new_name
        ctx.fs.rename(old_path, new_path)

    @staticmethod
    def from_device():
        """
            Return all connection methods of the device identity
        """
        retv = {}
        from phen.context import device as ctx
        dirpath = ctx.cid.subpath(u"system/adapters")
        if not ctx.fs.exists(dirpath):
            ctx.fs.makedirs(dirpath)
            return dirpath, retv
        for fname in ctx.fs.listdir(dirpath):
            if not fname.endswith(".adapter"):
                continue
            cm = Adapter.from_file(ctx, dirpath, fname)
            if cm is None:
                continue
            if cm.method != "inet":
                log.warn("unknown adapter method {} ignored in {}"
                         .format(cm.method, fname))
                continue
            retv[cm.name] = cm
        return dirpath, retv


class Adapters:
    def __init__(self):
        self.current_ipv4 = ""  # self.get_current_ipv4()
        self.reported_ipv4 = []
        self.path, self.adapters = Adapter.from_device()

    def restart(self):
        self.shut_down()
        self.start_up()

    def start_up(self, force=False, name=None):
        if name is not None:
            return self.adapters[name].listen()
        for adapter in self.adapters.values():
            if force or adapter.auto:
                adapter.listen()

    def shut_down(self):
        for adapter in self.adapters.values():
            adapter.stopListening()

    def new(self, name):
        if name in self.adapters:
            return False
        self.adapters[name] = Adapter(name)
        return True
        # note: the new adapter is not commited

    def commit(self, name):
        self.adapters[name].commit(self.path)

    def check_dynamic_ipv4(self, ip):
        # todo: this must be moved to connection.py
        if ip == self.current_ipv4 or not is_ipv4_addr(ip):
            return
        self.reported_ipv4.append(ip)
        if len(self.reported_ipv4) < 10:
            return
        from collections import Counter
        cnt = Counter(self.reported_ipv4)
        mc = cnt.most_common(1)[0]
        if mc[1] < 5:
            self.reported_ipv4.pop(0)  # remove oldest
            return
        # ok, time to update
        self.reported_ipv4 = []
        # self.update_connections_ip(mc[0])

    def update_connections_ip(self, ip):
        raise NotImplementedError
        # todo: this must be moved to connection.py
        from phen.context import device as ctx
        log.info("publishing new ipv4 in *.connection: " + ip)
        self.current_ipv4 = ip
        for fname in ctx.fs.listdir("."):
            if not fname.endswith("connection"):
                continue
            with ctx.fs.open(fname) as infile:
                cfg = json.loads(infile.read())
            if cfg["method"] != "inet":
                continue
            addr = cfg.get("address", "")
            if not addr or is_ipv4_addr(addr):
                cfg["address"] = self.current_ipv4
                __debug__ and log.debug("updated " + fname)
                with ctx.fs.open(fname, 'w') as out:
                    out.write(json.dumps(cfg))

    def get_current_ipv4(self):
        raise NotImplementedError
        # todo: this must be moved to connection.py
        from phen.context import device as ctx
        for fname in ctx.fs.listdir():
            if not fname.endswith("connection"):
                continue
            with ctx.fs.open(fname) as infile:
                cfg = json.loads(infile.read())
            addr = cfg.get("address", "")
            if is_ipv4_addr(addr):
                log.info("ipv4 published in *.connection: " + addr)
                return addr
        return None
