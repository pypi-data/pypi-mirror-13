# -*- coding:utf-8 -*-

import os
import six
import errno
from hashlib import sha256
from base64 import b64decode as b64d, b64encode as b64e

from Crypto.Cipher import PKCS1_OAEP as Cipher
from Crypto.Signature import PKCS1_PSS as Signer
from Crypto.PublicKey import RSA
from Crypto.Hash import SHA256

from phen.util import bin2idhash
from .asym import PublicKey, PrivateKey


class RSAPublicKey(PublicKey):
    def __init__(self, key_data, key=None):
        subtype = key_data.get("subtype", 'public')
        if subtype != 'public':
            raise ValueError("Not public key: '{}'".format(subtype))
        if key is None:
            if six.PY3:
                self.key = RSA.construct((key_data["n"], key_data["e"]))
            else:
                self.key = RSA.construct(
                    (long(key_data["n"]), long(key_data["e"]))
                )
        else:
            self.key = key
        self.size = key_data.get("size")
        modulus = str(self.key.n).encode("ascii")
        self.hash = bin2idhash(sha256(modulus).digest())

    @staticmethod
    def load(data):
        return RSAPublicKey(data)

    def dump(self):
        return {"version": 0, "type": 'RSA', "subtype": 'public',
                "n": self.key.n, "e": self.key.e, "size": self.size}

    def encrypt(self, data):
        enc = Cipher.new(self.key)
        return enc.encrypt(data)

    def verify(self, data, sign):
        verifier = Signer.new(self.key)
        return verifier.verify(SHA256.new(data), b64d(sign.encode("ascii")))


class RSAPrivateKey(PrivateKey):
    def __init__(self, key_spec):
        """
            Creates a new private key or imports an existing one
        """
        subtype = key_spec.get("subtype", 'private')
        if subtype != 'private':
            raise ValueError("Not private key: '{}'".format(subtype))
        self.key = key_spec.get("key")
        self.size = key_spec.get("size")
        pub_data = key_spec.copy()
        pub_data["subtype"] = 'public'
        self.pub = RSAPublicKey(pub_data, self.key.publickey())

    @staticmethod
    def new(key_spec):
        data = key_spec.copy()
        data["key"] = RSA.generate(key_spec.get("size"), os.urandom)
        return RSAPrivateKey(data)

    @staticmethod
    def load(data, passphrase):
        data = data.copy()
        if not isinstance(data["key"], dict):
            protected = b64d(data["key"].encode("ascii"))
            try:
                if not passphrase:
                    raise ValueError
                from phen.crypto import json_decrypt
                key_data = json_decrypt(protected, passphrase)
            except ValueError:
                raise IOError(errno.EACCES, "incorrect passphrase")
        else:
            key_data = data["key"]
        if six.PY3:
            numbers = (key_data[k] for k in "nedpq")
        else:
            numbers = (long(key_data[k]) for k in "nedpq")
        data["key"] = RSA.construct(tuple(numbers))
        return RSAPrivateKey(data)

    def dump(self, passphrase=""):
        numbers = {k: getattr(self.key, k) for k in "endpq"}
        if passphrase:
            from phen.crypto import json_encrypt
            ekey = b64e(json_encrypt(numbers, passphrase)).decode("ascii")
        return {"version": 0,
                "type": 'RSA', "subtype": 'private',
                "size": self.size, "key": ekey if passphrase else numbers}

    def _derive_AES_key(self):
        h = sha256(b"phen")
        h.update(str(self.key.p).encode("ascii"))
        return b64e(h.digest()[:16])

    def decrypt(self, data):
        enc = Cipher.new(self.key)
        return enc.decrypt(data)

    def sign(self, data):
        signer = Signer.new(self.key)
        retv = signer.sign(SHA256.new(data))
        return b64e(retv).decode("ascii")
