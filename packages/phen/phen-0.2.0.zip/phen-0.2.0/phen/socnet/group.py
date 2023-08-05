#!/usr/bin/env python
#-*- coding:utf-8 -*-

"""
    Group Management

    A group allows read access through its AES key, and write
    access by signing of the file identifier with the private key,
    whose respective public key is available in the folder access
    control.[clarification needed]

    The groups of a user are stored in its groups/ folder, and ve
    may allow access to contacts by adding the group file to the
    contact's shared group. Every user must scan vis contact's groups
    folder to collect all accessible groups.

    Groups are then labeled either "idhash/group name" and/or
    "username/group name". The user reference is omitted for the user's
    own groups. Groups u'public' and u'private' are special, and cannot
    exist as group files. Any file named so is malicious and must be ignored.

    A user can easily extend an external (not owned) group access to vis
    contacts by saving the group file to vis groups folder. Both original
    and cloned groups can be used interchangeably, without distinction.
"""

import six
import errno
from phen.event import Event
from phen.crypto import asym


class Group:
    def __init__(self, parent, gid, key):
        self.group_mgr = parent
        self.gid = gid
        self.key = key

    @staticmethod
    def new(parent, name, agreed_secret="", key_type='ECC secp224r1'):
        key = asym.PrivateKey.new(key_type, secret=agreed_secret)
        gpath = parent.ctx.cid.subpath("system/groups")
        fs = parent.ctx.fs
        if not fs.exists(gpath):
            parent.init_group_folder(gpath)
        gfname = "/".join((gpath, name))
        if fs.exists(gfname):
            raise IOError(errno.EEXIST,
                          "Group file at '{}' exists.".format(gfname))
        key.fs_save(fs, gfname)
        return Group(parent, name, key)

    @staticmethod
    def load(parent, gpath, gid, owner=None):
        try:
            path = "/".join((gpath, gid))
            key = asym.PrivateKey.fs_load(parent.ctx.fs, path)
        except:
            from traceback import print_exc
            print_exc()
            # todo: deal with corrupted groups more gracefully
            print("Corrupted group {}, ignoring".format(gid))
            return None
        return Group(parent, (owner + "/" + gid) if owner else gid, key)


class GroupContext:
    def __init__(self, gmgr, groups):
        self.gmgr = gmgr
        self.old_groups = self.gmgr.set_initial(*groups)

    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc_value, tback):
        self.gmgr.set_initial(self.old_groups)


class GroupManager:
    def __init__(self, ctx):
        self.ctx = ctx
        self.initial_groups = [u'private']
        self.ivec_groups = {}
        self.groups = {}
        self.groups_modified = Event()

    def set_initial(self, *groups):
        """
            Set the groups for new files and return the previous value.
        """
        if not groups:
            groups = [u'private']
        elif isinstance(groups[0], (list, tuple)):
            groups = groups[0]
        current = self.initial_groups
        self.initial_groups = groups
        return current

    def refresh(self):
        self.ivec_groups = {}
        prev = set(self.groups.keys())
        #print self.ctx, "refreshing groups, cur", prev
        self.groups = {}
        if self.ctx.cid:
            # load owned groups
            self.load_obj_groups(self.ctx.cid, None)
            # load contacts' groups
            for contact in self.ctx.contacts.all_contacts():
                try:
                    self.load_obj_groups(contact,
                                         contact.username or contact.idhash)
                except IOError:
                    # might not be available atm
                    pass
        #print "refreshing groups, now", set(self.groups.keys())
        if prev != set(self.groups.keys()):
            self.groups_modified()

    def folder_modified(self, folder, tag, external=False):
        if tag == 'groups':
            print("group folder?", folder)
            self.refresh()

    def init_group_folder(self, gpath=None):
        if gpath is None:
            gpath = self.ctx.cid.subpath("system/groups")
        with self(u'public'):
            folder = self.ctx.fs.makedirs(gpath)
            folder.notif_tag = 'groups'
        with self():
            self.new_group("contacts")

    def load_obj_groups(self, obj, owner):
        """Load groups from an identity or contact."""
        if not obj:
            return
        gpath = obj.subpath("system/groups")
        if not self.ctx.fs.exists(gpath):
            return  # ignore groups from non-initialized identity
        for gid in self.ctx.fs.listdir(gpath):
            group = Group.load(self, gpath, gid, owner)
            if group:
                self.groups[group.gid] = group

    def new_group(self, name, agreed_secret=None):
        """Create a new group."""
        if name in (u'private', u'public'):
            raise ValueError("'{}' is a special group, it always exists."
                             .format(name))
        if name not in self.groups:
            self.groups[name] = Group.new(self, name, agreed_secret)
        return self.groups[name]

    def get_id_by_ivec(self, ivec):
        if ivec == b'public':
            return u'public'
        group_id = self.ivec_groups.get(b'i' + ivec)
        return group_id
        # todo: local data
#        if group_id == u'private':
#            return b'private'
#        if group_id in self.ctx.cid.contact_mgr:
#            return group_id
#        return group_id and self.groups[group_id].gid

    def set_ivec(self, ivec, group_id):
        # todo: cache ivecs in local data
        #print 'set ivec', ivec, group_id
        self.ivec_groups[b'i' + ivec] = group_id

    def get_key(self, group_id):
        """Return the AES key of the group."""
        if not isinstance(group_id, six.text_type):
            raise TypeError("Invalid group_id type {}".format(repr(group_id)))
        if group_id == u'private':
            return self.ctx.cid and self.ctx.cid.AES_key
        obj = self.ctx.contacts.get_by_username(group_id)
        if not obj:
            obj = self.groups.get(group_id)
        if not obj:
            raise LookupError("No group named '{}'.".format(group_id))
        return obj.key.AES_key

    def __iter__(self):
        yield u'private'
        for con in self.ctx.contacts.contacts.values():
            yield con.username or con.idhash
        for gid in self.groups:
            yield gid

    def __contains__(self, gid):
        if gid == u'private':
            return True
        if (gid in self.ctx.contacts.by_username
                or gid in self.ctx.contacts.contacts):
            return True
        return gid in self.groups

    def __call__(self, *groups):
        return GroupContext(self, groups)
