# -*- coding:utf-8 -*-

import os
import json
import zipfile

from phen import storage
from phen.util import cvt_to_zipfile, is_idhash


def import_file(fs, src, dest):
    """
        Copy the file from the OS to the internal filesystem
    """
    with open(src, 'rb') as infile:
        with fs.open(dest, 'wd') as out:
            while True:
                data = infile.read(1 << 16)
                if not data:
                    break
                out.write(data)


def recursive_import(fs, src, dest):
    """
        Recursively copy the file or folder from
        the host OS to the internal filesystem
        dest: folder path
    """
    if not os.path.isdir(src):
        distname, fname = os.path.split(src)
        return import_file(fs, src, u"/".join((dest, fname)))

    src = src.rstrip(os.path.sep)
    slen = len(src) + 1
    dummy, destname = os.path.split(src)
    if not destname:
        base = dest
    else:
        base = u"/".join((dest, destname))
    if not fs.exists(base):
        fs.makedirs(base)
    for dirpath, dirnames, filenames in os.walk(src):
        sdirname = u"/".join((base, dirpath[slen:]))
        for dname in dirnames:
            sdest = "/".join((sdirname, dname))
            if not fs.exists(sdest):
                fs.mkdir(sdest)
        for fname in filenames:
            path = os.path.join(dirpath, fname)
            sdest = "/".join((sdirname, fname))
            import_file(fs, path, sdest)


def export_file(fs, src, dest):
    """
        Copy the file from the interal filesystem to the host's
    """
    with fs.open(src, 'rd') as infile:
        with open(dest, 'wb') as out:
            while True:
                data = infile.read(1 << 16)
                if not data:
                    break
                out.write(data)


def recursive_export(fs, src, dest):
    """
        Recursively copy the file or folder from
        the internal filesystem to the host's
        dest: folder path
    """
    fname = src.split("/")[-1]
    dest_name = os.path.join(dest, fname)
    if not fs.filemeta(src).is_folder():
        return export_file(fs, src, dest_name)
    if not os.path.exists(dest_name):
        os.mkdir(dest_name)
    for fname in fs.listdir(src):
        recursive_export(fs, "/".join((src, fname)), dest_name)


def _get_properties(fs, fname):
    p = {}
    groups = list(fs.groups(fname))
    if groups != [u"private"]:
        p["groups"] = groups
    fmeta = fs.filemeta(fname)
    p["mtime"] = fmeta.mtime
    p["dtime"] = fmeta.dtime
    if fmeta.xattr:
        p["xattr"] = fmeta.xattr
    trav, path = fs.traverse(fname)
    if trav[-1].is_folder:
        p["nonce"] = trav[-1].metadata["nonce"]
    return p


def _set_properties(fs, fpath, props):
    grp = set(gid for gid in props.get("groups", [])
              if gid == u'public' or gid in fs.ctx.groups)
    fs.groups(fpath, grp, 'set')
    if props.get("xattr"):
        fs.xattr(fpath, props.get("xattr"))
    dtime, mtime = props.get("dtime"), props.get("mtime")
    if dtime and mtime:
        fs.utime(fpath, dtime, mtime)


PFILE = u"filesystem-entries.props"


def pack_folder(fs, out, path=None, ui=None, owned=True, strip=0):
    """
        Recursively add the contents of the folder to the zipfile.
    """
    must_close = not isinstance(out, zipfile.ZipFile)
    out = cvt_to_zipfile(out)
    prev_cwd = fs.chdir(path or u"/" + fs.ctx.cidhash)
    cwd = fs.curdir[1:] + u"/"
    if strip == -1:
        strip = fs.curdir.count(u"/") - 1
    if strip:
        scwd = u"/".join(cwd.split(u"/")[strip:])
    flist = fs.listdir()
    if owned:
        # todo: deal with multis
        flist = [fname for fname in flist
                 if fs.author(fname) == fs.ctx.cidhash]
    props = {fname: _get_properties(fs, fname)
             for fname in flist}
    out.writestr((scwd if strip else cwd) + PFILE, json.dumps(props))
    for fname in flist:
        if fname == PFILE:
            # not permitted in backups
            continue
        fmeta = fs.filemeta(fname)
        ui and ui(fname, fmeta.size)
        if fmeta.is_folder():
            pack_folder(fs, out, u"/" + cwd + fname, ui, owned, strip)
            continue
        pkdname = (scwd if strip else cwd) + fname
        if fmeta.size < 1 << 19:
            with fs.open(fname, 'rd') as infile:
                out.writestr(pkdname, infile.read())
        else:
            with fs.open(fname) as infile:
                out.write(infile.file.name, pkdname)
    fs.chdir(prev_cwd)
    if must_close:
        out.close()


def _flist_iter(fs, flist, strip, end=None, ui=None):
    for fname in flist:
        parts = fname.split(u"/")
        if strip == -1:
            if not is_idhash(parts[0]):
                ui and ui(u"ignoring", fname)
                continue
            path = u"/".join([u""] + parts[:end])
        else:
            path = u"/".join(parts[strip:end])
        if path:
            yield fname, path, parts[-1]


def unpack_folder(fs, zin, path=None, ui=None, strip=0):
    if not isinstance(zin, zipfile.ZipFile):
        zin = zipfile.ZipFile(zin)
    flist = zin.namelist()
    all_props = {}
    prev_cwd = fs.chdir(path or u"/" + fs.ctx.cidhash)

    # read all property definitions
    for pkd, path, name in _flist_iter(fs, flist, 0):
        if name != PFILE:
            continue
        all_props[pkd] = json.loads(zin.read(pkd).decode("utf8"))

    # make all not-yet-existing folders
    for pkd, path, name in _flist_iter(fs, all_props, strip, -1, ui):
        fmeta = fs.exists(path)
        if fmeta is False:
            if strip == -1:
                # use the recorded nonce if absolute path
                parent = "/".join(pkd.split("/")[:-2] + [PFILE])
                folder_name = path.split("/")[-1]
                props = all_props.get(parent, {}).get(folder_name, {})
            else:
                props = {}
            ui and ui(u"mkdir", path)
            fs.makedirs(path, nonce=props.get("nonce"))
        elif not fmeta.is_folder:
            raise IOError(u"Can't unpack over non-folder: " + path)

    # extract files
    for pkd, path, name in _flist_iter(fs, flist, strip, ui=ui):
        if name == PFILE or fs.exists(path):
            continue
        ui and ui(u"write", path)
        with fs.open(path, 'wd') as out:
            with zin.open(pkd) as infile:
                while True:
                    data = infile.read(1 << 16)
                    if not data:
                        break
                    out.write(data)

    # apply properties
    for pkd, path, name in _flist_iter(fs, all_props, strip, -1, ui):
        props = all_props[pkd]
        for fname in props:
            fpath = u"/".join((path, fname))
            _set_properties(fs, fpath, props[fname])

    fs.chdir(prev_cwd)


def recover_content(fs, cid, infile, ui=None):
    """
        Restore backed-up contents.
    """
    if not storage.store.is_available((cid.hash, None)):
        recover_content_create(fs, cid, infile, ui)
    else:
        recover_content_update(fs, cid, infile)


def recover_content_create(fs, cid, infile, ui=None):
    pfn = "/filesystem-entries.props"
    fs.create_identity_root(cid)
    folders_made = {}
    fname = cid.hash + pfn
    folders_made[cid.hash] = json.loads(infile.read(fname))
    for fname in infile.namelist():
        if not fname.startswith(cid.hash):
            continue
        parts = fname.split("/")
        folder = "/".join(parts[:-1])
        if folder and folder not in folders_made:
            ui and ui("mkdir", folder)
            propdef = infile.read(folder + pfn)
            folders_made[folder] = json.loads(propdef)
            props = folders_made["/".join(parts[:-2]) or cid.hash][parts[-2]]
            # we assume folders are created in order
            nonce = props.get("nonce")
            r_fname = "/".join(parts[1:-1])
            fs.makedirs(r_fname, nonce=nonce)
            if props.get("xattr"):
                fs.xattr(r_fname, props.get("xattr"))
            dtime, mtime = props.get("dtime"), props.get("mtime")
            if dtime and mtime:
                fs.utime(r_fname, dtime, mtime)
        if fname.endswith(pfn) or not parts[-1]:
            continue
        ui and ui("write", fname)
        r_fname = "/".join(parts[1:])
        with fs.open(r_fname, 'wd') as out:
            with infile.open(fname) as i_infile:
                while True:
                    data = i_infile.read(1 << 16)
                    if not data:
                        break
                    out.write(data)
        props = folders_made[folder][parts[-1]]
        if props.get("xattr"):
            fs.xattr(r_fname, props.get("xattr"))


def recover_content_update(fs, cid, infile):
    fs.set_current_identity(cid)
    for fname in infile.namelist():
        if not fname.endswith("filesystem-entries.props"):
            continue
        parts = fname.split("/")
        folder = "/".join(parts[1:-1])
        props = json.loads(infile.read(fname))
        for f in props:
            full_path = f if not folder else (folder + "/" + f)
            if not fs.exists(full_path):  # user may have removed it
                continue
            grp = set(gid for gid in props[f].get("groups", [])
                      if gid == u'public' or gid in cid.ctx.groups)
            fs.groups(full_path, grp, 'set')
            dtime, mtime = props[f].get("dtime"), props[f].get("mtime")
            if dtime and mtime:
                fs.utime(full_path, dtime, mtime)


def export_essentials(fs, out, idhash=None, only_pub=True, level=None):
    """
        Export the files required for estabilishing contact.
    """
    out = cvt_to_zipfile(out)
    if not idhash:
        idhash = fs.ctx.cidhash
    if level is None:
        out.writestr("identity hash", idhash)
        level = 1
    fid_list = set(["public.key", "root"])
    recursive_list = []
    from phen.socnet.initfolder import essentials
    for glob in essentials:
        matches = fs.glob_re(glob, True, "/" + idhash)
        if only_pub:
            matches = [match for match in matches
                       if u'public' in fs.groups("/".join(match[:2]))]
        recursive_list += [
            fname for path, fname, fmeta in matches
            if path.endswith("system/devices") and is_idhash(fname)
        ]
        fid_list.update([fmeta.fid
                         for path, fname, fmeta in matches
                         if hasattr(fmeta, "fid")])
    fs.export_fid_list(out, idhash, fid_list)
    if not level:
        return out
    rec_ids = set(recursive_list)
    for idhash in rec_ids:
        export_essentials(fs, out, idhash, only_pub, level - 1)
    return out


def export_system(fs, out, idhash):
    fid_list = []
    for folder in ("system/contacts", "system/groups", "system/config"):
        path = fs.subpath(idhash, folder)
        if not fs.exists(path):
            continue
        fmeta = fs.filemeta(path)
        fid_list.append(fmeta.fid)
        if not fmeta.is_folder():
            continue
        for fname in fs.listdir(path):
            fullname = fs.subpath(idhash, folder, fname)
            fmeta = fs.filemeta(fullname)
            fid_list.append(fmeta.fid)
    fs.export_fid_list(out, idhash, fid_list)


def import_from_zipfile(fs, infile, idhash=None, fid_list=None):
    if not isinstance(infile, zipfile.ZipFile):
        infile = zipfile.ZipFile(infile)
    for info in infile.infolist():
        if info.filename.count("/") != 1:
            continue
        idfolder, fid = info.filename.split("/")
        if idhash is not None and idfolder != idhash:
            continue
        if fid_list is not None and fid not in fid_list:
            continue
        fid_pair = idfolder, fid
        if not storage.store.is_available(fid_pair):
            data = infile.read(info.filename)
            with storage.store.store(fid_pair) as out:
                out.write(data)
