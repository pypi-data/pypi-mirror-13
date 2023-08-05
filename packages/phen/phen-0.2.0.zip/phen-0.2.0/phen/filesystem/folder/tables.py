# -*- coding:utf-8 -*-

"""
    Table of files accessible by a group.
"""

import json
import zlib
import logging
from six import BytesIO
from base64 import b64decode as b64d, b64encode as b64e

from phen.crypto import sym, random_iv

from .filemeta import fm_json_load


log = logging.getLogger(__name__)


class Table(object):
    """
        Table of files accessible by a group.
    """
    def __init__(self):
        """
            Create a new table.
        """
        self.group_id = u'public'
        self.ivec = b'public'
        self.secret = None
        self.signature = ""
        self.key = None
        self.content_key = None
        self.inner_ivec = None
        self.auth_key = None
        self.by_fid = {}  # just an alias, never saved
        self.contents = {}
        self.deletions = {}

    def load(self, ivec, code, group_mgr):
        """
            Load a previously saved table.
        """
        code, self.signature = code
        self.ivec = ivec
        if ivec == b'public':
            self.group_id = u'public'
            self.contents, self.deletions = code
            # note: the following assumes `code` has been loaded
            # from a json, substituting the filemeta dicts by
            # actual Metadata objects (using fm_json_load)
            for name in self.contents:
                self.contents[name].name = name
            self.by_fid = {fmeta.fid: fmeta
                           for fmeta in self.contents.values()}
        elif not self.find_group(code, self.ivec, group_mgr):
            self.group_id = 'secret'
            self.secret = code

    def set_group(self, group_id, group_mgr):
        """
            Prepare the table for group use.
        """
        if self.saveable():
            raise ValueError("Cannot change a non-empty table's group")
        self.group_id = group_id
        if group_id == u'public':
            self.key = None
            self.content_key = None
            self.ivec = b'public'
        else:
            self.key = group_mgr.get_key(group_id)
            self.content_key = random_iv(False)
            self.inner_ivec = None
            self.ivec = random_iv()
        return self.ivec

    def find_group(self, code, ivec, group_mgr):
        """
            Iterate over known groups to find the apropriate key.
        """
        if not group_mgr:
            return False
        code = b64d(code.encode("ascii"))
        group_id = group_mgr.get_id_by_ivec(ivec)
        if group_id:
            if self.decode(group_id, group_mgr, code, ivec):
                return True
        for group_id in group_mgr:
            if self.decode(group_id, group_mgr, code, ivec):
                group_mgr.set_ivec(ivec, group_id)
                return True
        return False

    def decode(self, group_id, group_mgr, code, ivec):
        """
            Try to decrypt the file table.
        """
        key = group_mgr.get_key(group_id)
        if key is None:
            return False
        dec = sym.Decryptor(BytesIO(code[:32]), key, ivec)
        if dec.read(16) != b"phen-files-table":
            return False
        self.content_key = dec.read(16)
        self.inner_ivec = code[32:48]
        dec = sym.Decryptor(
            BytesIO(code[48:]), self.content_key, self.inner_ivec, False
        )
        code = zlib.decompress(dec.read()).decode("utf8")
        try:
            decoded = json.loads(code, object_hook=fm_json_load)
        except ValueError:
            return False
        self.contents, self.deletions = decoded
        for name in self.contents:
            self.contents[name].name = name
        self.by_fid = {fmeta.fid: fmeta for fmeta in self.contents.values()}
        self.group_id = group_id
        self.key = key
        return True

    def encode(self, enc=True):
        """
            Encode a representation of the contents for storage.
            In case the table is:
                - public: return directly the contents and deletions objects;
                - secret: the unmodified data;
                - group accessible: same as public, but as encrypted string;
        """
        if self.secret:
            return [self.secret, self.signature]
        dicts = (fmeta.to_dict() for fmeta in self.contents.values())
        contents = {f.pop("name"): f for f in dicts}
        stru = [contents, self.deletions]
        if not self.key or not enc:
            return [stru, self.signature]
        # note: json must be in canonical form for posterior signing
        canon_stru = json.dumps(stru, sort_keys=True, separators=(',', ':'))
        compressed = zlib.compress(canon_stru.encode("utf8"), 9)
        # the set (key, ivec, header) must never change
        header = b"phen-files-table" + self.content_key
        header_c = sym.encrypt(header, self.key, self.ivec)[:32]
        # the inner_ivec must always change if the data changes
        if self.inner_ivec is None:
            self.inner_ivec = random_iv(False)
        data_c = sym.encrypt(
            compressed, self.content_key, self.inner_ivec, False
        )
        ciphered = b"".join((header_c, self.inner_ivec, data_c))
        encoded = b64e(ciphered).decode("utf8")
        if self.auth_key:
            self.signature = self.auth_key.sign(encoded)
        return [encoded, self.signature]

    def contains(self, table, ignore_fids):
        """
            Determine if this table has all the information of other table.
        """
        ofids = set(table.by_fid.keys()) - ignore_fids
        if not set(self.by_fid.keys()).issuperset(ofids):
            return False
        ofids = set(table.deletions.keys()) - ignore_fids
        return set(self.deletions.keys()).issuperset(ofids)

    def join(self, table):
        self.inner_ivec = None
        for fid in table.by_fid:
            fmeta = table.by_fid[fid]
            if fid not in self.by_fid or self.by_fid[fid].mtime < fmeta.mtime:
                self.by_fid[fid] = fmeta = table.by_fid[fid]
                self.contents[fmeta.name] = fmeta
        for fid, timestamp in table.deletions.items():
            if fid not in self.deletions or self.deletions[fid] < timestamp:
                self.deletions[fid] = timestamp

    def add_file(self, fmeta):
        """
            Add the file to the table.
        """
        self.inner_ivec = None
        if fmeta.name in self.contents:
            # the following requires no changes be made
            # in a metadata object after inclusion
            self.by_fid.pop(self.contents[fmeta.name].fid)
        self.contents[fmeta.name] = fmeta
        self.by_fid[fmeta.fid] = fmeta

    def update_file(self, fmeta):
        """
            Update the metadata if the file is in the table.
        """
        self.inner_ivec = None
        if fmeta.name in self.contents:
            self.by_fid.pop(self.contents[fmeta.name].fid)
            self.contents[fmeta.name] = fmeta
            self.by_fid[fmeta.fid] = fmeta

    def delete_file(self, fmeta, timestamp, fid=None):
        """
            Remove the file from the table, if included, and
            add the entry to the deletion dict if timestamp > 0.
        """
        self.inner_ivec = None
        if fid:
            fmeta = self.by_fid[fid]
        if fmeta.fid in self.by_fid:
            self.by_fid.pop(fmeta.fid)
            self.contents.pop(fmeta.name)
        elif fmeta.fid is None:
            fmeta = self.contents.pop(fmeta.name, None)
            fmeta and self.by_fid.pop(fmeta.fid)
        if timestamp and fmeta:
            self.deletions[fmeta.fid] = timestamp

    def remove_deletion(self, fid):
        """
            Remove a deletion if currently included.
        """
        self.inner_ivec = None
        if fid in self.deletions:
            self.deletions.pop(fid)
            return True

    def saveable(self):
        """
            Return true if there is any relevant information to be saved.
        """
        return self.secret or self.contents or self.deletions
