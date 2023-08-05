# -*- coding:utf-8 -*-

import errno
from hashlib import sha256
from base64 import b64decode as b64d, b64encode as b64e

from cryptography.hazmat.primitives.asymmetric import padding
from cryptography.hazmat.primitives.asymmetric import rsa
from cryptography.hazmat.backends import default_backend
from cryptography.exceptions import InvalidSignature
from cryptography.hazmat.primitives import hashes

from phen.util import bin2idhash
from .asym import PublicKey, PrivateKey


class RSAPublicKey(PublicKey):
    def __init__(self, key_data, key=None):
        subtype = key_data.get("subtype", 'public')
        if subtype != 'public':
            raise ValueError("Not public key: '{}'".format(subtype))
        if key is None:
            pub_num = rsa.RSAPublicNumbers(key_data["e"], key_data["n"])
            self.key = pub_num.public_key(default_backend())
        else:
            self.key = key
            pub_num = self.key.public_numbers()
        self.size = key_data.get("size")
        modulus = str(pub_num.n).encode("ascii")
        self.hash = bin2idhash(sha256(modulus).digest())

    @staticmethod
    def load(data):
        return RSAPublicKey(data)

    def dump(self):
        pub_num = self.key.public_numbers()
        return {"version": 0, "type": 'RSA', "subtype": 'public',
                "n": pub_num.n, "e": pub_num.e, "size": self.size}

    def encrypt(self, data):
        return self.key.encrypt(
            data,
            padding.OAEP(
                mgf=padding.MGF1(algorithm=hashes.SHA1()),
                algorithm=hashes.SHA1(),
                label=None,
            ),
        )

    def verify(self, data, sign):
        verifier = self.key.verifier(
            b64d(sign.encode("ascii")),
            padding.PSS(
                mgf=padding.MGF1(hashes.SHA256()),
                salt_length=32
            ),
            hashes.SHA256()
        )
        verifier.update(data)
        try:
            verifier.verify()
            return True
        except InvalidSignature:
            return False


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
        self.pub = RSAPublicKey(pub_data, self.key.public_key())

    @staticmethod
    def new(key_spec):
        data = key_spec.copy()
        data["key"] = rsa.generate_private_key(
            public_exponent=65537,
            key_size=key_spec.get("size"),
            backend=default_backend()
        )
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
        e, n, d, p, q = (key_data[k] for k in "endpq")
        pub = rsa.RSAPublicNumbers(e, n)
        dmp1 = rsa.rsa_crt_dmp1(d, p)
        dmq1 = rsa.rsa_crt_dmp1(d, q)
        iqmp = rsa.rsa_crt_iqmp(p, q)
        priv_num = rsa.RSAPrivateNumbers(p, q, d, dmp1, dmq1, iqmp, pub)
        data["key"] = priv_num.private_key(default_backend())
        return RSAPrivateKey(data)

    def dump(self, passphrase=""):
        priv_num = self.key.private_numbers()
        pub_num = self.pub.key.public_numbers()
        numbers = {k: getattr(priv_num, k) for k in "dpq"}
        numbers.update({k: getattr(pub_num, k) for k in "en"})
        if passphrase:
            from phen.crypto import json_encrypt
            ekey = b64e(json_encrypt(numbers, passphrase)).decode("ascii")
        return {"version": 0,
                "type": 'RSA', "subtype": 'private',
                "size": self.size, "key": ekey if passphrase else numbers}

    def _derive_AES_key(self):
        priv_num = self.key.private_numbers()
        h = sha256(b"phen")
        h.update(str(priv_num.p).encode("ascii"))
        return b64e(h.digest()[:16])

    def decrypt(self, data):
        return self.key.decrypt(
            data,
            padding.OAEP(
                mgf=padding.MGF1(algorithm=hashes.SHA1()),
                algorithm=hashes.SHA1(),
                label=None,
            ),
        )

    def sign(self, data):
        signer = self.key.signer(
            padding.PSS(
                mgf=padding.MGF1(hashes.SHA256()),
                salt_length=32
            ),
            hashes.SHA256()
        )
        signer.update(data)
        return b64e(signer.finalize()).decode("ascii")
