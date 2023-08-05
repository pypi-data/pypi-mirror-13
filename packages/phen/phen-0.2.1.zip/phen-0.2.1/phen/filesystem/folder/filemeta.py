# -*- coding:utf-8 -*-

"""
    Metadata associated with files and folders.
"""

import os
import time

try:
    import pwd
except ImportError:
    pwd = None
try:
    import grp
except ImportError:
    grp = None


# file types
MULTI = -2
INVALID = -1
FOLDER = 0
FILE = 1
LINK = 2


class Metadata(object):
    """
        File description structure.
    """
    __slots__ = 'fid name type size mtime dtime key auth xattr'.split()

    def __init__(self, *p, **kw):
        """
            Initialize the metadata.

            Metadata(fid='d1d21as', name='abc', ...)
            Metadata(fmeta_to_clone)
        """
        self.size = 0
        self.auth = ''
        self.fid = None
        self.xattr = {}
        self.type = FOLDER
        self.key = '-'
        if p:
            obj = p[0]
            for k in self.__slots__:
                setattr(self, k, getattr(obj, k))
            return
        self.name = ''
        self.mtime = 0
        self.dtime = 0
        self.touch()
        self.dtime = self.mtime
        for k in kw:
            setattr(self, k, kw[k])

    def touch(self):
        """
            Update the timestamp.
        """
        self.mtime = time.time()

    def to_dict(self):
        """
            Dictionary representation for json.
        """
        return {k: getattr(self, k) for k in self.__slots__
                if getattr(self, k)}

    def __repr__(self):
        t = time.strftime("%Y-%m-%d %H:%M:%S", time.localtime(self.mtime))
        return (u"<[{2}] {0.type}: {0.name}, {0.size}B, {1}>"
                .format(self, t, self.fid[:5] if self.fid else "/////"))

    def is_multi(self):
        return self.type == MULTI

    def is_invalid(self):
        return self.type == INVALID

    def is_folder(self):
        return self.type == FOLDER

    def is_file(self):
        return self.type == FILE

    def is_link(self):
        return self.type == LINK

    @classmethod
    def filter_dict(cls, dct):
        """
            Return a dictionary with only valid attributes to Metadata.
        """
        return {k: v for k, v in dct.items() if k in cls.__slots__}

    def stat(self, sn_idhash=None):
        class stat_result(object):
            def __repr__(self):
                return "<S] {}>".format(", ".join(
                    "{}:{}".format(attr[3:], getattr(self, attr))
                    for attr in dir(self) if attr.startswith("st_")))
        st = stat_result()
        self.fill_stat(st, sn_idhash)
        return st

    def fill_stat(self, st, sn_idhash):
        """
            Convert the data to a stat structure.
        """
        import stat
        mode = self.xattr.get('mode')
        if mode is not None:
            st.st_mode = mode
        else:
            if self.type == FOLDER:
                st.st_mode = stat.S_IFDIR | 0o700
            else:
                st.st_mode = stat.S_IFREG | 0o600
        sn_info = sn_idhash and self.xattr.get(sn_idhash[:6])
        if sn_info:
            for attr in "dev ino nlink".split():
                setattr(st, "st_" + attr, sn_info[attr])
        else:
            st.st_dev, st.st_ino = 0, 0
            st.st_nlink = 1
        uid, gid = self.get_xugid()
        st.st_uid = os.getuid() if uid is None else uid
        st.st_gid = os.getgid() if gid is None else gid
        st.st_atime = self.xattr.get('atime', self.dtime)
        st.st_mtime = self.xattr.get('mtime', self.mtime)
        st.st_ctime = self.xattr.get('ctime', self.mtime)
        st.st_size = self.size

    def get_xugid(self):
        uid = self.xattr.get('uid')
        if uid is not None:
            try:
                if pwd and isinstance(uid, str):
                    uid = pwd.getpwnam(uid).pw_uid
            except KeyError:
                uid = None
        gid = self.xattr.get('gid')
        if gid is not None:
            try:
                if grp and isinstance(gid, str):
                    gid = grp.getgrnam(gid).gr_gid
            except KeyError:
                gid = None
        return uid, gid


def stat_to_xattr(st, sn_idhash):
    xad = {}
    sn_info = xad.setdefault(sn_idhash[:6], {})
    for attr in "dev ino nlink".split():
        sn_info[attr] = getattr(st, "st_" + attr)
    for attr in "mode atime mtime ctime".split():
        xad[attr] = getattr(st, "st_" + attr)
    if pwd:
        try:
            xad['uid'] = pwd.getpwuid(st.st_uid).pw_name
        except KeyError:
            xad['uid'] = st.st_uid
    if grp:
        try:
            xad['gid'] = grp.getgrgid(st.st_gid).gr_name
        except KeyError:
            xad['gid'] = st.st_gid
    return xad


def fm_json_load(dct):
    """
        Decode the Metadata from the json
    """
    if 'fid' in dct and 'key' in dct:
        # pylint: disable-msg=W0142
        return Metadata(**Metadata.filter_dict(dct))
    return dct
