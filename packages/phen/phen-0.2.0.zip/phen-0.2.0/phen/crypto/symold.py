# -*- coding:utf-8 -*-

import six
import errno
import base64
import hashlib

from Crypto.Cipher import AES


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
        self.cipher = AES.new(key, AES.MODE_CBC, ivec)

    def write(self, data):
        self.plain_buffer += data
        bytes_to_write = len(self.plain_buffer)
        bytes_to_write -= bytes_to_write % 16
        if not bytes_to_write:
            return
        to_encrypt = self.plain_buffer[:bytes_to_write]
        cipher_buffer = self.cipher.encrypt(to_encrypt)
        self.plain_buffer = self.plain_buffer[bytes_to_write:]
        self.cipher_file.write(cipher_buffer)
        self.sha.update(cipher_buffer)

    def finish(self):
        cipher_buffer = self.cipher.encrypt(pad(self.plain_buffer))
        self.cipher_file.write(cipher_buffer)
        self.sha.update(cipher_buffer)


def encrypt(plain_text, key, ivec, b64=True):
    if b64:
        key = base64.b64decode(key)
        ivec = base64.b64decode(ivec)
    cipher = AES.new(key, AES.MODE_CBC, ivec)
    plain_text = pad(plain_text)
    cipher_text = cipher.encrypt(plain_text)
    return cipher_text


class Decryptor:
    def __init__(self, cipher_file, key, ivec, b64=True):
        if b64:
            key = base64.b64decode(key)
            ivec = base64.b64decode(ivec)
        self.cipher_file = cipher_file
        self.plain_buffer = b""
        self.sha = hashlib.sha256(ivec)
        self.cipher = AES.new(key, AES.MODE_CBC, ivec)

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
            retv = self.plain_buffer
            self.plain_buffer = b""
            return retv
        temp = self.plain_buffer + self.cipher.decrypt(cipher_buffer)
        self.plain_buffer = temp[size:]
        return temp[:size]


def decrypt(cipher_text, key, ivec, b64=True):
    from six import BytesIO
    decryptor = Decryptor(BytesIO(cipher_text), key, ivec, b64)
    retv = decryptor.read()
    return unpad(retv)
