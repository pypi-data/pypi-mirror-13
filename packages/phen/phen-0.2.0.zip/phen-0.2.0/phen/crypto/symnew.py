# -*- coding:utf-8 -*-

import six
import errno
import base64
import hashlib

from cryptography.hazmat.primitives import ciphers
from cryptography.hazmat.backends import default_backend


backend = default_backend()


def pad(plain_text):
    """
        PKCS7 padding.
    """
    to_pad = 16 - len(plain_text) % 16
    return plain_text + six.int2byte(to_pad) * to_pad


def unpad(plain_text):
    """
        PKCS7 unpadding.
    """
    if six.PY3:
        return plain_text[:-plain_text[-1]]
    return plain_text[:-ord(plain_text[-1])]


class Encryptor:
    def __init__(self, cipher_file, key, ivec, b64=True):
        if b64:
            key = base64.b64decode(key)
            ivec = base64.b64decode(ivec)
        self.cipher_file = cipher_file
        self.plain_buffer = b""
        self.sha = hashlib.sha256(ivec)
        cipher = ciphers.Cipher(ciphers.algorithms.AES(key),
                                ciphers.modes.CBC(ivec), backend=backend)
        self.encryptor = cipher.encryptor()

    def write(self, data):
        self.plain_buffer += data
        bytes_to_write = len(self.plain_buffer)
        bytes_to_write -= bytes_to_write % 16
        if not bytes_to_write:
            return
        to_encrypt = self.plain_buffer[:bytes_to_write]
        cipher_buffer = self.encryptor.update(to_encrypt)
        self.plain_buffer = self.plain_buffer[bytes_to_write:]
        self.cipher_file.write(cipher_buffer)
        self.sha.update(cipher_buffer)

    def finish(self):
        cipher_buffer = self.encryptor.update(pad(self.plain_buffer))
        cipher_buffer += self.encryptor.finalize()
        self.cipher_file.write(cipher_buffer)
        self.sha.update(cipher_buffer)


def encrypt(plain_text, key, ivec, b64=True):
    if b64:
        key = base64.b64decode(key)
        ivec = base64.b64decode(ivec)
    cipher = ciphers.Cipher(ciphers.algorithms.AES(key),
                            ciphers.modes.CBC(ivec), backend=backend)
    encryptor = cipher.encryptor()
    cipher_text = encryptor.update(pad(plain_text)) + encryptor.finalize()
    return cipher_text


class Decryptor:
    def __init__(self, cipher_file, key, ivec, b64=True):
        if b64:
            key = base64.b64decode(key)
            ivec = base64.b64decode(ivec)
        self.cipher_file = cipher_file
        self.plain_buffer = b""
        self.sha = hashlib.sha256(ivec)
        cipher = ciphers.Cipher(ciphers.algorithms.AES(key),
                                ciphers.modes.CBC(ivec), backend=backend)
        self.decryptor = cipher.decryptor()

    def read(self, size=None):
        if size is None:
            cipher_buffer = self.cipher_file.read()
            size = len(cipher_buffer) + len(self.plain_buffer)
        elif size <= len(self.plain_buffer):
            retv = self.plain_buffer[:size]
            self.plain_buffer = self.plain_buffer[size:]
            return retv
        else:
            bytes_to_read = size - len(self.plain_buffer)
            if bytes_to_read % 16:
                bytes_to_read = bytes_to_read // 16 + 16
            cipher_buffer = self.cipher_file.read(bytes_to_read)
        if len(cipher_buffer) % 16:
            raise IOError(errno.EIO, "Data corrupted")
        self.sha.update(cipher_buffer)
        if not cipher_buffer:
            retv = self.plain_buffer + self.decryptor.finalize()
            self.plain_buffer = b""
            return retv
        temp = self.plain_buffer + self.decryptor.update(cipher_buffer)
        self.plain_buffer = temp[size:]
        return temp[:size]


def decrypt(cipher_text, key, ivec, b64=True):
    from six import BytesIO
    decryptor = Decryptor(BytesIO(cipher_text), key, ivec, b64)
    return unpad(decryptor.read())
