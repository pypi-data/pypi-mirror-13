# -*- coding:utf-8 -*-

import os
import logging
from twisted.internet import reactor
from twisted.web import resource, server

import phen
from .root import Root


log = logging.getLogger(__name__)


class Redirector(resource.Resource):
    isLeaf = True

    def __init__(self, port):
        resource.Resource.__init__(self)
        if port != 443:
            self.location = "https://{{}}:{}{{}}".format(port)
        else:
            self.location = "https://{}{}"

    def render_GET(self, request):
        request.redirect(self.location.format(
            request.getRequestHostname(), request.path
        ))
        request.finish()
        return server.NOT_DONE_YET


class Server:
    def __init__(self):
        self.redirector = None
        self.server = None
        self.root = Root()

    def setup(self):
        host = phen.plugin_cfg("http", "host", "localhost")
        redirect = phen.plugin_cfg("http", "redirect", 0)
        disable_ssl = phen.plugin_cfg("http", "disable_ssl", False)
        if disable_ssl:
            port = 2080 if os.getuid() else 80
        else:
            port = 2443 if os.getuid() else 443
        port = int(phen.plugin_cfg("http", "port", port))
        from phen.context import device
        if device:
            from phen.util.config import load
            self.cfg = load(device.fs, u"http.jcfg", abscence_ok=True)
            if "default-message" in self.cfg:
                self.root.index.content = self.cfg["default-message"]
            host = self.cfg.get("host", host)
            port = self.cfg.get("port", port)
            redirect = self.cfg.get("redirect", redirect)
            disable_ssl = self.cfg.get("disable-ssl", disable_ssl)
            self.root.set_domains(self.cfg.get("domains", {}))
            self.root.mount_statics(self.cfg.get("static", {}))
        else:
            self.cfg = {}
        if not disable_ssl and redirect:
            self.redirector = self._setup_redirector(host, redirect, port)
        self.server = self._setup_web_server(disable_ssl, host, port)

    def shutdown(self):
        if self.redirector:
            self.redirector.stopListening()
            self.redirector = None
        if self.server:
            self.server.stopListening()
            self.server = None

    def _setup_redirector(self, host, redirect, port):
        """setup http to https redirector"""
        if redirect is True:
            redirect = 2080 if os.getuid() else 80
        else:
            redirect = int(redirect)
        sire = server.Site(Redirector(port))
        return reactor.listenTCP(redirect, sire, interface=host)

    def _setup_web_server(self, disable_ssl, host, port):
        """setup http(s) interface"""
        log_path = self.cfg.get("log-path")
        if log_path:
            log_path = log_path.encode("utf8")
        site = server.Site(self.root, logPath=log_path)
        if disable_ssl:
            return reactor.listenTCP(port, site, interface=host)
        from phen.util.ssl import get_ctx
        return reactor.listenSSL(port, site, get_ctx(), interface=host)
