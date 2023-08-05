# -*- coding:utf-8 -*-

import os
import logging


log = logging.getLogger(__name__)


def is_port_free(host, port, dgram=False):
    import socket
    proto = socket.SOCK_DGRAM if dgram else socket.SOCK_STREAM
    sck = socket.socket(socket.AF_INET, proto)
    sck.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
    try:
        sck.bind((host, port))
    except socket.error:
        return False
    del sck
    return True


def launch_browser(url):
    import sys
    import subprocess
    if sys.platform[:3] == "win":
        os.startfile(url)
    elif sys.platform == "darwin":
        subprocess.Popen(["open", url])
    else:
        try:
            subprocess.Popen(["xdg-open", url])
        except OSError:
            log.error("could not launch browser")
