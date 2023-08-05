# -*- coding:utf-8 -*-

"""
    Cryptographic Primitives
"""

import os
import json
import zlib
import base64
from hashlib import sha256

from . import asym  # noqa
try:
    import cryptography
    from . import symnew as sym
except ImportError:
    cryptography = False
    from . import symold as sym


key_size = 16

key_types = {
    'Curve25519': {"type": 'Curve25519'},
    'RSA 4096': {"type": 'RSA', "size": 4096},
    'RSA 3072': {"type": 'RSA', "size": 3072},
    'RSA 2048': {"type": 'RSA', "size": 2048},
    'ECC secp192r1': {"type": 'ECC', "curve": "secp192r1/nistp192"},
    'ECC secp224r1': {"type": 'ECC', "curve": "secp224r1/nistp224"},
    'ECC secp256r1': {"type": 'ECC', "curve": "secp256r1/nistp256"},
    'ECC secp384r1': {"type": 'ECC', "curve": "secp384r1/nistp384"},
    'ECC secp521r1': {"type": 'ECC', "curve": "secp521r1/nistp521"},
    # seccure only:
    #    'ECC secp112r1': {"type": 'ECC', "curve": "secp112r1"},
    #    'ECC secp128r1': {"type": 'ECC', "curve": "secp128r1"},
    #    'ECC secp160r1': {"type": 'ECC', "curve": "secp160r1"},
    # cryptography only:
    #    'ECC sect571k1': {"type": 'ECC', "curve": "sect571k1"},
    #    'ECC sect409k1': {"type": 'ECC', "curve": "sect409k1"},
    #    'ECC sect283k1': {"type": 'ECC', "curve": "sect283k1"},
    #    'ECC sect233k1': {"type": 'ECC', "curve": "sect233k1"},
    #    'ECC sect163k1': {"type": 'ECC', "curve": "sect163k1"},
    #    'ECC sect571r1': {"type": 'ECC', "curve": "sect571r1"},
    #    'ECC sect409r1': {"type": 'ECC', "curve": "sect409r1"},
    #    'ECC sect283r1': {"type": 'ECC', "curve": "sect283r1"},
    #    'ECC sect233r1': {"type": 'ECC', "curve": "sect233r1"},
    #    'ECC sect163r2': {"type": 'ECC', "curve": "sect163r2"},
}


def random_key():
    return base64.b64encode(os.urandom(key_size)).decode("ascii")


def random_iv(b64=True):
    return base64.b64encode(os.urandom(16)) if b64 else os.urandom(16)


def json_encrypt(data, passphrase=None, key=None, ivec=None):
    if ivec is None:
        riv = random_iv(False)
    if key is None:
        key = sha256(passphrase.encode("utf8")).digest()[:16]
    canonized = json.dumps(data, sort_keys=True, separators=(',', ':'))
    compressed = b"protected:" + zlib.compress(canonized.encode("utf8"), 9)
    encrypted = sym.encrypt(compressed, key, ivec or riv, False)
    return encrypted if ivec else (riv + encrypted)


def json_decrypt(data, passphrase=None, key=None, ivec=None, object_hook=None):
    if ivec is None:
        ivec, data = data[:16], data[16:]
    if key is None:
        key = sha256(passphrase.encode("utf8")).digest()[:16]
    from six import BytesIO
    dec = sym.Decryptor(BytesIO(data), key, ivec, False)
    if dec.read(10) != b"protected:":
        raise ValueError("Data corrupted or incorrect key")
    compressed = zlib.decompress(dec.read()).decode("utf8")
    return json.loads(compressed, object_hook=object_hook)
