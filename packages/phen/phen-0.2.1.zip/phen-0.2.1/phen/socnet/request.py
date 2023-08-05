#!/usr/bin/env python
#-*- coding:utf-8 -*-

import os
import json

from functools import wraps
from binascii import b2a_base64, a2b_base64

from phen.crypto import asym


def request_routing(payload_dest, payload):
    return {"request": "route",
            "to": payload_dest,
            "payload": payload}


def onionize(ctx, route, dest, request):
    if route:
        hop_id, hop = onionize(ctx, route, route.pop(-1), request)
        request = request_routing(hop_id, hop)
    else:
        request["from"] = ctx.cidhash
        request["nonce"] = os.urandom(8).encode("hex")
        request["signature"] = ctx.cid.sign(request["nonce"])
    key = ctx.get_pubkey(dest)
    return dest, b2a_base64(key.encrypt_bigstr(json.dumps(request)))[:-1]


def routing(func):
    @wraps(func)
    def routed(ctx, *p, **kw):
        reply = kw.pop("reply", False)
        route = kw.pop("route")[:]
        if reply:
            rev_route = route[::-1]
            origin = route.pop(0)
            back_route = onionize(ctx, rev_route, origin, "reply")[1]
        wrapped_request = func(*p, **kw)
        if reply:
            wrapped_request["back_route"] = back_route
        dest, request = onionize(ctx, route, route.pop(-1), wrapped_request)
        fname = ctx.fs.subpath(dest, "system/requests", rid=True)
        tgrp = ctx.groups.set_initial(u'public')
        with ctx.fs.open(fname, 'w') as out:
            out.write(request)
        ctx.groups.set_initial(tgrp)
        return fname
    return routed


@routing
def generic_request(dct):
    return dct


@routing
def request_contact(msg, key):
    return {"request": "contact",
            "msg": msg,
            "key": key.dump()}


#print "\nDirect route"
#request_contact(None, "me", "moo", "secret", route=["a"])
#
#print "\nOne hop"
#request_contact(None, "me", "moo", "secret", route=["a", "b"])
#
#print "\nSeveral hops, expect reply"
#request_contact(None,
#                sender="d",
#                msg="...",
#                key="key",
#                route=["a", "b", "c", "d"],
#                reply=True)


class Dispatcher:
    def __init__(self, ctx):
        self.ctx = ctx
        self.requests = {}

    def refresh_requests(self):
        req_folder = self.ctx.cid.subpath("system/requests")
        for req_id in self.ctx.fs.listdir(req_folder):
            if req_id == ".access" or req_id in self.requests:
                continue
            fpath = "/".join((req_folder, req_id))
            try:
                with self.ctx.fs.open(fpath) as req_file:
                    enc_req = a2b_base64(req_file.read())
                    req = json.loads(self.ctx.cid.pk.decrypt_bigstr(enc_req))
            except:
                continue   # ignore, for debugging
#                self.ctx.fs.unlink(fpath)
            self.requests[req_id] = req
            # todo: signal new request
        return self.requests

    def dispatch(self, req_id, grant=False, *p, **kw):
        req = self.requests.pop(req_id)
        req_fname = self.ctx.cid.subpath("system/requests", req_id)
        self.ctx.fs.unlink(req_fname)
        method = ["deny_", "grant_"][bool(grant)] + req["request"]
        dispatcher = getattr(self, method, None)
        if dispatcher:
            try:
                retv = dispatcher(req, *p, **kw)
            except:
                raise  # debugging
                retv = None
            return retv

    def grant_contact(self, req):
        profile = self.ctx.get_profile(req["from"])
        contact = self.ctx.contacts._add_contact(
            req["from"],
            asym.PrivateKey.load_data(req["key"]),
            'WAITING',
            profile=profile)
        return contact.confirm_access()

    def grant_route(self, req):
        fname = self.ctx.fs.subpath(req["to"], "system/requests", rid=True)
        with self.ctx.groups(u'public'):
            with self.ctx.fs.open(fname, 'w') as out:
                out.write(req["payload"])
        return True
