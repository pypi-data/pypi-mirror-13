#!/usr/bin/env python
#-*- coding:utf-8 -*-

import os
import phen


store = None


def setup():
    os.umask(0o77)
    method = phen.cfg.get("method", 'hostfs')
    root_path = phen.cfg.get("root-path", "/tmp/phen")
    if phen.cfg.get("single-process"):
        net_addr = None
    else:
        net_addr = (
            phen.plugin_cfg("storage", "bind", "127.0.0.1"),
            int(phen.plugin_cfg("storage", "port", 2000))
        )
    device_key = phen.cfg.get("device-key", "device.key")
    global store
    if method == 'hostfs':
        from .hostfs import HostFS
        store = HostFS(device_key, root_path, net_addr)
    elif method == 'sqlite':
        in_memory = phen.plugin_cfg("storage", "in_memory", False),
        from .sqlite import SQLite
        store = SQLite(device_key, root_path, net_addr, in_memory)
    else:
        raise ValueError("unknown storage method")
