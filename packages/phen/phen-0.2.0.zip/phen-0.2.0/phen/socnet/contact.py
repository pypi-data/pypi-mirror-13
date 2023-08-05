#!/usr/bin/env python
#-*- coding:utf-8 -*-

"""
    Contact Management

    An identity is said to be a contact when it shares a private group
    with you, and has access to your 'contacts' group.

    The first step in becoming someone's contact is to retrieve vis
    identity basic info, including the 'requests' folder. Then you
    make a request to share a private group, providing a group key.
    The request is accepted if the request file is deleted and you
    have access to the 'contacts' group. If the file is deleted and
    you still can't access the 'contacts' group, it means the other
    user denied the request.

    Alternatively, both parties can agree on a shared passphrase
    off-the-channel, and derive a ECC key from it. Each must then
    create the private group and provide access to each other's
    'contacts' group. Later they should request a change of the
    private group key.
"""

import json

from phen.crypto import asym


#/id/contacts/idxyz
#{
#    "username": user,
#    "idhash": idhash,
#    "update-from": "https://dl.dropboxusercontent.com/u/7545292/",
#    "update-to": "Dropbox" # p2p | http | ftp | pendrive | whatever
#}


#todo: class Contact(Peer):
class Contact(object):
    __valid_fields = "username name state notes key".split()
    username = ""
    name = ""
    state = ''
    notes = ""
    key = ""

    def __init__(self, parent, idhash=None):
        self.parent = parent
        self.idhash = idhash
        if idhash:
            self.load(idhash)

    def load(self, idhash):
        self.idhash = idhash
        with self.parent._contact_file(idhash) as infile:
            json_src = json.loads(infile.read())
        for k in json_src:
            if k not in Contact.__valid_fields:
                json_src.pop(k)
        self.__dict__.update(json_src)
        self.key = asym.PrivateKey.load_data(self.key)

    def confirm_access(self):
        if self.state == 'ACTIVE':
            return True
        cgrp = self.subpath("system/groups/contacts")
        if self.parent.fs.exists(cgrp):
            self.state = 'ACTIVE'
            self.commit()
            return True
        return False

    def commit(self):
        with self.parent._contact_file(self.idhash, 'w') as out:
            out.write(json.dumps({
                k: (getattr(self, k) if k != 'key' else self.key.dump())
                for k in Contact.__valid_fields}))

    def is_active(self):
        return self.state == 'ACTIVE'

    def subpath(self, *p):
        """Return the full path of a contact's hosted file."""
        return "/".join(["", self.idhash] + list(p))

    def can_request(self, fs):
        return fs.access(self.subpath("system/requests"))

    def direct_request(self, ctx, request):
        from .request import generic_request
        return generic_request(ctx, request, route=[self.idhash])


class ContactManager:
    def __init__(self, ctx):
        """Initialize by loading contact list."""
        self.ctx = ctx
        self.contacts = {}
        self.by_username = {}

    def _contact_file(self, idhash, mode='r'):
        path = "/".join([self.path, idhash])
        return self.ctx.fs.open(path, mode)

    def translate_idhash(self, idhash):
        """Try to convert an idhash into a username."""
        if idhash in self.contacts:
            contact = self.contacts[idhash]
            if contact.username:
                return contact.username
        return idhash

    def translate_path(self, path):
        """Try to convert the root folder's idhash into a username."""
        parts = path.split("/")
        if len(parts) > 1 and not parts[0] and parts[1] in self.contacts:
            contact = self.contacts[parts[1]]
            if contact.username:
                parts[1] = contact.username
                return "/".join(parts)
        return path

    def refresh(self):
        """Load the contact list."""
        if not self.ctx.cid:
            return
        self.path = self.ctx.cid.subpath("system/contacts")
        try:
            flist = self.ctx.fs.listdir(self.path)
        except IOError:  # device doesn't have the contact folder
            flist = []
        self.contacts = {
            idhash: Contact(self, idhash)
            for idhash in flist}
        self.by_username = {con.username: con
                            for con in self.contacts.values()
                            if con.username not in self.contacts}
        for contact in self.contacts.values():
            contact.confirm_access()

    def get_by_username(self, username):
        if username in self.by_username:
            return self.by_username[username]
        # fallback to idhash
        return username in self.contacts and self.contacts[username]

    def all_contacts(self):
        return (contact for idhash, contact in self.contacts.items())

    def active_contacts(self):
        return (contact for idhash, contact in self.contacts.items()
                if contact.is_active())

    def __iter__(self):
        return self.all_contacts()

    def __contains__(self, idhash):
        return idhash in self.contacts

    def add_contact_with_secret(self, idhash, secret, **kw):
        if idhash in self.contacts:
            return self.contacts[idhash]
        key_type = kw.get("key_type", 'ECC 224 (secp224r1)')
        key = asym.PrivateKey.new(key_type, secret=secret)
        profile = kw.get("profile")
        return self._add_contact(idhash, key, 'WAITING', profile)

    def add_contact_request(self, route, **kw):
        idhash = route[0]
        if idhash in self.contacts:
            return self.contacts[idhash]
        from .request import request_contact
        msg = kw.get("msg")
        key_type = kw.get("key_type", 'ECC 224 (secp224r1)')
        secret = kw.get("secret")
        key = asym.PrivateKey.new(key_type, secret=secret)
        request_contact(self.ctx,
                        msg=msg,
                        key=key,
                        route=route)
        profile = kw.get("profile")
        return self._add_contact(idhash, key, 'REQUESTED', profile)

    def _add_contact(self, idhash, key, state, profile=None):
        con = Contact(self)
        con.idhash = idhash
        if profile:
            if profile[0]:
                con.username = profile[0]
            if profile[1]:
                con.name = profile[1]
        con.key = key
        con.state = state
        con.commit()
        self.contacts[idhash] = con
        if con.username:
            self.by_username[con.username] = con
        self.ctx.fs.groups(
            self.ctx.cid.subpath("system/groups/contacts"), idhash)
        return con

#    def collect_requests(self):
#        fname = "/".join(("", self.idhash, "contact_request.json")
#        for idhash, reqfname in self.ctx.fs.map_multi(fname).items():
#            try:
#                with self.ctx.fs.open(reqfname) as infile:
#                    req = json.loads(infile.read()))
#            except ValueError:
#                continue
#            if not isinstance(req, dict):
#                continue
#            req['idhash'] = idhash
#            self.requests.append(req)
#
#    def accept_request(self, idprefix):
#        for req in self.requests:
#            if req['idhash'].startswith(idprefix):
#                for key in req:
#                    if key not in Contact.__slots__:
#                        req.pop(key)
#                cont = Contact(req)
#                self.contacts[cont.idhash] = cont
#                if cont.username in self.contacts:
#                    cont.username = ""
#                else:
#                    self.contacts[cont.username] = cont
