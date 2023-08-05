# -*- coding:utf-8 -*-

"""
    View of another user's Identity
"""

from phen.crypto.asym import PublicKey


class Peer:
    def __init__(self, ctx, idhash):
        self.idhash = idhash
        self.ctx = ctx

    def get_pubkey(self):
        from phen.storage import store
        with store.load((self.idhash, "public.key")) as key_file:
            retv = PublicKey.load(key_file)
        return retv

    def can_request(self):
        req_path = self.ctx.fs.subpath(self.idhash, "system/requests")
        return self.ctx.fs.access(req_path)

    def get_profile(self):
        """
            Try to get basic profile information from an identity.
        """
        # todo: profile module
        profile_path = self.ctx.fs.subpath(self.idhash, "profile")
        fmeta = self.ctx.fs.exists(profile_path)
        if fmeta is not None:
            return tuple(fmeta.xattr[k] for k in ("user", "name"))
        return "nobody", "Nobody"
