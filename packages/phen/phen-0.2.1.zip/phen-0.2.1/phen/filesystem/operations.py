# -*- coding:utf-8 -*-

"""
    File and folder manipulation operations.
"""

import re
import six
import json
import errno
import functools

from .folder import Metadata
from .folder import filemeta as fmtypes
from .traverse import Traverser
from .fileacc import FileAccessor, DirectFileAccessor

from phen.util import fill_io_error


def _filemeta(path, node, folder_size=False):
    """
        Retrieve the file metadata relative to the path.
    """
    parent = node.parent if node.is_folder else node.folder
    if parent is None:
        raise fill_io_error(errno.EPERM, path)
    if node.is_folder:
        fmeta = node.folder_fmeta
        if folder_size:
            from phen import storage
            fmeta = Metadata(fmeta)
            fmeta.size = storage.store.size((parent.idhash, fmeta.fid))
    elif not node.exists:
        raise fill_io_error(errno.ENOENT, path)
    else:
        fmeta = node.fmeta
    return fmeta


def _access(path, node, is_add=True, is_file=True):
    """
        Assess if the destination is writable/erasable.
    """
    parent = node.parent if node.is_folder else node.folder
    if parent is None:
        raise fill_io_error(errno.EPERM, path)
    fmeta = Metadata(type=fmtypes.FILE if is_file else fmtypes.FOLDER)
    if node.is_folder:
        folder = node
    elif node.type == fmtypes.INVALID:
        raise fill_io_error(errno.ENOENT, path)
    else:
        folder = node.folder
    try:
        folder.check_access(fmeta, is_add)
    except IOError:
        return False
    return True


def _author(path, node):
    """
        Retrieve the file's author.
    """
    parent = node.parent if node.is_folder else node.folder
    if parent is None:
        raise fill_io_error(errno.EPERM, path)
    if not node.exists:
        raise fill_io_error(errno.ENOENT, path)
    if node.is_folder:
        return parent.get_author(node.fid)
    fid = node.multi.fid if node.multi else node.fmeta.fid
    return node.folder.get_author(fid)


def _xattr(path, node, xattr_dict=None, update=False, check=True):
    """
        Change extended attributes.
    """
    if check:
        import json
        # ensure the data is encodable (raises TypeError)
        json.dumps(xattr_dict)
    if not node.exists:
        raise fill_io_error(errno.ENOENT, path)
    if node.is_folder:
        fmeta = node.folder_fmeta
        if not fmeta:
            raise fill_io_error(errno.EPERM, path)
        parent = node.parent
    else:
        fmeta = node.fmeta
        parent = node.folder
    if xattr_dict is not None:
        if update:
            fmeta.xattr.update(xattr_dict)
        else:
            fmeta.xattr = xattr_dict
        parent.add_file(fmeta)
    return fmeta.xattr


def _utime(path, node, dtime, mtime=None):
    """
        Change the file timestamps.
    """
    parent = node.parent if node.is_folder else node.folder
    if parent is None:
        raise fill_io_error(errno.EPERM, path)
    if not node.exists:
        raise fill_io_error(errno.ENOENT, path)
    if node.is_folder:
        fmeta = node.folder_fmeta
    else:
        fmeta = node.fmeta
    fmeta.dtime = dtime
    # this may mess up syncing... you better know what you're doing
    if mtime is not None:
        fmeta.mtime = mtime
    parent.add_file(fmeta, touch=mtime is None)


def _groups(path, node, gset=None, op='add'):
    """
        Retrieve or change the file's groups.
    """
    folder, fmeta = __groups_fmeta(path, node)
    retv = folder.get_groups(fmeta)
    if gset is not None:
        if isinstance(gset, six.text_type):
            gset = set((gset,))
        if op == 'add':
            if gset - retv:
                folder.add_file(fmeta, gset - retv)
                retv |= gset
        elif op == 'set':
            return __groups_set(folder, fmeta, gset, op, retv)
        elif op == 'del':
            if retv & gset:
                folder.delete_file(fmeta, retv & gset, bool(retv - gset))
            retv -= gset
    return retv


def __groups_fmeta(path, node):
    if not node.exists:
        raise fill_io_error(errno.ENOENT, path)
    if node.is_folder:
        folder = node.parent
        if not folder:  # root folder
            raise fill_io_error(errno.EPERM, path)
        fmeta = node.folder_fmeta
    else:
        folder = node.folder
        fmeta = node.multi or node.fmeta
    return folder, fmeta


def __groups_set(folder, fmeta, gset, op, retv):
    if not gset:
        gset = set([u'private'])
    if gset - retv:
        folder.add_file(fmeta, gset - retv)
    if retv - gset:
        folder.delete_file(fmeta, retv - gset, keep_file=True)
    return gset


def _mkdir(path, node, **kw):
    """
        Create a folder at the specified path
        Args: path (str): path of the folder
    """
    if node.exists:
        raise fill_io_error(errno.EEXIST, path)
    if node.multi and node.fmeta.name != node.folder.fs.ctx.cidhash:
        raise fill_io_error(errno.EACCES, path)
    name = node.multi.name if node.multi else node.fmeta.name
    return node.folder.mkdir(name, path, **kw)


def _rmdir(path, node, force=False):
    """
        Remove a folder.
        Invalid if folder is virtual from multientry.
    """
    parent = node.parent if node.is_folder else node.folder
    if parent is None:
        raise fill_io_error(errno.EPERM, path)
    # todo: access control
    if not node.is_folder:
        raise fill_io_error(errno.ENOTDIR, path)
    if node.listdir() and not force:
        raise fill_io_error(errno.ENOTEMPTY, path)
    if not parent.is_folder:
        raise NotImplementedError
    parent.delete_file(node.folder_fmeta)


def _open(ctx, path, node, mode='r', immediate_add=False):
    """
        Open the specified file.
        Return the handle to the temporary file.
    """
    if node.is_folder:
        raise fill_io_error(errno.EISDIR, path)
#    if any(m in mode for m in 'wa+'):
#        self.check_permissions(perm.write)

    # opening for reading
    if 'r' in mode and '+' not in mode:
        # verify if destination path exists and is a proper file
        if not node.exists:
            raise fill_io_error(errno.ENOENT, path)
        fmeta = node.fmeta
        author_ = node.folder.get_author(fmeta.fid)
    # opening for writing / updating
    else:
        if ctx.cid is None:
            raise fill_io_error(errno.EPERM, path)
        # we cannot overwrite someone else's multi,
        # we must remove it and open our own file
        if node.is_multi and node.multi_id != ctx.cidhash:
            raise fill_io_error(errno.EPERM, path)
        # fs.invalidate_cache_item(path, node)
        # del fs.traverse_cache[path]
        # check if file does not exist
        if not node.exists:
            # in this case append is just a regular
            # write (not really, see tests)
            if 'a' in mode:
                mode = mode.replace('a', 'w')
            if node.is_multi:
                # name is virtual, must manually invalidate it
                ctx.fs.update_cache_item(path)
                fmeta = Metadata(name=node.multi.fmeta.name, type=fmtypes.FILE)
            else:
                fmeta = Metadata(name=node.fmeta.name, type=fmtypes.FILE)
            # create a temporary file entry
            if immediate_add:
                node.folder.add_file(fmeta)
            else:
                fmeta.fid = None
        # file exists
        else:
            fmeta = node.fmeta
            if not node.is_multi:
                if ctx.cidhash != node.folder.get_author(fmeta.fid):
                    # we cannot overwrite someone else's file,
                    # we must remove it and open our own
                    raise fill_io_error(errno.EPERM, path)
            else:
                # name is virtual, must manually invalidate it
                ctx.fs.update_cache_item(path)
        author_ = ctx.cidhash
    if 'd' in mode and '+' not in mode:
        facc_class = DirectFileAccessor
    else:
        facc_class = FileAccessor
    return facc_class(node.folder, fmeta, mode, author_)


def _unlink(path, node, force=False, keep_file=False):
    """
        Remove the file.
    """
    if not node.exists:
        raise fill_io_error(errno.ENOENT, path)
    if node.is_folder:
        raise fill_io_error(errno.EISDIR, path)
    node.folder.delete_file(node.fmeta, keep_file)


def _rename(origin, path1, destination, path2):
    if not origin.exists:
        raise fill_io_error(errno.ENOENT, path1)
    if origin == destination:
        raise fill_io_error(errno.EPERM, path1)
    if origin.is_folder:
        ofolder = origin.parent
        ometa = origin.folder_fmeta
        _rename_folder(origin, ofolder, ometa, destination, path2)
    else:
        ofolder = origin.folder
        ometa = origin.fmeta
        _rename_file(ofolder, ometa, destination, path2)
    ofolder.fs.update_cache_item(path1)


def _rename_folder(origin, ofolder, ometa, destination, path2):
    groups = ofolder.get_groups(ometa)
    if not destination.is_folder:
        if destination.exists:
            # can't move a folder over a file
            raise fill_io_error(errno.ENOTDIR, path2)
        if destination.folder.idhash != ofolder.idhash:
            # moving folders across identities is not possible
            raise fill_io_error(errno.EPERM, path2)
        name = destination.fmeta.name
        destination = destination.folder
    else:
        pchain = destination
        while pchain:
            if pchain == origin:
                raise fill_io_error(errno.EBUSY, origin.path)
            pchain = pchain.parent
        name = ometa.name
        if name in destination.file_dict:
            # overwriting - can't move a folder over a file
            raise fill_io_error(errno.EEXIST, path2, name)
    # move folder to destination
    new_fmeta = Metadata(ometa)
    new_fmeta.name = name
    ofolder.check_access(ometa, False)
    destination.check_access(new_fmeta)
    ofolder.delete_file(ometa, keep_file=True)
    destination.add_file(new_fmeta, groups)
    origin.parent = destination
    origin.path = path2
    origin.set_modified()


def _rename_file(ofolder, ometa, destination, path2):
    # check if we can actually remove from the original folder
    ofolder.check_access(ometa, False)
    groups = ofolder.get_groups(ometa)
    if not destination.is_folder:
        dfolder = destination.folder
        name = destination.fmeta.name
        if destination.exists:
            dmeta = destination.fmeta
            oauthor = ofolder.get_author(ometa.fid)
            if dfolder.get_author(dmeta.fid) == oauthor:
                # same author, overwrite
                # can we overwrite it?
                dfolder.check_access(dmeta, False)
            else:
                # create a multientry
                dmeta = None
        else:
            dmeta = None
    else:
        dfolder = destination
        name = ometa.name
        if name in dfolder.file_dict:
            if len(dfolder.file_dict[name]) > 1:
                # cannot overwrite a multi
                raise fill_io_error(errno.EPERM, path2, name)
            dmeta = dfolder.file_dict[name][0]
            # can we overwrite it?
            dfolder.check_access(dmeta, False)
        else:
            dmeta = None
    if dfolder.idhash != ofolder.idhash:
        raise NotImplementedError("copy between identities tbd")
    dfolder.check_access(ometa)
    new_fmeta = Metadata(ometa)
    new_fmeta.name = name
    dfolder.check_access(new_fmeta)
    if dmeta is not None:
        dfolder.delete_file(dmeta)
    ofolder.delete_file(ometa, keep_file=True)
    dfolder.add_file(new_fmeta, groups)


class Operations(Traverser):
    """
        Class for manipulating folders and its contents.
    """

    def listdir(self, path=u"."):
        """
            Return the list of files/folders at the specified path.

            Args:
                path (str): path to the folder (can be filesystem root)
        """
        path = self.abspath(path)
        if not path:
            from phen import storage
            return storage.store.list_root()
        trav, path = self.traverse(path, absolute=True)
        obj = trav[-1]
        if obj.is_folder:
            return obj.listdir()
        elif obj.multi:
            return obj.folder.list_multi(obj.multi.name)
        elif not obj.exists:
            if obj.fmeta.name == "":
                return obj.folder.listdir()
            raise fill_io_error(errno.ENOENT, path)
        raise fill_io_error(errno.ENOTDIR, path)

    def wrap_method(method):
        """
            Wrap the method, providing it with the
            traversed path, and copying its docstring.
        """
        @functools.wraps(method)
        def wrapper(self, path, *p, **kw):
            trav, path = self.traverse(path)
            # pylint: disable-msg=W0142
            return method(path, trav[-1], *p, **kw)
        return wrapper

    # get metadata from the specified file/folder.
    filemeta = wrap_method(_filemeta)
    # check permission to write
    access = wrap_method(_access)
    # change extended attributes
    xattr = wrap_method(_xattr)
    # change the modification time
    utime = wrap_method(_utime)
    # create a folder
    mkdir = wrap_method(_mkdir)
    # remove a folder
    rmdir = wrap_method(_rmdir)
    # remove file
    unlink = wrap_method(_unlink)

    # return the file's author
    author = wrap_method(_author)
    # return the groups to which the file belongs or change its access
    groups = wrap_method(_groups)

    def open(self, path, mode='r', immediate_add=False):
        """
            Open a file.
        """
        trav, path = self.traverse(path)
        return _open(self.ctx, path, trav[-1], mode, immediate_add)

    def rename(self, path1, path2):
        """
            Rename or move a file to a different folder.
        """
        trav1, path1 = self.traverse(path1)
        trav2, path2 = self.traverse(path2)
        return _rename(trav1[-1], path1, trav2[-1], path2)

    def exists(self, path):
        """
            Verify if a file or folder exists at the path.
        """
        try:
            trav, path = self.traverse(path)
            if trav[-1].is_folder or trav[-1].exists:
                return trav[-1]
        except IOError:
            pass
        return False

    def chdir(self, path=None):
        """
            Change the current working folder.
        """
        if path is None:
            idhash = hasattr(self, "ctx") and self.ctx.cidhash or u""
            newdir = u"/" + idhash
        else:
            newdir = u"/" + self.abspath(path)
        self.listdir(newdir)
        retv = self.curdir
        self.curdir = newdir
        return retv

    def makedirs(self, path, **kw):
        """
            Create a leaf folder and its intermediaries as needed.
        """
        to_create = []
        while not self.exists(path) and u"/" in path:
            idx = path.rfind(u"/")
            segment = path[idx + 1:]
            if segment and segment != u".":
                to_create.append(segment)
            path = path[:idx]
        if not path:
            raise RuntimeError("`makedirs` can't create the root folder")
        trav, path = self.traverse(path)
        retv = trav[-1]
        if not retv.is_folder:
            idx = path.rfind(u"/")
            path = path[:idx]
            to_create.append(retv.fmeta.name)
            retv = retv.folder
        while to_create:
            name = to_create.pop(-1)
            path += u"/" + name
            retv = retv.mkdir(name, path, **kw)
        return retv

    def rmtree(self, path):
        """
            Remove a folder tree.
        """
        for fname in self.listdir(path):
            fpath = u"/".join([path, fname])
            fmeta = self.filemeta(fpath)
            # todo: deal with multis
            if fmeta.is_folder():
                self.rmtree(fpath)
            else:
                self.unlink(fpath)
        self.rmdir(path)

    def map_multi(self, path):
        """
            Return a dictionary of identity hashes mapping to
            the contents of the expected multi.
        """
        try:
            idlist = self.listdir(path)
            return {idhash: u"/".join((path, idhash)) for idhash in idlist}
        except IOError as exc:
            if exc == errno.ENOTDIR:
                return {self.author(path): path}
        return {}

    def dump(self, path):
        """
            Dump the unencoded folder structure - helper method for debugging.
        """
        trav, path = self.traverse(path)
        folder = trav[-1] if trav[-1].is_folder else trav[1].folder
        retv = [json.dumps(folder.metadata, indent=4),
                folder.dump(),
                u"notif_tag: {0.notif_tag}\nmtime: {0.mtime}".format(folder)]
        return u"\n".join(retv)

    def json_read(self, path, **kw):
        with self.open(path, 'rd') as infile:
            return json.loads(infile.read().decode("utf8"), **kw)

    def json_write(self, path, data, **kw):
        with self.open(path, 'wd') as out:
            return out.write(json.dumps(data, **kw).encode("utf8"))

    def glob_re(self, path_regex, im_files=False, base_path=None):
        """
            Select files and folders based no regular expressions.

            Note this is different than os.glob, wildcards must be
            expressed as .*, the actual dot must be escaped (i.e. \.), and
            you must explicitly express the end of a segment (e.g. wiki$/.*
            otherwise it would match "wikipedia/something" as well).
        """
        retv = []
        if not path_regex:
            return retv
        if path_regex[0] == u"/":
            if not base_path:
                base_path = u"/"
            path_regex = path_regex.lstrip(u"/")
        dive = path_regex.find(u"/") if u"/" in path_regex else -1
        if dive != -1:
            regex = path_regex[:dive]
            path_regex = path_regex[dive + 1:]
        else:
            regex = path_regex
            path_regex = ""
        base_path = base_path or u"."
        for fname in self.listdir(base_path):
            try:
                if not re.match(regex, fname):
                    continue
            except Exception:
                # invalid regex, return what we have so far
                return retv
            fpath = u"/".join([base_path, fname])
            try:
                fmeta = self.filemeta(fpath)
            except IOError:
                fmeta = None
            if dive == -1 or im_files:
                retv.append((base_path, fname, fmeta))
            if dive != -1 and fmeta.is_folder():
                retv += self.glob_re(path_regex, im_files, fpath)
        return retv

    def glob(self, pattern):
        """
            Return a list of paths matching a pathname pattern,
            just like `glob.glob`.
        """
        return list(self.iglob(pattern))

    def iglob(self, pattern):
        from glob import has_magic
        if not has_magic(pattern):
            if self.exists(pattern):
                yield pattern
            return
        idx = pattern.rfind("/")
        if idx < 0:
            idx = 0
        dirname, basename = pattern[:idx], pattern[idx:]
        if not dirname:
            for name in self._glob1(None, basename):
                yield name
            return
        if has_magic(dirname):
            dirs = self.iglob(dirname)
        else:
            dirs = [dirname]
        if has_magic(basename):
            glob_in_dir = self._glob1
        else:
            glob_in_dir = self._glob0
        for dirname in dirs:
            for name in glob_in_dir(dirname, basename):
                yield "/".join((dirname, name))

    def _glob1(self, dirname, pattern):
        if not dirname:
            dirname = self.curdir
        try:
            names = self.listdir(dirname)
        except IOError:
            return []
        import fnmatch
        return fnmatch.filter(names, pattern)

    def _glob0(self, dirname, basename):
        if not basename:
            fmeta = self.filemeta(dirname)
            if fmeta and fmeta.is_folder():
                return [basename]
        else:
            if self.exists("/".join((dirname, basename))):
                return [basename]
        return []
