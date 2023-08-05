# -*- coding:utf-8 -*-

"""
    Objects to manage contents from one author in the folder.
"""

import json

from .tables import Table


class AuthorContents:
    """
        Collection of all file tables in the folder from one author.
    """
    def __init__(self, author):
        self.author = author
        self.oldest_sync = 0
        self.signature = None
        self.tables = {}
        self.all_tables = []

    def load(self, json_s, group_mgr):
        """
            Load the previously saved contents.
        """
        self.signature = json_s["signature"]
        self.oldest_sync = json_s["oldest_sync"]
        for ivec, code in json_s["tables"].items():
            table = Table()
            table.load(ivec.encode("utf8"), code, group_mgr)
            self.all_tables.append(table)
            if table.group_id != 'secret':
                self.tables[table.group_id] = table

    def rescan_tables(self, group_mgr):
        retv = False
        for table in self.all_tables:
            if table.group_id != 'secret':
                continue
            table.load(table.ivec, (table.secret, table.signature), group_mgr)
            if table.group_id != 'secret':
                self.tables[table.group_id] = table
                retv = True
        return retv

    def get_groups(self, fmeta):
        """
            Return the list of group identifiers that
            we know can access the file.
        """
        return [gid for gid in self.tables
                if fmeta.name in self.tables[gid].contents]

    def saveable(self):
        """
            Tell if the manifest has any saveable file.
        """
        return any(table.saveable() for table in self.all_tables)

    def get_table(self, group_id, group_mgr):
        """
            Return the table of the specified group, creating
            one if currently there is none.
        """
        if group_id in self.tables:
            return self.tables[group_id]
        table = Table()
        table.set_group(group_id, group_mgr)
        self.tables[group_id] = table
        self.all_tables.append(table)
        return table

    def add_file(self, fmeta, group_ids, group_mgr):
        """
            Add or update the file.
        """
        if not len(group_ids):
            raise ValueError("No group ID informed")
        for group_id in group_ids:
            table = self.get_table(group_id, group_mgr)
            # add the file
            table.add_file(fmeta)
        # update all previously existing
        for table in self.tables.values():
            table.update_file(fmeta)
        self.signature = None

    def delete_file(self, fmeta, timestamp, group_ids, group_mgr):
        """
            Remove the file from all tables and add to their
            deletion dicts.
        """
        for group_id in group_ids:
            table = self.get_table(group_id, group_mgr)
            table.delete_file(fmeta, timestamp)
        self.signature = None

    def remove_deletion(self, fid, group_ids=None):
        """
            Remove the file identifier from all deletion dicts.
        """
        for group_id, table in self.tables.items():
            if group_ids and group_id not in group_ids:
                continue
            if table.remove_deletion(fid):
                self.signature = None

    def to_dict(self, enc, inc_sign=False):
        """
            Return a dictionary representation proper for json.
        """
        retv = {"oldest_sync": self.oldest_sync,
                "tables": {table.ivec.decode("utf8"): table.encode(enc)
                           for table in self.all_tables}}
        if inc_sign:
            retv["signature"] = self.signature
        return retv

    def to_signed_dict(self, identity, folder_fid):
        """
            Return the signed structure for json.
        """
        retv = self.to_dict(True)
        if not self.signature:
            if self.author != identity.hash:
                raise ValueError("Attempting to sign with wrong identity")
            to_sign = json.dumps(retv, sort_keys=True, separators=(',', ':'))
            to_sign += folder_fid
            data = to_sign.encode('utf8')
            self.signature = identity.sign(data)
        retv["signature"] = self.signature
        return retv

    def commit(self, identity, folder_fid, oldest_sync):
        """
            Make sure all changes are signed.
        """
        if oldest_sync:
            self.oldest_sync = oldest_sync
        if not self.signature:
            self.to_signed_dict(identity, folder_fid)

    def verify(self, pkgetter, folder_fid):
        """
            Check if the signature is valid.
        """
        try:
            pubkey = pkgetter(self.author)
        except IOError:
            raise LookupError("Unknown identity - cannot verify data")
        stru = self.to_dict(True)
        signed = json.dumps(stru, sort_keys=True, separators=(',', ':'),
                            default=lambda o: o.to_dict())
        signed += folder_fid
        data = signed.encode('utf8')
        return pubkey.verify(data, self.signature)

    def get_files(self):
        """
            Iterates over every file in every readable table,
            therefore possibly yielding the same item multiple times.
        """
        for table in self.tables.values():
            for fmeta in table.contents.values():
                yield fmeta

    def fill_deletion_dict(self, deletion_dict):
        """
            Retrieve all visible deletions with their timestamps.
        """
        for table in self.tables.values():
            for fid in table.deletions:
                timestamp = table.deletions[fid]
                if fid not in deletion_dict:
                    deletion_dict[fid] = [timestamp, [self.author]]
                    continue
                if self.author not in deletion_dict[fid][1]:
                    deletion_dict[fid][1].append(self.author)
                if deletion_dict[fid][0] < timestamp:
                    deletion_dict[fid][0] = timestamp

    def fill_dicts(self, fid_dict, file_dict, deletion_dict):
        """
            Build a structure of metadata from all non-deleted files,
            indexed and subindexed by name and author (file_dict), and
            indexed by fid (fid_dict).
        """
        for fmeta in self.get_files():
            fid = fmeta.fid
            if fid not in fid_dict:
                # note: fid_dict includes deleted files
                fid_dict[fid] = (fmeta, self.author)
            if fid in deletion_dict and fmeta.mtime <= deletion_dict[fid][0]:
                continue
            entry = file_dict.setdefault(fmeta.name, {})
            entry[self.author] = fmeta

    def contains(self, contents, ignore_fids, ignore_secrets=False):
        """
            Verify if we have all contents of another object.
        """
        if not ignore_secrets:
            secrets = set(table.secret for table in self.all_tables
                          if table.secret)
        for table in contents.all_tables:
            if table.secret:
                if not ignore_secrets and table.secret not in secrets:
                    return False
                continue
            if table.group_id not in self.tables:
                return False
            ltable = self.tables[table.group_id]
            if not ltable.contains(table, ignore_fids):
                return False
        return True

    def join(self, contlist):
        """
            Incorporate the files and deletions of separate
            contents from the same author. The author's identity
            must be able to sign the modifications.
        """
        for contents in contlist:
            # we should be able to see all tables
            assert len(contents.tables) == len(contents.all_tables)
            for group_id in contents.tables:
                if group_id not in self.tables:
                    self.tables[group_id] = contents.tables.pop(group_id)
                    self.signature = None
                else:
                    if self.tables[group_id].join(contents.tables[group_id]):
                        self.signature = None
        if not self.signature:
            for fid, timestamp in self.deletion_dict.items():
                if fid not in self.fid_dict and timestamp < self.oldest_sync:
                    self.remove_deletion(fid)

    def acknowledge_deletions(self, acks, deletion_dict, group_mgr):
        """
            Replicate another author's deletions of our files.
        """
        for fid in acks:
            for table in self.tables.values():
                if fid in table.by_fid:
                    table.delete_file(None, acks[fid], fid=fid)
            if fid not in deletion_dict:
                deletion_dict[fid] = [acks[fid], []]
            if self.author not in deletion_dict[fid][1]:
                deletion_dict[fid][1].append(self.author)
        self.signature = None
