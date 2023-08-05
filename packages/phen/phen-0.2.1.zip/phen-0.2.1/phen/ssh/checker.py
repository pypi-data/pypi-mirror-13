# -*- coding:utf-8 -*-

import time
import logging
from zope.interface import implementer

from twisted.conch.error import ValidPublicKey
from twisted.conch.ssh import userauth
from twisted.conch.ssh.keys import Key
from twisted.cred.checkers import ICredentialsChecker
from twisted.cred.credentials import ISSHPrivateKey, IUsernamePassword
from twisted.cred.error import UnauthorizedLogin


log = logging.getLogger(__name__)


@implementer(ICredentialsChecker)
class Checker(object):
    credentialInterfaces = (ISSHPrivateKey, IUsernamePassword)

    def requestAvatarId(self, credentials):
        from phen.context import device
        username = credentials.username
        dotidx = username.rfind(b'.')
        if dotidx > 0:
            username = username[:dotidx]
        if not device.accounts[username].exists():
            raise UnauthorizedLogin("Unauthorized user")
        acc_config = device.accounts[username].get_config()
        if hasattr(credentials, "signature"):
            if not credentials.signature:
                raise ValidPublicKey()
            key = Key.fromString(credentials.blob)
            keys = acc_config.get("ssh-keys", [])
            if not isinstance(keys, list):
                keys = [keys]
            candidates = []
            for c_key in keys:
                try:
                    candidates.append(Key.fromString(c_key.encode("utf8")))
                except:
                    pass
            if not any(key == c_key for c_key in candidates):
                raise UnauthorizedLogin("Invalid public-key")
            if key.verify(credentials.signature, credentials.sigData):
                return credentials.username
        passphrase = getattr(credentials, "password", None)
        if acc_config.get("ssh-key-only", False) or passphrase is None:
            raise UnauthorizedLogin("Unauthorized authentication method")
        if not device.accounts[username].check_passphrase(
                passphrase.decode("utf8"),
                acc_config):
            raise UnauthorizedLogin("Incorrect passphrase")
        return credentials.username


class AuthServer(userauth.SSHUserAuthServer):
    passwordDelay = 3
    attemptLog = {}

    def _cbFinishedAuth(self, tup):
        addr = self.transport.getPeer().address.host
        self.attemptLog.pop(addr, None)
        log.info("account '{}' logged in <-- {}, with {}"
                 .format(self.user, addr, self.method))
        userauth.SSHUserAuthServer._cbFinishedAuth(self, tup)

    def _log_or_ban_attempt(self):
        addr = self.transport.getPeer().address.host
        if addr not in self.attemptLog:
            self.attemptLog[addr] = 1, 0
            cnt = 1
        else:
            cnt, tstamp = self.attemptLog[addr]
            cnt += 1
            cur_time = time.time()
            import phen
            attempts = int(phen.plugin_cfg("ssh", "attempts", 10))
            if cnt >= attempts:
                # clean the log
                for addr2, tup in list(self.attemptLog.items()):
                    if cur_time - tup[1] > 60 * 60:
                        self.attemptLog.pop(addr2)
                # ban the mf
                ban_cmd = phen.plugin_cfg("phen", "banIP", None)
                if ban_cmd is not None:
                    port = str(phen.plugin_cfg("ssh", "port", 2222))
                    import subprocess
                    try:
                        cmd = " ".join([ban_cmd, addr, port])
                        subprocess.Popen(cmd, shell=True)
                    except:
                        log.error("could not execute phen.banIP command")
                else:
                    log.warn("would have banned {}".format(addr))
                self.attemptLog.pop(addr)
            else:
                self.attemptLog[addr] = cnt, time.time()
        return addr, cnt

    def _ebBadAuth(self, reason):
        addr, cnt = self._log_or_ban_attempt()
        log.info("{} failed to log in as {}, try {} {}"
                 .format(addr, self.user, cnt, self.method))
        userauth.SSHUserAuthServer._ebBadAuth(self, reason)
