# -*- coding:utf-8 -*-

import sys
import errno

from phen import context as ctx
from .util import input_key_specs, input_passphrase


class DeviceSetup:
    def __init__(self):
        self.state = None
        self.stdin = sys.stdin
        self.stdout = sys.stdout

    def send(self, msg, nolf=False):
        lf = "" if nolf else "\n"
        self.stdout.write(msg + lf)
        if not lf:
            self.stdout.flush()

    def readline(self):
        retv = self.stdin.readline()
        return retv

    def _create_device(self):
        self.send(
            "It seems the device has not been initialized yet.\n"
            "Let's create an identity for it:\n"
            "(you may choose to leave the pass phrase empty if"
            " only you can access the device)\n"
        )
        try:
            self.state = 'load-dev'
            key_type, passphrase, aetherial = input_key_specs(self)
            if not key_type:
                return True
            self.state = None
        except KeyboardInterrupt:
            return False
        ctx.device.create_identity(
            passphrase, key_type=key_type, aetherial=aetherial
        )
        return True

    def _unlock_device(self):
        self.send("The device is locked.\n")
        try:
            self.state = 'load-dev'
            passphrase = input_passphrase(self)
            self.state = None
            ctx.device.load_identity(passphrase)
        except IOError as exc:
            if exc.errno == errno.EACCES:
                return True
            raise
        except KeyboardInterrupt:
            return False

    def setup(self):
        must_create = False
        try:
            idhash = ctx.device.load_identity()
            if idhash is None:
                must_create = True
        except IOError as exc:
            if exc.errno != errno.EACCES:
                return False
        while not ctx.device.cid:
            if must_create:
                if not self._create_device():
                    return
                continue
            if not self._unlock_device():
                return
