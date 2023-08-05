#!/usr/bin/env python
#-*- coding:utf-8 -*-

"""
    Personal Information Manager
"""


class PersonalInfoMgr:
    def __init__(self, ctx):
        self.ctx = ctx

    def get_names(self, idhash):
        """
            Return user and real name, if available.
        """
        profile_path = self.ctx.fs.subpath(idhash, "profile")
        fmeta = self.ctx.fs.exists(profile_path)
        if fmeta is False:
            return "nobody", "nobody"
        elif fmeta.is_folder:
            fmeta = fmeta.folder_fmeta
        return tuple(fmeta.xattr.get(k, "nobody") for k in ("user", "name"))
