# -*- coding:utf-8 -*-

"""
    Initial Identity Folder Structure
"""

import random


# minimal set of public files required to personalize
# an identity and to be able to contact it
essentials = [
    u".*.connection$",  # device
    u"profile$/.*",
    u"system$/devices$/.*",
    # "system$/proxies$/.*",
    u"system$/requests/.access",
]
# additionally, all devices and proxies' essentials (one
# recursion level) should be included


def initialize_user(ctx):
    """Create the initial files for a user."""
#    with ctx.groups(u'public'):
#        ctx.fs.mkdir("profile")
#        ctx.fs.mkdir("system/requests")
#        # user has to explicitly give access permissions in requests/.access
    with ctx.groups():
        ctx.fs.mkdir(u"system/contacts")


default_connection = {
    "method": "inet",
    "proto": "tcp",
    "host": "",
    "port": 0,
}

default_adapter = {
    "method": "inet",
    "auto": False,
    "proto": "tcp",
    "host": "0.0.0.0",
    "port": 0,
}


def initialize_device(ctx):
    """Create the initial files for a synchronization node."""
    from phen.util import net
    for i in range(10):
        port = random.randint(1024, 65536)
        if net.is_port_free("0.0.0.0", port):
            break
    default_connection["port"] = port
    default_adapter["port"] = port
    with ctx.groups():
        # note: user has to make the connection files public
        ctx.fs.json_write(u"default.connection", default_connection)
        ctx.fs.chdir(u"system")
        ctx.fs.mkdir(u"adapters")
        ctx.fs.json_write(u"adapters/default.adapter", default_adapter)


def initialize_identity(ctx, idtype):
    """Create the initial files for the identity.

    `ctx.fs.curdir` should point to the identity's
    folder (the default right after creation)
    """
    if idtype == 1:
        return initialize_user(ctx)
    if idtype == 2:
        return initialize_device(ctx)
