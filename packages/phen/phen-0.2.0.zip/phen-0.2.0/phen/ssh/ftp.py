# -*- coding:utf-8 -*-

from twisted.conch.interfaces import ISFTPServer, ISFTPFile
from twisted.conch.ssh import filetransfer as fxfer
from twisted.conch.ls import lsLine

from zope.interface import implements
from functools import wraps


def cvt_stat(stat):
    return {"size": stat.st_size,
            "uid": 0, "gid": 0,
            "permissions": stat.st_mode,
            "atime": stat.st_atime,
            "mtime": stat.st_mtime}


def wrapped_IOError(func):

    @wraps(func)
    def check_error(*p, **kw):
        try:
            return func(*p, **kw)
        except IOError as exc:
            raise fxfer.SFTPError(fxfer.FX_FAILURE, str(exc))

    return check_error


class SFTPServer:
    implements(ISFTPServer)

    def __init__(self, avatar):
        self.fs = avatar.ctx.fs

    def gotVersion(self, otherVersion, extData):
        return {}

    @wrapped_IOError
    def openFile(self, filepath, flags, attrs):
        return MarshalledFile(self, filepath.decode("utf8"), flags, attrs)

    @wrapped_IOError
    def openDirectory(self, path):
        return MarshalledFolder(self, path.decode("utf8"))

    @wrapped_IOError
    def removeFile(self, filename):
        self.fs.unlink(filename.decode("utf8"))

    @wrapped_IOError
    def renameFile(self, oldname, newname):
        self.fs.rename(oldname.decode("utf8"), newname.decode("utf8"))

    @wrapped_IOError
    def makeDirectory(self, path, attrs=None):
        self.fs.mkdir(path.decode("utf8"))

    @wrapped_IOError
    def removeDirectory(self, path):
        self.fs.rmdir(path.decode("utf8"))

    def _stat_path(self, path):
        try:
            fmeta = self.fs.filemeta(path.decode("utf8"))
        except IOError:
            from phen.filesystem.folder.filemeta import Metadata
            fmeta = Metadata()
        return fmeta.stat()

    @wrapped_IOError
    def getAttrs(self, path, followLinks=True):
        return cvt_stat(self._stat_path(path))

    def setAttrs(self, path, attrs):
        raise NotImplementedError

    @wrapped_IOError
    def readLink(self, path):
        raise IOError("Not a link: " + path)

    def makeLink(self, linkPath, targetPath):
        raise NotImplementedError

    @wrapped_IOError
    def realPath(self, path):
        retv = u"/" + self.fs.abspath(path.decode("utf8"))
        return retv.encode("utf8")

    def extendedRequest(self, extendedName, extendedData):
        raise NotImplementedError


class MarshalledFile:
    implements(ISFTPFile)

    def __init__(self, server, path, flags, attrs=None):
        self.server = server
        self.path = path
        if flags & fxfer.FXF_APPEND:
            mode = 'a'
        else:
            if flags & fxfer.FXF_WRITE:
                mode = 'w'
            else:
                mode = 'r'
        self.handle = server.fs.open(path, mode)

    def close(self):
        self.handle.close()

    def readChunk(self, offset, length):
        self.handle.seek(offset)
        return self.handle.read(length)

    def writeChunk(self, offset, data):
        self.handle.seek(offset)
        return self.handle.write(data)

    def getAttrs(self):
        return self.server.getAttrs(self.path)

    def setAttrs(self, attrs=None):
        raise NotImplementedError


class MarshalledFolder:
    def __init__(self, server, path):
        self.server = server
        self.path = path
        self.files = server.fs.listdir(path)

    def __iter__(self):
        return self

    def has_next(self):
        return self.files

    def next(self):
        if not self.files:
            raise StopIteration
        fname = self.files.pop(0)
        stat = self.server._stat_path("/".join((self.path, fname)))
        fname = fname.encode("utf8")
        return (fname, lsLine(fname, stat), cvt_stat(stat))

    def close(self):
        self.files = None
