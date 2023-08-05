# -*- coding:utf-8 -*-

"""
    Objects to manage folder contents.
"""

import json
import logging

from .filemeta import fm_json_load
from .authorcontents import AuthorContents


log = logging.getLogger(__name__)


class Contents(object):
    """
        Collection of contents from all authors.
    """
    def __init__(self):
        self.file_dict = {}
        self.deletion_dict = {}
        self._fid_dict = {}  # note: includes deleted fids
        self.contents = {}
        from ..access import AccessControl
        self.access_control = AccessControl(self)

    def rescan_tables(self, group_mgr):
        updated = any(content.rescan_tables(group_mgr)
                      for author, content in self.all_contents())
        if updated:
            self.build_listing()
            return True

    def from_dict(self, json_s, folder_fid, group_mgr, pkgetter=None):
        """
            Load the data from the json structure.
            Return whether all contents were accepted.
        """
        assert len(folder_fid) in (47, 86)  # 43 + 'root' or fid
        self.contents = {}
        retv = True
        for author in json_s["contents"]:
            self.contents[author] = contents = []
            for json_contents in json_s["contents"][author]:
                acontents = AuthorContents(author)
                acontents.load(json_contents, group_mgr)
                if pkgetter and not acontents.verify(pkgetter, folder_fid):
                    log.warn("invalid author contents: " + folder_fid)
                    retv = False
                else:
                    contents.append(acontents)
        self.build_listing()
        return retv

    def to_dict(self, identity, folder_fid):
        """
            Generate the structure for encoding in json.
        """
        partial = {author: [contents.to_signed_dict(identity, folder_fid)
                            for contents in self.contents[author]
                            if contents.saveable()]
                   for author in self.contents}
        stru = {"contents": {author: contents
                             for author, contents in partial.items()
                             if contents}}
        return stru

    def clone(self, identity, folder_fid, group_mgr):
        """
            Return a copy of the folder.
        """
        retv = Contents()
        stru = self.to_dict(identity, folder_fid)
        tjson = json.dumps(stru, sort_keys=True,
                           indent=4, separators=(',', ': '))
        retv.from_dict(json.loads(tjson, object_hook=fm_json_load),
                       folder_fid, group_mgr)
        return retv

    def dump(self):
        """
            Dump the unencoded structure - helper method for debugging.
        """
        stru = {author: [contents.to_dict(False, True)
                         for contents in self.contents[author]
                         if contents.saveable()]
                for author in self.contents}
        retv = json.dumps(stru, sort_keys=True,
                          indent=4, separators=(',', ': '))
        return retv

    def all_contents(self, author=None):
        """
            Iterate over all contents from one or all authors.
        """
        if self.contents is None:
            state = "closed" if getattr(self, "is_closed", False) else "open"
            msg = u"Folder {} is {}".format(self, state).encode("utf8")
            raise RuntimeError(msg)
        if author:
            if author not in self.contents:
                return
            for contents in self.contents[author]:
                yield author, contents
            return
        for author in self.contents:
            for contents in self.contents[author]:
                yield author, contents

    def author_contents(self, author_id, create=True):
        """
            Return the author's contents object, creating it
            if none is currently in the folder.
        """
        if author_id.hash not in self.contents:
            if not create:
                return False
            self.contents[author_id.hash] = [AuthorContents(author_id.hash)]
        return self.contents[author_id.hash][0]

    def build_listing(self):
        """
            Create the initial unified file and deletion dicts.
        """
        self.file_dict = {}
        self.deletion_dict = {}
        self._fid_dict = {}
        for author, contents in self.all_contents():
            contents.fill_deletion_dict(self.deletion_dict)
        for author, contents in self.all_contents():
            contents.fill_dicts(self._fid_dict, self.file_dict,
                                self.deletion_dict)

    def _deletion_authors(self, fid):
        return fid in self.deletion_dict and self.deletion_dict[fid][1]

    def add_file(self, author_id, fmeta, group_ids, group_mgr):
        """
            Add or update a file to the folder.
        """
        self.access_control.check(author_id, True, fmeta)
        self._fid_dict[fmeta.fid] = (fmeta, author_id.hash)
        contents = self.author_contents(author_id)
        contents.add_file(fmeta, group_ids, group_mgr)
        entry = self.file_dict.setdefault(fmeta.name, {})
        entry[author_id.hash] = fmeta
        if fmeta.name == ".access":
            self.access_control.invalidate()

    def delete_file(self, author_id, fmeta, timestamp, group_ids, group_mgr):
        """
            Remove the file from the specified groups, or from
            the folder altogether, and optionally add it to the
            the author's deletion dicts (when timestamp > 0).
        """
        self.access_control.check(author_id, False, fmeta)
        contents = self.author_contents(author_id)
        # if removing from folder we must get all known groups.
        # todo: solution for the case where a file is also included
        # in a secret table... probably the user shouldn't have had the
        # permission to remove the file in the first place...
        if timestamp or not group_ids:
            group_ids = self.get_groups(fmeta)
        contents.delete_file(fmeta, timestamp, group_ids, group_mgr)
#        if not group_ids and timestamp > 0:
#            self.file_dict.pop(fmeta.name)
#            if fmeta.fid in self.deletion_dict:
#                self.deletion_dict[fmeta.fid][0] = timestamp
#                self.deletion_dict[fmeta.fid][1].append(author_id.hash)
#            else:
#                self.deletion_dict[fmeta.fid] = [timestamp, [author_id.hash]]
#        else:
#            self.build_listing()
        # todo: smarter way to update the dicts (above is incomplete)
        self.build_listing()

    def commit(self, author_id, folder_fid, oldest_sync=None):
        """
            Sign any changes authored by the identity.
        """
        for author, contents in self.all_contents(author_id.hash):
            contents.commit(author_id, folder_fid, oldest_sync)

    def search_contents(self, author, rcontents):
        """Check if we have the exact remote content."""
        for a, lcontents in self.all_contents(author):
            if lcontents.signature == rcontents.signature:
                return True
        return False

    def replay(self, author, fids, files, deletions):
        """Assert there is no access control infringements."""
        for fmetas in files.values():
            fmeta = fmetas[author]
            try:
                self.access_control.check(author, True, fmeta)
            except IOError:
                return False
        for fid in deletions:
            try:
                if fid in self._fid_dict:
                    # file may have already been deleted, but let's check
                    self.access_control.check(author, False,
                                              self._fid_dict[fid][0])
                else:
                    # we don't know the file, assume it is ok to delete it
                    continue
#                    self.access_control.check(author, False, fid=fid)
            except IOError:
                return False
        return True

    def join(self, author_id):
        """Join any additional contents the author might have received.

        Return indication of need to commit.
        """
        idhash = author_id.hash
        if idhash not in self.contents or len(self.contents[idhash]) < 2:
            return False
        self.contents[idhash][0].join(self.contents[idhash][1:])
        self.contents[idhash] = self.contents[idhash][:1]
        return True

    def sync(self, author_id, folder_fid, remote, group_mgr, oldest_sync=None):
        """Incorporate all valid (permitted) operations of a remote folder.

        Note: AuthorContents objects from the remote folder are
        directly used (we're assuming the remote is a disposable object).
        Return the set of rejected and accepted files and deletions.
        """
        a_file, a_deletions = set(), {}
        r_file, r_deletions = set(), set()
        if __debug__:
            if hasattr(remote, "idhash"):
                log.debug("sync start {0.idhash}/{0.fid}".format(remote))
            else:
                log.debug("sync start [remote is plain Contents]")
        last_syncs = {author: min(contents.oldest_sync
                                  for a, contents in self.all_contents(author))
                      for author in self.contents}
        for author, rcontents in remote.all_contents():
            __debug__ and log.debug("analyzing contents from author '{}'"
                                    .format(author))
            if not self.access_control.allow_secret_tables():
                if any(t.secret for t in rcontents.all_tables):
                    __debug__ and log.debug("- secret files not permitted")
                    continue
            if not rcontents.signature:
                __debug__ and log.debug("- contents not signed")
                continue
            if self.search_contents(author, rcontents):
                __debug__ and log.debug("+ signature match - no sync needed")
                continue
            fids, files, deletions = {}, {}, {}
            rcontents.fill_deletion_dict(deletions)
            rcontents.fill_dicts(fids, files, deletions)
            if author == author_id.hash:
                replay_ok = True
            else:
                replay_ok = self.replay(author, fids, files, deletions)
            if __debug__:
                log.debug("* deleted files/folders:")
                for fid in deletions:
                    log.debug("  * " + fid)
            if not replay_ok:
                r_file.update(fids.keys())
                r_deletions.update(deletions.keys())
                # todo: collect statistics
                break
            for fmeta, fauthor in list(fids.values()):
                if fmeta.fid in self._fid_dict:
                    if (fmeta.fid in self.deletion_dict or
                            self._fid_dict[fmeta.fid][0].mtime >= fmeta.mtime):
                        fids.pop(fmeta.fid)
                        continue
                if fauthor in last_syncs and fmeta.mtime < last_syncs[fauthor]:
                    log.debug("- found new entry older than last sync:")
                    log.debug(u"  - {0.fid} {0.name}: {0.mtime} <= {1}"
                              .format(fmeta, last_syncs[fauthor]))
                    log.debug("- contents ignored")
                    fids = None
                    break
            if fids is None:
                continue
            a_file.update(fids.keys())
            # update the deletion dict with the most
            # recent deletion of all deleted fids
            for fid in deletions:
                is_latest = (
                    fid not in a_deletions or
                    a_deletions[fid][0] < deletions[fid][0]
                )
                if is_latest:
                    a_deletions[fid] = deletions[fid]
            if author not in self.contents:
                self.contents[author] = []
            self.contents[author].append(rcontents)
        if __debug__:
            log.debug("accepted additions:")
            for fid in a_file:
                log.debug("* " + fid)
            log.debug("accepted deletions:")
            for fid in a_deletions:
                log.debug("* " + fid)
            log.debug("rejected additions:")
            for fid in r_file:
                log.debug("* " + fid)
            log.debug("rejected deletions:")
            for fid in r_deletions:
                log.debug("* " + fid)
        if a_file or a_deletions:
            self.analyze_new_contents(author_id, a_file, a_deletions,
                                      folder_fid, oldest_sync, group_mgr)
        return a_file, set(a_deletions), r_file, r_deletions

    def remove_reduntant_contents(self):
        ignore_fids = set(self.deletion_dict.keys())
        need_rebuild = False
        for author in self.contents:
            for contents in self.contents[author][::-1]:
                if not contents.author:
                    continue
                for oth_cont in self.contents[author]:
                    if oth_cont == contents or not oth_cont.author:
                        continue
                    if contents.contains(oth_cont, ignore_fids):
                        oth_cont.author = None
                        need_rebuild = True
            for contents in self.contents[author][:]:
                if not contents.author:
                    self.contents[author].remove(contents)
        return need_rebuild

    def analyze_new_contents(self, author_id, a_file, a_deletions,
                             folder_fid, oldest_sync, group_mgr):
        self.build_listing()
        if self.remove_reduntant_contents():
            self.build_listing()
        need_commit = self.join(author_id)
        contents = self.author_contents(author_id, False)
        if contents:
            # remote acknowledgements
            acks = (
                fid for fid in self.deletion_dict
                if fid not in self._fid_dict and
                author_id.hash in self.deletion_dict[fid][1]
            )
            if acks:
                __debug__ and log.debug("author acknowledged our deletion of:")
                for fid in acks:
                    __debug__ and log.debug("* " + fid)
                    contents.remove_deletion(fid)
                    self.deletion_dict[fid][1].remove(author_id.hash)
            # acknowledging remote deletions
            acks = {
                fid: a_deletions[fid][0] for fid in a_deletions
                if fid in self._fid_dict and
                author_id.hash == self._fid_dict[fid][1]
            }
            if acks:
                __debug__ and log.debug("we acknowledge the deletion of:")
                for fid in acks:
                    __debug__ and log.debug("* " + fid)
                contents = self.author_contents(author_id)
                contents.acknowledge_deletions(acks, self.deletion_dict,
                                               group_mgr)
            need_commit |= contents.signature is None
        a_file.difference_update(self.deletion_dict.keys())
        if need_commit:
            __debug__ and log.debug("commiting changes")
            self.commit(author_id, folder_fid, oldest_sync)
        else:
            __debug__ and log.debug("no commit needed")

    def get_filemeta(self, fname=None, author=None, fid=None, deleted=False):
        """
            Retrieve the file metadata associated with the name and author.
        """
        if fid is not None:
            if fid not in self._fid_dict:
                raise LookupError("File is not in this folder")
            if not deleted and fid in self.deletion_dict:
                raise LookupError("File has been deleted from this folder")
            return self._fid_dict[fid][0]
        if fname in self.file_dict:
            if not author:
                if len(self.file_dict[fname]) > 1:
                    raise TypeError("File is multientry and "
                                    "no author was specified")
                return list(self.file_dict[fname].values())[0]
            if author not in self.file_dict[fname]:
                raise LookupError("File was not written "
                                  "by the specified author")
            return self.file_dict[fname][author]
        raise LookupError("File is not in this folder")

    def get_authors(self, fname):
        """
            Return the list of authors of the (possibly) multientry.
        """
        if fname in self.file_dict:
            return list(self.file_dict[fname].keys())
        raise LookupError("File is not in this folder")

    def get_author(self, fid, deleted=False):
        """
            Return the file's author.
        """
        if fid not in self._fid_dict:
            raise LookupError("File is not in this folder")
        if not deleted and fid in self.deletion_dict:
            raise LookupError("File has been deleted from this folder")
        return self._fid_dict[fid][1]

    def get_groups(self, fmeta):
        """
            Return the set of all groups that can access the file.
        """
        groups = set()
        for contents in self.contents[self.get_author(fmeta.fid)]:
            groups.update(contents.get_groups(fmeta))
        return groups
