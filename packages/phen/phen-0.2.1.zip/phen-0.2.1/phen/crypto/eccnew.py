# -*- coding:utf-8 -*-

import json
import errno
from hashlib import sha256, sha512
from base64 import b64decode as b64d, b64encode as b64e

from phen.util import bin2idhash
from .asym import PublicKey, PrivateKey

from cryptography.exceptions import InvalidSignature
from cryptography.hazmat.backends import default_backend
from cryptography.hazmat.primitives import hashes
from cryptography.hazmat.primitives.asymmetric import ec, utils


class ECCPublicKey(PublicKey):
    """
        Elliptic Curve Criptography private key
    """
    def __init__(self, key_spec, key=None):
        curve = key_spec.get("curve")
        curve_attr = curve.split("/")[0].upper()
        if not hasattr(ec, curve_attr):
            raise ValueError("Unsupported ECC curve '{}'".format(curve))
        self.curve = curve
        if key is None:
            subtype = key_spec.get("subtype", 'public')
            if subtype != 'public':
                raise ValueError("Not public key: '{}'".format(subtype))
            x = key_spec["x"]
            y = key_spec["y"]
            curve = getattr(ec, curve_attr)()
            key_data = str(key_spec["x"]) + str(key_spec["y"])
            pubnum = ec.EllipticCurvePublicNumbers(x, y, curve)
            self.key = pubnum.public_key(default_backend())
        else:
            self.key = key
            n = self.key.public_numbers()
            key_data = str(n.x) + str(n.y)
        self.hash = bin2idhash(sha256(key_data.encode("ascii")).digest())

    @staticmethod
    def load(data):
        return ECCPublicKey(data)

    def dump(self):
        n = self.key.public_numbers()
        return {"version": 0,
                "type": 'ECC', "subtype": 'public',
                "curve": self.curve,
                "x": n.x, "y": n.y}

    def encrypt(self, data, mac_bytes=10):
        import hmac
        from cryptography.hazmat.primitives import ciphers
        n = self.key.public_numbers()
        ephemeral = ec.generate_private_key(n.curve, default_backend())
        ecdh = ephemeral.exchange(ec.ECDH(), self.key)
        shared_key = sha512(ecdh).digest()  # ecies kdf
        h = hmac.new(shared_key[32:], digestmod=sha256)
        cipher = ciphers.Cipher(
            ciphers.algorithms.AES(shared_key[:32]),
            ciphers.modes.CTR(b'\x00' * 16), backend=default_backend()
        )
        encryptor = cipher.encryptor()
        enc_data = encryptor.update(data) + encryptor.finalize()
        h.update(enc_data)
        eph_pub = ephemeral.public_key()
        ser_key = eph_pub.public_numbers().encode_point()  # format \x04
        return ser_key + enc_data + h.digest()[:mac_bytes]

    def verify(self, data, signature):
        r, s = json.loads(signature)
        signature = utils.encode_rfc6979_signature(r, s)
        v = self.key.verifier(signature, ec.ECDSA(hashes.SHA256()))
        v.update(data)
        try:
            v.verify()
        except InvalidSignature:
            return False
        return True


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
        pub = self.key.public_key()
        pub_spec = key_spec.copy()
        pub_spec["subtype"] = 'public'
        self.pub = ECCPublicKey(pub_spec, pub)

    @staticmethod
    def new(key_spec, secret=u""):
        curve = key_spec.get("curve")
        curve_attr = curve.split("/")[0].upper()
        if not hasattr(ec, curve_attr):
            raise ValueError("Unsupported ECC curve '{}'".format(curve))
        curve = getattr(ec, curve_attr)()
        if not secret:
            key = ec.generate_private_key(curve, default_backend())
        else:
            from .pp_ec_kdf import ec_passphrase_to_key
            key = ec_passphrase_to_key(curve, secret.encode("utf8"))
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
        x = int(key_data["x"])
        y = int(key_data["y"])
        curve_attr = data["curve"].split("/")[0].upper()
        curve = getattr(ec, curve_attr)()
        pub_num = ec.EllipticCurvePublicNumbers(x, y, curve)
        priv_num = ec.EllipticCurvePrivateNumbers(e, pub_num)
        key = priv_num.private_key(default_backend())
        return ECCPrivateKey(data, key)

    def dump(self, passphrase=""):
        priv_num = self.key.private_numbers()
        pub_num = self.pub.key.public_numbers()
        numbers = {"e": priv_num.private_value,
                   "x": pub_num.x, "y": pub_num.y}
        if passphrase:
            from phen.crypto import json_encrypt
            ekey = b64e(json_encrypt(numbers, passphrase)).decode("ascii")
        data = {"version": 0,
                "type": 'ECC', "subtype": 'private',
                "curve": self.curve, "key": ekey if passphrase else numbers}
        return data

    def _derive_AES_key(self):
        priv_num = self.key.private_numbers()
        h = sha256(b"phen" + str(priv_num.private_value).encode("ascii"))
        return b64e(h.digest()[:16])

    def decrypt(self, data, mac_bytes=10):
        import hmac
        from cryptography.hazmat.primitives import ciphers
        curve = self.pub.key.public_numbers().curve
        data_idx = (curve.key_size + 7) // 8 * 2 + 1
        ephemeral = ec.EllipticCurvePublicNumbers.from_encoded_point(
            curve, data[:data_idx]
        )
        ephemeral = ephemeral.public_key(default_backend())
        ecdh = self.key.exchange(ec.ECDH(), ephemeral)
        shared_key = sha512(ecdh).digest()
        h = hmac.new(shared_key[32:], digestmod=sha256)
        cipher = ciphers.Cipher(
            ciphers.algorithms.AES(shared_key[:32]),
            ciphers.modes.CTR(b'\x00' * 16), backend=default_backend()
        )
        decryptor = cipher.decryptor()
        enc_data = data[data_idx:-mac_bytes]
        retv = decryptor.update(enc_data) + decryptor.finalize()
        h.update(enc_data)
        if h.digest()[:mac_bytes] != data[-mac_bytes:]:
            raise ValueError("data corrupted")
        return retv

    def sign(self, data):
        signer = self.key.signer(ec.ECDSA(hashes.SHA256()))
        signer.update(data)
        signature = signer.finalize()
        r, s = utils.decode_rfc6979_signature(signature)
        return json.dumps([r, s])
