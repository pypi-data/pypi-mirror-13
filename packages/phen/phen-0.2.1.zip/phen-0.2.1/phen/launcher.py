#!/usr/bin/env python
#-*- coding:utf-8 -*-

"""
    Launches phen from multiple available versions
"""

import os
import sys
import signal
import subprocess

from phen import retcodes


# ignore keyboard interruptions, let the child process them
def sigint(sig, stack):
    pass
signal.signal(signal.SIGINT, sigint)


def run():
    # 1. parse command line
    # 2. read config file, if exists

    retcode = retcodes.start
    while retcode != retcodes.exit:
        # 3. scan data/app folder for which phen version to use
        parts = os.path.realpath(__file__).split(os.path.sep)
        python_path = os.path.sep.join(parts[:-2])
        phen_path = os.path.sep.join(parts[:-1])

        # 4. launch phen from app folder or from this module
        retcode = subprocess.call(["python", phen_path] + sys.argv[1:],
                                  env={"PYTHONPATH": python_path})
        if retcode == retcodes.error:
            # unhandled exception, must blacklist the version used
            break
