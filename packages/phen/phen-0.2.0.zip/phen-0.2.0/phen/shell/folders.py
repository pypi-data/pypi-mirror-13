#!/usr/bin/env python
#-*- coding:utf-8 -*-

from .base import shlexed, requires_cid
from .util import file_complete


class FolderCommands:
    def do_cd(self, line):
        """cd [folder path]

        Changes the current working folder, or go
        to your root folder if none specified.
        """
        if not line:
            line = u"/"
            if self.ctx.cidhash:
                line += self.ctx.cidhash
        try:
            self.ctx.fs.chdir(line)
        except Exception as e:
            self.send(e)
        self.update_prompt()

    def complete_cd(self, text, line, start_index, end_index):
        return file_complete(self.ctx.fs, text, True)

    def do_pwd(self, line):
        """pwd

        Prints the current working folder.
        """
        self.send(self.ctx.fs.curdir)

    @requires_cid
    def do_mkdir(self, line):
        """mkdir <folder path>

        Creates a folder.
        """
        if not line:
            return self.do_help("mkdir")
        try:
            self.ctx.fs.mkdir(line)
        except Exception as e:
            self.send(e)

    @requires_cid
    def do_rmdir(self, line):
        """rmdir <folder path>

        Removes an empty folder.
        """
        if not line:
            return self.do_help("rmdir")
        try:
            self.ctx.fs.rmdir(line)
        except Exception as e:
            self.send(e)

    complete_rmdir = complete_cd

    @requires_cid
    def do_rmtree(self, line):
        """rmtree <folder path>

        Removes a folder and all its contents.
        """
        if not line:
            return self.do_help("rmtree")
        try:
            self.ctx.fs.rmtree(line)
        except Exception as e:
            self.send(e)

    complete_rmtree = complete_cd

    def do_dump(self, line):
        """dump [folder path]

        Prints the folder unencoded structure.
        """
        try:
            self.send(self.ctx.fs.dump(line or u"."))
        except Exception as e:
            self.send(e)

    complete_dump = complete_cd

    def do_ls(self, line, ll=False):
        """ls [folder path]

        Lists the contents of the folder, or the current
        working one if none specified.
        """
        if not line:
            line = u"."
        if len(line) > 1:
            line = line.rstrip("/")
        try:
            files = sorted(self.ctx.fs.listdir(line))
        except Exception as e:
            self.send(e)
            return

        fmtd = [_fmt(self.ctx, self.color, "/".join((line, f)), ll)
                for f in files] if files else ["<empty>"]
        if ll:
            self.send("\n".join(fmtd))
        else:
            self.columnize([f.encode("utf-8") for f in fmtd])

    complete_ls = complete_cd

    def do_ll(self, line):
        """ll

        Long line file list.
        """
        self.do_ls(line, True)

    complete_ll = complete_cd

    @shlexed
    def do_glob(self, args):
        """glob [glob expr. [intermediate files = True | False* [command]]]

        Lists the files matched by the glob expression, which is a composite
        of regular expressions, e.g. ".*/.*/.*\.txt"

        Note that you must explicitly express the end of a segment,
        e.g. "wiki$/.*" otherwise it would match "wikipedia/something" as well.
        """
        # todo: match the whole path against a single regex, eg. system(/.+)*
        glob = ".*" if not args else args[0]
        im_files = len(args) > 1 and args[1].lower() == "true"
        cmd = args[2:] if len(args) > 2 else None
        if cmd and not hasattr(self, "do_" + cmd[0]):
            self.send("no such command '{}'".format(cmd[0]))
            return
        try:
            fmetas = self.ctx.fs.glob(glob, im_files)
        except Exception as e:
            self.send(e)
            return
        if cmd:
            method = getattr(self, "do_" + cmd[0])
            for fmeta in fmetas:
                args = "".join([a for a in cmd[1:] +
                               ["/".join(fmeta[:2])]])
                method(args)
            return
        self.send("\n".join(_fmt(self.ctx, self.color, "/".join(f[:2]))
                            for f in fmetas) if fmetas else "<empty>")


def _fmt(ctx, use_color, f, ll=True):
    if f.startswith("./"):
        f = f[2:]
    elif f.startswith("//"):
        f = f[1:]
    try:
        fmeta = ctx.fs.filemeta(f, True)
    except IOError:
        fmeta = None
    if not fmeta:  # root
        return f
    if fmeta.is_folder():
        color = 4  # blue
    else:
        color = 7  # white
    size = "{:9d}".format(fmeta.size)
    style = 0  # normal
    groups = ctx.fs.groups(f)
    if u'public' in groups:
        style = 1  # bold
    elif len(groups) == 1 and u'private' in groups:
        style = 3  # italic / inverse
    if use_color:
        name = "\x1b[{};3{}m{}\x1b[0m".format(style, color, f)
        groups = "\x1b[1;30m({})\x1b[0m".format(", ".join(groups))
    else:
        name = f
        groups = "({})".format(", ".join(groups))

    if not ll:
        return name

    import time
    author = ctx.fs.author(f)
    ftime = time.strftime("%Y-%m-%d %H:%M:%S", time.localtime(fmeta.mtime))
    return "{} {} {}  {}\t{}".format(ftime, author[:5], size, name, groups)
