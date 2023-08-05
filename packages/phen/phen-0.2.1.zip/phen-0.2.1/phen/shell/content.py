#!/usr/bin/env python
#-*- coding:utf-8 -*-

import os

from phen.filesystem.io import (
    recursive_import, recursive_export, pack_folder, unpack_folder
)

from .base import ProtectedSubCmd, protected, requires_cid, shlexed


class Content(ProtectedSubCmd):
    """
        Content IO.
    """
    cmdname = "content"

    def __init__(self, parent, *p, **kw):
        ProtectedSubCmd.__init__(self, *p, **kw)
        self.parent = parent
        self.ctx = parent.ctx

    def preloop(self):
        self.update_prompt()

    def update_prompt(self):
        if self.color:
            pfmt = "\x1b[1;32mcontent)\x1b[1;34m{}\x1b[0m$ "
        else:
            pfmt = "content){}$ "
        self.prompt = pfmt.format(self.ctx.fs.curdir)

    @protected
    @requires_cid
    @shlexed
    def do_import(self, args):
        """import <host-path>

        Imports a file or folder from the host filesystem.
        """
        if not args:
            return self.do_help("import")
        try:
            recursive_import(self.ctx.fs, args[0], self.ctx.fs.curdir)
        except Exception as e:
            self.send(e)

    @protected
    def complete_import(self, text, *p):
        dirname, fname = os.path.split(text)
        if not dirname:
            dirname = u"./"
        from glob import glob
        return glob(os.path.join(dirname, fname + "*"))

    @protected
    @shlexed
    def do_export(self, args):
        """export <internal-path> [host-folder]

        Exports a file or folder to the host filesystem.
        """
        if not args or len(args) > 2:
            return self.do_help("export")
        source_path = args[0]
        dest_folder = args[1] if len(args) > 1 else "."
        if not os.path.isdir(dest_folder):
            return self.send("Destination must be a folder")
        try:
            recursive_export(self.ctx.fs, source_path, dest_folder)
        except Exception as e:
            self.send(e)

    @protected
    def complete_export(self, text, *p):
        from .util import file_complete
        return file_complete(self.ctx.fs, text)

    @protected
    @requires_cid
    @shlexed
    def do_unpack(self, args):
        """unpack <zip-file-path> [n] [-a] [-q]

        Unpacks a previously packed folder (will not work with a regular zip).
        The `n` parameter indicates the number of levels to ignore.
        Options:
            -a      consider paths absolute (first level must be fingerprint)
            -q      quiet
        """
        if len(args) < 1:
            return self.do_help("unpack")
        source_path = args[0]
        try:
            strip = int(args[1])
        except:
            strip = 0
        if "-a" in args:
            strip = -1

        def ui(op, fname):
            self.send("{}: {}".format(op, fname))

        try:
            unpack_folder(self.ctx.fs, source_path, u".",
                          None if "-q" in args else ui, strip)
        except Exception as e:
            self.send(e)

    complete_unpack = complete_import

    @protected
    @shlexed
    def do_pack(self, args):
        """pack <folder> <zip-file-path> [--all|--owned] [--strip] [-f] [-q]

        Packs a folder into a zip file in the host filesystem.
        Options:
            --all       include files created by other identities
            --owned     packs only files from the current identity (default)
            --strip     use paths relative to the one specified, not root
            -f          force destination overwrite
            -q          quiet
        """
        if len(args) < 2:
            return self.do_help("pack")
        owned = "--all" not in args
        strip = -1 if "--strip" in args else 0
        source_path = args[0]
        dest_path = args[1]
        if not dest_path.lower().endswith(".zip"):
            dest_path += ".zip"
        if os.path.exists(dest_path) and "-f" not in args:
            return self.send("Destination exists, use -f to overwrite")

        def ui(fname, size):
            self.send("Adding {} ({} bytes)".format(fname, size))

        try:
            pack_folder(self.ctx.fs, dest_path, source_path,
                        None if "-q" in args else ui, owned, strip)
        except Exception as e:
            self.send(e)

    complete_pack = complete_export
