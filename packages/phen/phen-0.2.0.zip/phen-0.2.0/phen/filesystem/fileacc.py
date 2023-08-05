# -*- coding:utf-8 -*-

"""
    Temporary Cryptographing File module.
"""

import os
import six
import errno

from tempfile import NamedTemporaryFile
from base64 import b64decode as b64d

from phen import storage
from phen.util import bin2idhash
from phen.crypto import sym, random_key


class FileAccessor:
    """
        Temporary Cryptographing File.

        Store the unencrypted data in a temporary file, and encrypt
        it in its final non-volatile destination when closed.
    """
    def __init__(self, parent, filemeta, mode, author):
        self.author = author
        self.parent = parent
        self.filemeta = filemeta
        self.mode = mode
        self.file = NamedTemporaryFile()
        if 'r' in mode or 'a' in mode:
            self.decrypt()
        if 'a' in mode:
            self.seek(0, os.SEEK_END)
            # we're not completely POSIX compliant, as you can
            # seek and write elsewhere
        else:
            self.seek(0)
        # note that the NamedTemporaryFile has mode '+' by default

    def decrypt(self):
        """
            Decrypt the file contents into a temporary file.
        """
        fid_pair = self.parent.idhash, self.filemeta.fid
        if not storage.store.is_available(fid_pair):
            self.parent.fs.request(fid_pair)
            if not storage.store.is_available(fid_pair):
                raise IOError(errno.EAGAIN,
                              "File data must be retrieved: '{}'"
                              .format(self.filemeta.name))
        with storage.store.load(fid_pair) as inf:
            ivec = inf.read(16)
            key = b64d(self.filemeta.key)
            dec = sym.Decryptor(inf, key, ivec, False)
            while True:
                chunk = dec.read(1 << 16)
                if not chunk:
                    break
                self.write(chunk)
            sha = dec.sha
            self.truncate(self.filemeta.size)
            sha.update(self.author.encode("ascii"))
            fid = bin2idhash(sha.digest())
            if fid != self.filemeta.fid:
                raise IOError(errno.EIO, "Data corrupted")

    def encrypt(self):
        """
            Encrypt the data on the temporary file.
        """
        key = random_key()
        ivec = os.urandom(16)
        idhash = self.parent.idhash
        with storage.store.new_tempfile() as out:
            enc = sym.Encryptor(out, b64d(key), ivec, False)
            self.seek(0)
            out.write(ivec)
            while True:
                chunk = self.read(1 << 16)
                if not chunk:
                    break
                enc.write(chunk)
            enc.finish()
            out.flush()
            sha = enc.sha
        oldfmeta = self.filemeta
        self.filemeta = oldfmeta.__class__(oldfmeta)  # clone it
        # hash author's id
        sha.update(self.author.encode("ascii"))
        fid = bin2idhash(sha.digest())
        self.filemeta.size = self.tell()
        self.filemeta.key = key
        self.filemeta.fid = fid
        self.filemeta.touch()
        storage.store.store_tempfile(out, (idhash, fid))
        return oldfmeta

    def __enter__(self):
        """
            Called by the 'with' protocol.
        """
        return self

    def __exit__(self, *p):
        """
            Called by the 'with' protocol.
        """
        self.close()

    def __del__(self):
        """
            Called when the object is about to be destroyed.
        """
        self.close()

    def close(self):
        """
            Finish the file processing.
        """
        if not self.file.closed:
            if 'r' not in self.mode or '+' in self.mode:
                oldfmeta = self.encrypt()
                self.parent._close(self, oldfmeta)
            self.file.close()

    def write(self, buff):
        """
            'write' wrapper.
        """
        # note, be sure the buffer is a str or bytearray
        try:
            retv = self.file.write(buff)
        except TypeError:  # python3
            if isinstance(buff, six.text_type):
                raise ValueError("String must be encoded (e.g. in utf8)")
        except ValueError:
            if isinstance(buff, six.text_type):  # python2
                raise ValueError("String must be encoded (e.g. in utf8)")
            raise IOError("File not open for writing")
        return retv

    def read(self, length=None):
        """
            'read' wrapper.
        """
        if length is not None:
            return self.file.read(length)
        else:
            return self.file.read()

    def readline(self, length=None):
        """
            'read' wrapper.
        """
        if length is not None:
            return self.file.readline(length)
        else:
            return self.file.readline()

    def __iter__(self):
        while True:
            line = self.readline()
            if not line:
                break
            yield line

    def seek(self, offset, whence=0):
        """
            'seek' wrapper.
        """
        return self.file.seek(offset, whence)

    def tell(self):
        """
            'tell' wrapper.
        """
        return self.file.tell()

    def truncate(self, length=0):
        """
            'truncate' wrapper.
        """
        return self.file.truncate(length)


class DecryptingStream:
    def __init__(self, input_file, filemeta, author):
        self.input_file = input_file
        self.filemeta = filemeta
        self.author = author
        self.bytes_read = 0
        ivec = self.input_file.read(16)
        key = b64d(self.filemeta.key)
        self.dec = sym.Decryptor(self.input_file, key, ivec, False)

    def tell(self):
        return self.bytes_read

    def read(self, size=None):
        if size is None:
            retv = self.dec.read()
        else:
            retv = self.dec.read(size)
        self.bytes_read += len(retv)
        if self.bytes_read > self.filemeta.size:
            retv = retv[:-(self.bytes_read - self.filemeta.size)]
            self.bytes_read = self.filemeta.size
        return retv

    def close(self):
        sha = self.dec.sha
        self.input_file.close()
        sha.update(self.author.encode("ascii"))
        fid = bin2idhash(sha.digest())
        if fid != self.filemeta.fid:
            raise IOError(errno.EIO, "Data corrupted")
        return fid


class EncryptingStream:
    def __init__(self, output_file):
        ivec = os.urandom(16)
        self.output_file = output_file
        self.bytes_written = 0
        self.output_file.write(ivec)
        self.key = random_key()
        self.enc = sym.Encryptor(output_file, b64d(self.key), ivec, False)

    def tell(self):
        return self.bytes_written

    def write(self, data):
        self.enc.write(data)
        size = len(data)
        self.bytes_written += size
        return size

    def finish(self, oldfmeta, author):
        self.enc.finish()
        sha = self.enc.sha
        self.output_file.close()
        filemeta = oldfmeta.__class__(oldfmeta)  # clone it
        # hash author's id
        sha.update(author.encode("ascii"))
        fid = bin2idhash(sha.digest())
        filemeta.size = self.bytes_written
        filemeta.key = self.key
        filemeta.fid = fid
        filemeta.touch()
        return self.output_file, filemeta

    def close(self):
        self.output_file.close()


class DirectFileAccessor:
    """
        Direct Cryptographing File.

        Directly store the encrypted data in the destination location.
    """
    def __init__(self, folder, filemeta, mode, author):
        self.author = author
        self.folder = folder
        self.filemeta = filemeta

        if 'a' in mode or 'w' in mode:
            output_file = storage.store.new_tempfile()
            out_stream = EncryptingStream(output_file)
        if 'r' in mode or 'a' in mode:
            fid_pair = folder.idhash, filemeta.fid
            if not storage.store.is_available(fid_pair):
                folder.fs.request(fid_pair)
                if not storage.store.is_available(fid_pair):
                    raise IOError(errno.EAGAIN,
                                  "File data must be retrieved: '{}'"
                                  .format(filemeta.name))
            input_file = storage.store.load(fid_pair)
            in_stream = DecryptingStream(input_file, filemeta, author)
        if 'a' in mode:
            while True:
                chunk = in_stream.read(1 << 16)
                if not chunk:
                    break
                out_stream.write(chunk)
            in_stream.close()
            mode = 'wd'
        self.mode = mode
        self.stream = in_stream if 'r' in mode else out_stream

    def __enter__(self):
        """
            Called by the 'with' protocol.
        """
        return self

    def __exit__(self, *p):
        """
            Called by the 'with' protocol.
        """
        self.close()

    def __del__(self):
        """
            Called when the object is about to be destroyed.
        """
        self.close()

    def close(self):
        """
            Finish the file processing.
        """
        if not self.stream:
            return
        if 'r' not in self.mode:
            oldfmeta = self.filemeta
            tempfile, self.filemeta = self.stream.finish(oldfmeta, self.author)
            fid_pair = self.folder.idhash, self.filemeta.fid
            storage.store.store_tempfile(tempfile, fid_pair)
            self.folder._close(self, oldfmeta)
        self.stream.close()
        self.stream = None

    def write(self, buff):
        """
            'write' wrapper.
        """
        try:
            retv = self.stream.write(buff)
        except TypeError:
            if isinstance(buff, six.text_type):
                raise ValueError("String must be encoded (e.g. in utf8)")
        except ValueError:
            if isinstance(buff, six.text_type):
                raise ValueError("String must be encoded (e.g. in utf8)")
            raise IOError("File not open for writing")
        return retv

    def read(self, length=None):
        """
            'read' wrapper.
        """
        return self.stream.read(length)

    def readline(self, length=None):
        """
            'readline' wrapper.
        """
        raise NotImplementedError

    def seek(self, offset, whence=0):
        """
            Seeking not allowed in direct mode.
        """
        raise IOError(errno.ESPIPE, "Seeking not allowed")

    def tell(self):
        """
            'tell' wrapper.
        """
        return self.stream.tell()

    def truncate(self, length=0):
        """
            'truncate' wrapper.
        """
        raise IOError(errno.ESTRPIPE, "Truncating not allowed")
