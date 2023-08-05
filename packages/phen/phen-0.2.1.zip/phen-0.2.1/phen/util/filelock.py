#!/usr/bin/env python
#-*- coding:utf-8 -*-

import os
import time
import errno


class Filelock:
    def __init__(self, fname, timeout=0, stale=30, sleep=1):
        lockname = fname + ".lock"
        self.__dict__.update(locals())

    def __enter__(self):
        curtime = start = time.time()
        acquired = False
        while not acquired and (
                not self.timeout or curtime < start + self.timeout):
            try:
                os.mkdir(self.lockname)
                acquired = True
            except OSError as exc:
                if exc.errno != errno.EEXIST:
                    raise
                if os.stat(self.lockname).st_mtime + self.stale < curtime:
                    acquired = True
                    os.utime(self.lockname, (curtime, curtime))
                else:
                    time.sleep(self.sleep)
                    curtime = time.time()
        if not acquired:
            raise IOError(errno.EBUSY)
        return self

    def refresh(self):
        curtime = time.time()
        os.utime(self.lockname, (curtime, curtime))

    def __exit__(self, *p):
        os.rmdir(self.lockname)
