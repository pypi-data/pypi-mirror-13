# -*- coding:utf-8 -*-

import os
import json
import errno
from hashlib import sha256, sha512
from base64 import b64decode as b64d, b64encode as b64e

from .asym import PublicKey, PrivateKey

from . import seccure


curve_names = {v[0] for v in seccure.RAW_CURVES.values()}


class ECCPublicKey(PublicKey):
    """
        Elliptic Curve Criptography private key
    """
    def __init__(self, key_spec, key=None):
        curve = key_spec.get("curve")
        if curve not in curve_names:
            raise ValueError("Unsupported ECC curve '{}'".format(curve))
        self.curve = curve
        if key is None:
            subtype = key_spec.get("subtype", 'public')
            if subtype != 'public':
                raise ValueError("Not public key: '{}'".format(subtype))
            s_curve = seccure.Curve.by_name(curve)
            x = key_spec["x"]
            y = key_spec["y"]
            key_data = str(key_spec["x"]) + str(key_spec["y"])
            self.key = seccure.PubKey(seccure.AffinePoint(x, y, s_curve))
        else:
            self.key = key
            key_data = str(key.p.x) + str(key.p.y)
        from phen.util import bin2idhash
        self.hash = bin2idhash(sha256(key_data.encode("ascii")).digest())

    @staticmethod
    def load(data):
        return ECCPublicKey(data)

    def dump(self):
        return {"version": 0,
                "type": 'ECC', "subtype": 'public',
                "curve": self.curve,
                "x": int(self.key.p.x), "y": int(self.key.p.y)}

    def encrypt(self, data, mac_bytes=10):
        import hmac
        import Crypto.Util
        import Crypto.Cipher.AES
        ephemeral = self.key.p.curve.passphrase_to_privkey(os.urandom(16))
        ecdh = seccure.serialize_number(
            (self.key.p * ephemeral.e).x,
            seccure.SER_BINARY, self.key.p.curve.elem_len_bin
        )
        shared_key = sha512(ecdh).digest()  # ecies kdf
        h = hmac.new(shared_key[32:], digestmod=sha256)
        ctr = Crypto.Util.Counter.new(128, initial_value=0)
        cipher = Crypto.Cipher.AES.new(
            shared_key[:32], Crypto.Cipher.AES.MODE_CTR, counter=ctr
        )
        enc_data = cipher.encrypt(data)
        h.update(enc_data)
        eph_pub = ephemeral.curve.base * ephemeral.e
        # `cryptography` doesn't support point compression, so
        # to keep this compatible we must output in format \x04
        # ser_key = eph_pub.to_bytes(seccure.SER_BINARY)
        outlen = self.key.p.curve.elem_len_bin
        ser_key = (
            b"\x04" +
            seccure.serialize_number(eph_pub.x, seccure.SER_BINARY, outlen) +
            seccure.serialize_number(eph_pub.y, seccure.SER_BINARY, outlen)
        )
        return ser_key + enc_data + h.digest()[:mac_bytes]

    def verify(self, data, sign):
        r, s = json.loads(sign)
        md = sha256(data).digest()
        return self.key.p._ECDSA_verify(md, None, r, s)


class ECCPrivateKey(PrivateKey):
    """
        Elliptic Curve Criptography private key
    """
    def __init__(self, key_spec, key):
        subtype = key_spec.get("subtype", 'private')
        if subtype != 'private':
            raise ValueError("Not private key: '{}'".format(subtype))
        self.key = key
        self.curve = key_spec.get("curve")
        pub = seccure.PubKey(key.curve.base * key.e)
        pub_spec = key_spec.copy()
        pub_spec["subtype"] = 'public'
        self.pub = ECCPublicKey(pub_spec, pub)

    @staticmethod
    def new(key_spec, secret=u""):
        curve = key_spec.get("curve")
        if curve not in curve_names:
            raise ValueError("Unsupported ECC curve '{}'".format(curve))
        if not secret:
            secret = os.urandom(16)
        else:
            secret = secret.encode("utf8")
        s_curve = seccure.Curve.by_name(curve)
        key = s_curve.passphrase_to_privkey(secret)
        return ECCPrivateKey(key_spec, key)

    @staticmethod
    def load(data, passphrase=u""):
        if "key" not in data or "curve" not in data:
            raise ValueError("Corrupted ECC private key file")
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
        e = int(key_data["e"])
        curve = data["curve"]
        if curve not in curve_names:
            raise ValueError("Unsupported ECC curve '{}'".format(curve))
        s_curve = seccure.Curve.by_name(curve)
        key = seccure.PrivKey(seccure.gmpy.mpz(e), s_curve)
        return ECCPrivateKey(data, key)

    def dump(self, passphrase=""):
        pub_num = self.pub.key.p
        numbers = {"e": int(self.key.e), "x": int(pub_num.x),
                   "y": int(pub_num.y)}
        if passphrase:
            from phen.crypto import json_encrypt
            ekey = b64e(json_encrypt(numbers, passphrase)).decode("ascii")
        data = {"version": 0,
                "type": 'ECC', "subtype": 'private',
                "curve": self.curve, "key": ekey if passphrase else numbers}
        return data

    def _derive_AES_key(self):
        h = sha256(b"phen" + str(int(self.key.e)).encode("ascii"))
        return b64e(h.digest()[:16])

    def decrypt(self, data, mac_bytes=10):
        import hmac
        import Crypto.Util
        import Crypto.Cipher.AES
        if data[:1] == b"\x00":
            data_idx = self.key.curve.pk_len_bin
            ephemeral = self.key.curve.point_from_string(
                data[:data_idx], seccure.SER_BINARY
            )
        elif data[:1] == b"\x04":
            klen = self.key.curve.elem_len_bin
            x = seccure.deserialize_number(data[1:1 + klen])
            y = seccure.deserialize_number(data[1 + klen:1 + klen * 2])
            data_idx = klen * 2 + 1
            ephemeral = seccure.AffinePoint(x, y, self.key.curve)
        else:
            raise ValueError("key format not supported")
        ecdh = seccure.serialize_number(
            (ephemeral * self.key.e).x,
            seccure.SER_BINARY, self.key.curve.elem_len_bin
        )
        shared_key = sha512(ecdh).digest()  # ecies kdf
        h = hmac.new(shared_key[32:], digestmod=sha256)
        ctr = Crypto.Util.Counter.new(128, initial_value=0)
        cipher = Crypto.Cipher.AES.new(
            shared_key[:32], Crypto.Cipher.AES.MODE_CTR, counter=ctr
        )
        enc_data = data[data_idx:-mac_bytes]
        h.update(enc_data)
        if h.digest()[:mac_bytes] != data[-mac_bytes:]:
            raise seccure.IntegrityError
        return cipher.decrypt(enc_data)

    def sign(self, data):
        md = sha256(data).digest()
        r, s = self.key._ECDSA_sign(md)
        return json.dumps([int(r), int(s)])
