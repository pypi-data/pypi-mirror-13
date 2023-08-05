# !/usr/bin/env python

import six
import errno
import weakref

from .folder import Folder
from .dsave import DelayedSave

from phen import plugin_cfg
from phen.cache import Cache
from phen.util import fill_io_error, is_idhash


def path_parser(path, curdir=u''):
    """
        Expand ancestry references into an absolute path.
        Do not try to verify the existence of intermediate folders.
    """
    parts = path.rstrip(u"/").split(u"/")
    if not parts[0]:
        cparts = []
        parts.pop(0)
    else:
        cparts = curdir.split(u"/") if curdir != u"/" else []
    for part in parts:
        if not part or part == u".":
            continue
        if part.count(u".") == len(part):
            cparts = cparts[:1 - len(part)]
        else:
            cparts.append(part)
    return u"/".join(cparts)


class FilemetaCache:
    is_folder = False

    def __init__(self, fmeta, folder, multi=None):
        self.fmeta = fmeta
        self.folder = folder
        self.multi = multi
        self.multi_id = ''
        self.serial = folder.cache_serial

    def __repr__(self):
        return "<=%s=%i=%s=>" % (
            str(self.fmeta), self.serial, '*' if self.multi else '-'
        )

    @property
    def exists(self):
        return not self.fmeta.is_invalid()

    @property
    def is_multi(self):
        return self.multi is not None

    @property
    def expired(self):
        return self.serial != self.folder.cache_serial


class Traverser(object):
    """
        Class for loading, caching, and traversing folders.
    """
    def __init__(self):
        """
            Initialize the cache.
        """
        size = plugin_cfg("phen", "fs-cache", 1 << 8)
        self.cache = Cache(size, None)
        self.fmeta_cache = Cache(size, None)
        self.traverse_cache = weakref.WeakValueDictionary()
        self.dsave = DelayedSave()
        self.curdir = ''

    def open_folder(self, fid_pair, path, key, parent=None):
        """
            Return the specified folder, opening it if necessary.
        """
        if fid_pair not in self.cache:
            if key is None and fid_pair[1] != "root":
                ctx = getattr(self, "cid", None)
                if ctx is None:
                    return None
                idhash = ctx.cidhash
                from phen import storage
                l_fid = storage.store.local_data_fid(fid_pair, idhash, "key")
                if not storage.store.is_available(l_fid):
                    return None
                try:
                    with storage.store.load(l_fid, ctx.cid) as infile:
                        import json
                        path, key = json.load(infile)
                except IOError:
                    return None
            folder = Folder.load(self, fid_pair, path, parent, key)
            self.cache.add(folder.fid_pair, folder)
        else:
            folder = self.cache.get(fid_pair)
            if folder.path is None:
                # instantiated by sync
                folder.path = path
        assert folder.opened_by == self.ctx.cidhash
        return folder

    def add_to_folder_cache(self, folder):
        """
            Add a just created folder to the cache.
        """
        return self.cache.add(folder.fid_pair, folder)

    def flush_cache(self):
        """
            Clear the cache.
        """
        self.cache.clear()
        self.fmeta_cache.clear()
        self.traverse_cache.clear()

    def flush(self):
        """
            Save pending write operations then clear the cache.
        """
        self.dsave.flush()
        self.flush_cache()

    def startup(self):
        self.dsave.start()

    def shutdown(self):
        self.dsave.shutdown()
        self.flush_cache()

    def update_cache_item(self, path, idhash=None, fmeta=None, folder=None):
        if fmeta is None:
            # must remove the entire folder hierarchy... perhaps it
            # would be better to have a hierarchical cache - TODO
            for key in list(self.traverse_cache):
                if key.startswith(path):
                    self.traverse_cache.pop(key)
            return
        if (idhash, fmeta.fid) in self.fmeta_cache:
            fitem = self.fmeta_cache[(idhash, fmeta.fid)]
            fitem.fmeta = fmeta
            fitem.folder = folder
            fitem.multi = None
            fitem.serial = folder.cache_serial
        else:
            fitem = None
        if path in self.traverse_cache:
            item = self.traverse_cache[path]
            if not item.is_folder and item is not fitem:
                item.fmeta = fmeta
                item.folder = folder
                item.multi = None
                item.serial = folder.cache_serial
        elif fmeta.is_file():
            if not fitem:
                fitem = FilemetaCache(fmeta, folder)
            self.traverse_cache[path] = fitem

    def abspath(self, path):
        """
            Expand the possibly relative path to an absolute one,
            **without the leading slash**.
        """
        if not isinstance(path, six.text_type):
            raise TypeError("Paths must be text, not {}"
                            .format(path.__class__.__name__))
        if not path:
            return path
        path = path_parser(path, self.curdir)
        return path.lstrip("/")

    def subpath(self, *p, **kw):
        subp = [""] + list(p)
        rid = kw.get("rid")
        while rid:
            import random
            random_id = hex(random.getrandbits(64))[2:]
            fname = "/".join(subp + [random_id])
            if not self.exists(fname):  # operations dependency
                return fname
        return "/".join(subp)

    def traverse_recursive(self, path, parts, traversed, levels):
        part = parts.pop(-1)
        retv = self.traverse_cache.get(path)
        if retv is not None and not retv.is_folder and retv.expired:
            retv = None
        if retv is not None:
            if levels:  # required number of levels not reached
                if not parts:
                    raise fill_io_error(errno.EPERM, '')
                self.traverse_recursive("/".join(parts), parts,
                                        traversed, levels - 1)
            traversed.append(retv)
            return retv
        # check if we reached the root
        if not len(parts):
            idhash = part
            if not is_idhash(idhash):
                raise fill_io_error(errno.EPERM, '', idhash)
            folder = self.open_folder((idhash, "root"), idhash, None)
            self.traverse_cache[path] = folder
            traversed.append(folder)
            return folder
        # nopz, we must get the parent
        parent = self.traverse_recursive("/".join(parts), parts[:],
                                         traversed, levels and (levels - 1))
        if isinstance(parent, Folder):
            fmeta = parent.filemeta(part, no_error=True)
            fid_pair = parent.idhash, fmeta.fid
            if fmeta.is_folder():
                retv = self.open_folder(fid_pair, path, fmeta.key, parent)
            else:
                if fid_pair in self.fmeta_cache:
                    retv = self.fmeta_cache[fid_pair]
                    if retv.expired:
                        retv = None
                if retv is None:
                    if not fmeta.is_multi():
                        retv = FilemetaCache(fmeta, parent)
                    else:
                        retv = FilemetaCache(fmeta, parent, fmeta)
                    if fmeta.fid is not None:
                        # new / non-existing files must not be cached
                        self.fmeta_cache[fid_pair] = retv
            if fmeta.fid is not None:
                self.traverse_cache[path] = retv
            traversed.append(retv)
            return retv
        else:
            multi_attempt = is_idhash(part)
            if multi_attempt or parent.is_multi:
                p_part = parts.pop(-1)
                if len(traversed) > 1:
                    granpa = traversed[-2]
                else:
                    granpa = self.traverse_recursive("/".join(parts), parts,
                                                     [], 0)
                    traversed.insert(0, granpa)
                fmeta = granpa.filemeta(part, p_part, no_error=True)
                fid = (fmeta.fid or "/////") + (parent.fmeta.fid or "/////")
                fid_pair = granpa.idhash, fid
                if fid_pair in self.fmeta_cache:
                    retv = self.fmeta_cache[fid_pair]
                    if retv.expired:
                        retv = None
                if retv is None:
                    retv = FilemetaCache(fmeta, granpa, parent)
                    retv.multi_id = part
                    if fmeta.fid is not None:
                        self.fmeta_cache[fid_pair] = retv
                if fmeta.fid is not None:
                    self.traverse_cache[path] = retv
                traversed.append(retv)
                return retv
            if parent.exists:
                raise fill_io_error(errno.ENOTDIR, path)
        raise fill_io_error(errno.ENOENT, "/".join(parts))

    def traverse(self, path, levels=0, absolute=False):
        """
            Walk through the folder hierarchy.
        """
        if not path:
            raise fill_io_error(errno.EINVAL)
        if not absolute:
            path = self.abspath(path)
        parts = path.split("/")
        if not parts:
            raise fill_io_error(errno.EINVAL)
        traversed = []
        self.traverse_recursive("/".join(parts), parts, traversed, levels)
        return traversed, path
