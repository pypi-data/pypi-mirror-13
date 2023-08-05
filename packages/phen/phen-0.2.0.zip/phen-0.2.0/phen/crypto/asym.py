# -*- coding:utf-8 -*-

import json


class PrivateKey:
    @staticmethod
    def new(key_type=None, key_spec=None, **kw):
        from phen.crypto import key_types
        from .curve25519 import CurvePrivateKey
        if key_type:
            key_spec = key_types.get(key_type)
        if key_spec is None:
            raise ValueError("Undetermined private key specification")
        if key_spec["type"] == 'RSA':
            return Backends.RSAPrivateKey.new(key_spec)
        elif key_spec["type"] == 'ECC':
            return Backends.ECCPrivateKey.new(key_spec, kw.get("secret"))
        elif key_spec["type"] == 'Curve25519':
            return CurvePrivateKey.new(key_spec)
        else:
            raise ValueError("Unknown private key type")

    @staticmethod
    def load(key_file, passphrase=None):
        data = json.loads(key_file.read().decode("utf8"))
        return PrivateKey.load_data(data, passphrase)

    @staticmethod
    def fs_load(fs, filename, passphrase=None):
        with fs.open(filename) as key_file:
            data = json.loads(key_file.read().decode("utf8"))
        return PrivateKey.load_data(data, passphrase)

    @staticmethod
    def load_data(data, passphrase=None):
        from .curve25519 import CurvePrivateKey
        if data["type"] == 'RSA':
            return Backends.RSAPrivateKey.load(data, passphrase)
        elif data["type"] == 'ECC':
            return Backends.ECCPrivateKey.load(data, passphrase)
        elif data["type"] == 'Curve25519':
            return CurvePrivateKey.load(data, passphrase)
        else:
            raise ValueError("Unknown private key type")

    _AES_key = None

    @property
    def AES_key(self):
        if self._AES_key is None:
            self._AES_key = self._derive_AES_key()
        return self._AES_key

    def save(self, key_file, passphrase=None):
        key_file.write(json.dumps(self.dump(passphrase)).encode("utf8"))

    def fs_save(self, fs, fname, passphrase=None):
        with fs.open(fname, 'w') as out:
            self.save(out, passphrase)


class PublicKey:
    @staticmethod
    def load(key_file):
        data = json.loads(key_file.read().decode("utf8"))
        return PublicKey.load_data(data)

    @staticmethod
    def fs_load(fs, filename):
        with fs.open(filename) as key_file:
            data = json.loads(key_file.read().decode("utf8"))
        return PublicKey.load_data(data)

    @staticmethod
    def load_data(data):
        from .curve25519 import CurvePublicKey
        if data["type"] == 'RSA':
            return Backends.RSAPublicKey.load(data)
        elif data["type"] == 'ECC':
            return Backends.ECCPublicKey.load(data)
        elif data["type"] == 'Curve25519':
            return CurvePublicKey.load(data)
        else:
            raise ValueError("Unknown public key type")

    def save(self, key_file):
        key_file.write(json.dumps(self.dump()).encode("utf8"))

    def fs_save(self, fs, fname):
        with fs.open(fname, 'w') as out:
            self.save(out)


class Backends:
    @classmethod
    def init(cls):
        cls.available = []
        try:
            from phen.crypto import rsa
            # todo: update this when PyCA/cryptography supports en/decryption
            # from phen.crypto import eccnew
            from phen.crypto import eccnew
            cls.available.append((eccnew, rsa))
        except ImportError:
            pass
        try:
            from phen.crypto import rsaold
            from phen.crypto import ecc
            cls.available.append((ecc, rsaold))
        except ImportError:
            pass
        if not cls.available:
            raise RuntimeError("Could not find any viable encryption backend")
        cls.set(cls.available[0])

    @classmethod
    def set(cls, mod):
        cls.ECCPrivateKey = mod[0].ECCPrivateKey
        cls.ECCPublicKey = mod[0].ECCPublicKey
        cls.RSAPrivateKey = mod[1].RSAPrivateKey
        cls.RSAPublicKey = mod[1].RSAPublicKey


Backends.init()
