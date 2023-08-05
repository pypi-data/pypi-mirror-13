# -*- coding:utf-8 -*-

from .util import input_passphrase, file_complete
from .base import ProtectedSubCmd, requires_cid, shlexed


class Groups(ProtectedSubCmd):
    """
        Group management and attribution.
    """
    cmdname = "grp"

    def __init__(self, parent, *p, **kw):
        ProtectedSubCmd.__init__(self, *p, **kw)
        self.parent = parent
        self.ctx = parent.ctx

    def preloop(self):
        self.update_prompt()

    def update_prompt(self):
        if self.color:
            pfmt = "\x1b[1;32mgrp)\x1b[1;34m{}\x1b[0m$ "
        else:
            pfmt = "grp){}$ "
        idhash = self.ctx.fs.curdir
        self.prompt = pfmt.format(idhash[:5])

    @shlexed
    @requires_cid
    def do_list(self, args):
        """list [file path]

        Lists all groups accessible by the current identity or
        the ones to which the specified file/folder belongs.

        """
        groups = self.ctx.fs.groups(args[0]) if args else self.ctx.groups
        self.columnize([e.encode("utf-8") for e in groups])

    def complete_list(self, text, line, start_index, end_index):
        return file_complete(self.ctx.fs, text)

    @shlexed
    @requires_cid
    def do_create(self, args):
        """create <name> [shared secret | --]

        Creates a new group, using an agreed secret if specified.

        Examples:
            create "work buddies"
            create folks_at_conference "remember this passphrase"

        """
        if not args:
            return self.do_help("create")
        if len(args) > 2:
            return self.send("Too many arguments, perhaps missing quotes")
        secret = args[1] if len(args) > 1 else None
        if secret == '--':
            secret = input_passphrase(self, "Enter the shared secret: ")
        name = args[0]
        self.ctx.groups.new_group(name, secret)

    def _change_groups(self, path, groups, op='set'):
        try:
            groups = self.ctx.fs.groups(path, groups, op)
            self.columnize([e.encode("utf-8") for e in groups])
        except IOError as e:
            self.send(e)
        except LookupError as e:
            self.send(e)

    @shlexed
    @requires_cid
    def do_set(self, args):
        """set <file path> <group1> [group2 ... groupN]

        Set the file's groups.
        """
        if len(args) < 2:
            return self.do_help("set")
        self._change_groups(args[0], set(args[1:]), 'set')

    @shlexed
    @requires_cid
    def do_add(self, args):
        """add <file path> <group1> [group2 ... groupN]

        Add groups to the file visibility.
        """
        if len(args) < 2:
            return self.do_help("add")
        self._change_groups(args[0], set(args[1:]), 'add')

    @shlexed
    @requires_cid
    def do_del(self, args):
        """add <file path> <group1> [group2 ... groupN]

        Remove groups from the file visibility.
        """
        if len(args) < 2:
            return self.do_help("del")
        self._change_groups(args[0], set(args[1:]), 'del')

    def complete_set(self, text, line, start_index, end_index):
        import shlex
        args = shlex.split(line.encode("utf8"))
        if len(args) < 3:
            retv = [
                fname
                for fname in file_complete(self.ctx.fs, text)
            ]
        else:
            retv = [
                group for group in self.ctx.groups
                if line[-1] == ' ' or group.startswith(args[-1])
            ]
        return retv

    complete_add = complete_set
    complete_del = complete_set
