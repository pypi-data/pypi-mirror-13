# -*- coding:utf-8 -*-

import errno
from hashlib import sha256
from base64 import b64decode as b64d, b64encode as b64e

import nacl.utils
import nacl.public
import nacl.signing
import nacl.encoding

from .asym import PublicKey, PrivateKey


class CurvePublicKey(PublicKey):
    def __init__(self, public_keys, encoded=None):
        self.crypto_key, self.verify_key = public_keys
        if not encoded:
            encoded = (
                self.crypto_key.encode(nacl.encoding.Base64Encoder),
                self.verify_key.encode(nacl.encoding.Base64Encoder)
            )
        key_hash = sha256(encoded[0] + encoded[1]).digest()
        from phen.util import bin2idhash
        self.hash = bin2idhash(key_hash)

    @staticmethod
    def load(data):
        keys = (
            nacl.public.PublicKey(
                data["keys"][0], encoder=nacl.encoding.Base64Encoder
            ),
            nacl.signing.VerifyKey(
                data["keys"][1], encoder=nacl.encoding.Base64Encoder
            )
        )
        return CurvePublicKey(keys, data["keys"])

    def dump(self):
        keys = (
            self.crypto_key.encode(nacl.encoding.Base64Encoder),
            self.verify_key.encode(nacl.encoding.Base64Encoder)
        )
        return {
            "version": 0, "type": 'Curve25519',
            "subtype": 'public', "keys": keys
        }

    def encrypt(self, data, private_key=None):
        if not private_key:
            # create a throw-away key so the source can't be identified
            private_key = nacl.public.PrivateKey.generate()
        box = nacl.public.Box(private_key, self.crypto_key)
        nonce = nacl.utils.random(box.NONCE_SIZE)
        encrypted = box.encrypt(data, nonce)
        pkencoded = private_key.public_key.encode(nacl.encoding.Base64Encoder)
        print(nonce, encrypted, pkencoded)
        return pkencoded + encrypted

    def verify(self, data, sign):
        try:
            self.verify_key.verify(b64d(sign) + data)
            return True
        except nacl.exceptions.BadSignatureError:
            return False


class CurvePrivateKey(PrivateKey):
    def __init__(self, private_keys):
        self.crypto_key, self.signing_key = private_keys
        public_keys = (
            self.crypto_key.public_key,
            self.signing_key.verify_key
        )
        self.pub = CurvePublicKey(public_keys)

    @staticmethod
    def new(key_spec):
        keys = (
            nacl.public.PrivateKey.generate(),
            nacl.signing.SigningKey.generate()
        )
        return CurvePrivateKey(keys)

    @staticmethod
    def load(data, passphrase):
        data = data.copy()
        if not isinstance(data["keys"], list):
            protected = b64d(data["keys"].encode("ascii"))
            try:
                if not passphrase:
                    raise ValueError
                from phen.crypto import json_decrypt
                encoded_keys = json_decrypt(protected, passphrase)
            except ValueError:
                raise IOError(errno.EACCES, "incorrect passphrase")
        else:
            encoded_keys = data["keys"]
        keys = (
            nacl.public.PrivateKey(
                encoded_keys[0], encoder=nacl.encoding.Base64Encoder
            ),
            nacl.signing.SigningKey(
                encoded_keys[1], encoder=nacl.encoding.Base64Encoder
            )
        )
        return CurvePrivateKey(keys)

    def dump(self, passphrase=""):
        keys = [
            self.crypto_key.encode(nacl.encoding.Base64Encoder)
            .decode("ascii"),
            self.signing_key.encode(nacl.encoding.Base64Encoder)
            .decode("ascii"),
        ]
        if passphrase:
            from phen.crypto import json_encrypt
            ekeys = b64e(json_encrypt(keys, passphrase)).decode("ascii")
        return {"version": 0, "type": 'Curve25519', "subtype": 'private',
                "keys": ekeys if passphrase else keys}

    def _derive_AES_key(self):
        h = sha256(b"phen")
        h.update(self.crypto_key.encode(nacl.encoding.Base64Encoder))
        return b64e(h.digest()[:16])

    def decrypt(self, data):
        public_key = nacl.public.PublicKey(
            data[:44], encoder=nacl.encoding.Base64Encoder
        )
        box = nacl.public.Box(self.crypto_key, public_key)
        return box.decrypt(data[44:])

    def sign(self, data):
        signed = self.signing_key.sign(data)
        return b64e(signed[:-len(data)]).decode("ascii")
