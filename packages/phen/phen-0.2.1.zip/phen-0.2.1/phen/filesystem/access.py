# -*- coding:utf-8 -*-

"""File System Access Control

Authorization is granted through the .access file, that only the
folder's author can create.

todo: allow other people to change configurations, by adding
an "include" section in the file.

"""

import errno

from six.moves import configparser

from phen.crypto import asym
from .fileacc import FileAccessor


def no_op():
    return 0


class AccessControl:
    def __init__(self, parent):
        self.folder = parent
        self.key_cache = {}

    def load_configuration(self, filename=u".access"):
        self.config = configparser.ConfigParser()
        if filename in self.folder.file_dict:
            authors = self.folder.file_dict[filename]
            if self.folder.metadata["author"] not in authors:
                raise IOError(errno.EPERM)
            fmeta = authors[self.folder.metadata["author"]]
            try:
                cfg_file = FileAccessor(self.folder, fmeta, 'r',
                                        self.folder.metadata["author"])
            except IOError as exc:
                if exc.args[0] == errno.EAGAIN:
                    del self.config
                    return
                raise
            cfg_file.seek(0)
            with cfg_file:
                try:
                    from six import StringIO
                    cfg_contents = cfg_file.read().decode("utf8")
                    self.config.readfp(StringIO(cfg_contents))
                except Exception:
                    from traceback import print_exc
                    print_exc()
                    pass

    def invalidate(self):
        if hasattr(self, "config"):
            del self.config

    def allow_secret_tables(self):
        # allow signed tables
        return True

    def check_restrictions(self, author, fmeta, section):
        try:
            file_size = self.config.getint(section, "file_size")
            if file_size < fmeta.size:
                return False
        except configparser.NoOptionError:
            pass
        fid_dict, file_dict, deletion_dict = {}, {}, {}

        def perform():
            for a, contents in self.folder.all_contents(author):
                contents.fill_dicts(fid_dict, file_dict, deletion_dict)
                # note: fid_dict includes deleted files
                # todo: check fid_dict references below

        try:
            file_count = self.config.getint(section, "file_count")
            perform()
            perform = no_op
            if file_count == len(fid_dict):
                # must not add anything else
                return False
        except configparser.NoOptionError:
            pass
        try:
            total_size = self.config.getint(section, "total_size")
        except configparser.NoOptionError:
            total_size = 0
        if total_size:
            perform()
            perform = no_op
            current_total = sum(entry[0].size for entry in fid_dict.values())
            if current_total >= total_size:
                return False
            try:
                total_grace = self.config.getint(section, "total_grace")
            except configparser.NoOptionError:
                total_grace = 0
            if fmeta.size + current_total > total_size + total_grace:
                return False
        return True

    def check(self, author, add, fmeta):
        if not hasattr(self.folder, "metadata"):
            # folder is a plain FolderContents, instead of Folder
            return True
        if not hasattr(self, "config"):
            self.load_configuration()
        if hasattr(author, "hash"):
            author = author.hash
        if self.folder.metadata["author"] == author:
            if not hasattr(self, "config"):
                return True
            if not self.config.has_section("author"):
                # author can do anything
                return True
            # unless ve has revoked vis own access
            try:
                if not self.config.getboolean("author", "self_revoke"):
                    return True
            except configparser.NoOptionError:
                return True
            # if self-revoked, ve may fall in other categories
        if not hasattr(self, "config"):
            return False
        if add:
            op = 'mkdir' if fmeta.is_folder() else 'add'
        else:
            op = 'rmdir' if fmeta.is_folder() else 'del'
        for section in self.config.sections():
            if section == "author":
                continue
            try:
                key = self.config.get(section, op)
            except configparser.NoOptionError:
                continue
            if key == u'public':
                if self.check_restrictions(author, fmeta, section):
                    return True
            if key not in self.key_cache:
                try:
                    self.key_cache[key] = asym.PublicKey.load_data(key)
                except configparser.NoOptionError:
                    self.key_cache[key] = None
            if self.key_cache[key]:
                # is ve authorized?
                if self.key_cache[key].verify(fmeta.fid, fmeta.auth):
                    # yep, let's check if file is within restrictions
                    if self.check_restrictions(author, fmeta, section):
                        return True
                    # nopz, but perhaps another section is less restrictive
                # nopz, better luck next time
#        from StringIO import StringIO
#        out = StringIO()
#        self.config.write(out)
#        print out.getvalue()
        raise IOError(errno.EPERM)
