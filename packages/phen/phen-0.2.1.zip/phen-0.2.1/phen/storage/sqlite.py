#!/usr/bin/env python
#-*- coding:utf-8 -*-

"""
    Storage in a SQLite database (proof of concept, should not be used)
"""

import os
import sqlite3 as sql
from six import StringIO
from twisted.internet import reactor, threads

from .acc_ctrl import AccessController


SQL_INITIALIZATION = """
    CREATE TABLE IF NOT EXISTS files (
       idhash TEXT NOT NULL,
       fid TEXT NOT NULL,
       data BLOB,
       PRIMARY KEY (idhash, fid)
    );
"""


class SQLite(AccessController):
    def __init__(self, dev_key, root_path, net_addr=None, memory=False):
        AccessController.__init__(self, root_path, net_addr, lock=False)
        self.dev_key = dev_key
        self.blocks = {}
        self.temp_files = {}
        dbname = ":memory:" if memory else (self.root.fs + ".db")
        self.sqlconn = threads.blockingCallFromThread(reactor,
                                                      sql.connect, dbname)
        self.sqlexec(SQL_INITIALIZATION)
        self.set_owner = False

    def sqlexec(self, statement, parameters=None):
        def exe_in_rthread():
            with self.sqlconn:
                if parameters is None:
                    self.sqlconn.execute(statement)
                else:
                    self.sqlconn.execute(statement, parameters)
        reactor.callFromThread(exe_in_rthread)

    def curexec(self, statement, parameters=None, one=True):
        def exe_in_rthread():
            cur = self.sqlconn.cursor()
            if parameters is None:
                cur.execute(statement)
            else:
                cur.execute(statement, parameters)
            if one:
                return cur.fetchone()
            return cur.fetchall()
        return threads.blockingCallFromThread(reactor, exe_in_rthread)

    def shutdown(self):
        AccessController.shutdown(self)
        reactor.callFromThread(self.sqlconn.close)

    def device_key(self, data=None):
        path = os.path.join(self.root.path, self.dev_key)
        if data is None:
            if os.path.exists(path):
                with open(path, 'rt') as kfile:
                    return kfile.read()
        else:
            with open(path, 'wb') as out:
                out.write(data)
            os.chmod(path, 0o600)

    def temp_storage(self, fid_pair):
        """
            return a path for data to be stored outside the database
        """
        idhash, fid = fid_pair
        return os.path.join(self.root.fs, idhash, fid)

    def list_root(self):
        rows = self.curexec("SELECT idhash FROM files WHERE fid='root';",
                            one=False)
        return [row[0] for row in rows]

    def is_available(self, fid_pair, partial=False):
        """
            Check the availability of a file.
        """
        row = self.curexec(
            "SELECT COUNT(*) FROM files WHERE idhash=? AND fid=?;", fid_pair
        )
        if row is None or row[0] < 1:
            if not partial:
                return False
            path = self.temp_storage(fid_pair)
            if os.path.exists(path + ".blocks"):
                return 'partial'
        return True

    def local_data_fid(self, fid_pair, identity, description):
        """
            Transform a genuine fid into one for local data storage.
        """
        from phen.util import bin2idhash
        from hashlib import sha256
        h = sha256(fid_pair[1] + identity.hash + description)
        return ("local", bin2idhash(h.digest()))

    def size(self, fid_pair):
        row = self.curexec(
            "SELECT LENGTH(data) FROM files WHERE idhash=? AND fid=?;",
            fid_pair
        )
        if row is None:
            return -1
        return row[0]

    def load(self, fid_pair, identity=None):
        #if identity:
        #    decrypt
        row = self.curexec(
            "SELECT data FROM files WHERE idhash=? AND fid=?;", fid_pair
        )
        if row is None:
            raise IOError("file not available")
        retv = StringIO(row[0])
        retv.close = lambda: 0
        retv.__enter__ = lambda: retv
        retv.__exit__ = lambda x, y, z: 0
        return retv

    def store(self, fid_pair, identity=None, mode='wb', folder=False):
        #if identity:
        #    encrypt
        idhash, fid = fid_pair
        self.sqlexec("INSERT OR REPLACE INTO files(idhash, fid)"
                     "VALUES (?, ?);", fid_pair)
        self.temp_files[fid_pair] = retv = StringIO()
        retv.close = lambda: (
            0 if not folder else self.store_tempfile(retv, fid_pair)
        )
        retv.__enter__ = lambda: retv
        retv.__exit__ = lambda x, y, z: retv.close()
        return retv

    def unlock(self, folder, mtime, keep_history=False):
        """
            Release folder from exclusive use.
        """
        AccessController.unlock(self, folder, mtime)

    def remove(self, fid_pair):
        idhash, fid = fid_pair
        self.sqlexec("DELETE FROM files WHERE idhash=? AND fid=?;", fid_pair)

    def new_tempfile(self):
        retv = StringIO()
        retv.close = lambda: 0
        retv.__enter__ = lambda: retv
        retv.__exit__ = lambda x, y, z: 0
        return retv

    def store_tempfile(self, tempfile, fid_pair):
        idhash, fid = fid_pair
        data = sql.Binary(tempfile.getvalue())
        self.sqlexec(
            "INSERT OR REPLACE INTO files(idhash, fid, data)"
            "VALUES (?, ?, ?);", (idhash, fid, data)
        )
        if fid_pair in self.temp_files:
            del self.temp_files[fid_pair]

    def open_blocks(self, fid_pair, mode='r+b', restart=False):
        from .blocks import BlocksManager
        if fid_pair in self.blocks:
            return self.blocks[fid_pair]
        try:
            path = self.temp_storage(fid_pair) + ".blocks"
            blocks = open(path, mode)
        except IOError:
            return 'done'
        self.blocks[fid_pair] = BlocksManager(blocks, path, restart)
        return self.blocks[fid_pair]

    def close_blocks(self, fid_pair, remove):
        if fid_pair not in self.blocks:
            return False
        self.blocks.pop(fid_pair).finished(remove)
