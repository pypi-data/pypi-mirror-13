# -*- coding:utf-8 -*-

from twisted.cred import portal
from twisted.conch import avatar, interfaces
from twisted.conch.insults import insults
from twisted.conch.ssh import session, filetransfer
from twisted.conch.ssh.keys import Key
from twisted.conch.ssh.factory import SSHFactory
from twisted.internet import reactor
from zope.interface import implements
from twisted.python import components

import logging

import phen
from phen.context import Context

from .checker import Checker, AuthServer
from .shell import ShellProtocol
from .ftp import SFTPServer
from .protocols import registry


log = logging.getLogger(__name__)


class SSHPhenContext(avatar.ConchUser):
    implements(interfaces.ISession)

    def __init__(self, username):
        avatar.ConchUser.__init__(self)
        dotidx = username.rfind(b'.')
        if dotidx > 0:
            username, id_prefix = username[:dotidx], username[dotidx + 1:]
        else:
            id_prefix = None
        from phen.context import device
        self.ctx = Context(device.accounts[username])
        if id_prefix:
            self.ctx.load_by_prefix(id_prefix)
        else:
            self.ctx.load_default()
        self.channelLookup['session'] = session.SSHSession
        self.subsystemLookup['sftp'] = filetransfer.FileTransferServer
        self.state = None
        self.use_color = False
        self.proto = None

    def openShell(self, protocol):
        serverProtocol = insults.ServerProtocol(ShellProtocol, self)
        serverProtocol.makeConnection(protocol)
        protocol.makeConnection(session.wrapProtocol(serverProtocol))

    def getPty(self, terminal, windowSize, attrs):
        self.use_color = b'xterm' in terminal

    def windowChanged(self, windowSize):
        print("chg:", windowSize)

    def execCommand(self, protocol, cmd):
        for cls, test in registry:
            if test(cmd):
                self.proto = sub_prot = cls(self, cmd)
                sub_prot.makeConnection(protocol)
                protocol.makeConnection(session.wrapProtocol(sub_prot))
                return True

    def eofReceived(self):
        if self.proto is not None:
            self.proto.eofReceived()

    def closed(self):
        log.info("account '{}' logged out -->".format(self.ctx.account))
        self.ctx.shutdown()


components.registerAdapter(
    SFTPServer, SSHPhenContext, filetransfer.ISFTPServer
)


class SSHPhenRealm:
    implements(portal.IRealm)

    def requestAvatar(self, avatarId, mind, *ifaces):
        if interfaces.IConchUser in ifaces:
            return ifaces[0], SSHPhenContext(avatarId), lambda: None
        else:
            raise Exception("No supported interfaces found.")


def get_key(type_="private"):
    import os
    key_str = phen.plugin_cfg("ssh", type_ + "Key", None)
    if key_str is not None:
        return Key.fromString(key_str)
    key_path = phen.plugin_cfg("ssh", type_ + "KeyPath", None)
    if os.getuid():
        if key_path is None:
            # fallback to the user's personal keys
            key_path = os.path.expanduser("~/.ssh/id_rsa")
            if type_ == "public":
                key_path += ".pub"
    else:
        key_path = "/etc/ssh/ssh_host_rsa_key"
        if type_ == "public":
            key_path += ".pub"
    if os.path.exists(key_path):
        return Key.fromFile(key_path)


factory = SSHFactory()


def setup():
    privateKey = get_key()
    publicKey = get_key("public")
    if privateKey and publicKey:
        factory.privateKeys = {'ssh-rsa': privateKey}
        factory.publicKeys = {'ssh-rsa': publicKey}
        factory.services.update({'ssh-userauth': AuthServer})
    else:
        log.error("No valid SSH server keys found.")
        return
    factory.portal = portal.Portal(SSHPhenRealm())
    factory.portal.registerChecker(Checker())
    host = phen.plugin_cfg("ssh", "host", "localhost")
    port = phen.plugin_cfg("ssh", "port", 2222)
    try:
        reactor.listenTCP(int(port), factory, interface=host)
    except Exception:
        log.exception("while trying to bind SSH port")
