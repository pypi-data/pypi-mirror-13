# -*- coding:utf-8 -*-

from phen.util import path_join as pj


class InvalidAccount(RuntimeError):
    """Write operations with unset account are forbbiden"""


class Account:

    is_admin = False
    default_config = {"passphrase": ""}

    def __init__(self, base_path, name):
        self.name = name
        if name == 'admin':
            self.is_admin = True
        if base_path is None:
            # keep the other attributes undefined, as their
            # access on the special objects must raise an exception
            return
        self.path = pj(base_path, name)
        from phen.context import device
        self.ctx = device

    def __repr__(self):
        return "acc:" + self.name

    def __eq__(self, oth):
        if not isinstance(oth, Account):
            return False
        return self.name == oth.name

    def exists(self):
        return self.ctx.fs.exists(self.path)

    def create(self):
        if self.ctx.fs.exists(self.path):
            return False
        self.ctx.fs.makedirs(self.path)
        self.set_config(self.default_config)
        return True

    def destroy(self):
        if not self.ctx.fs.exists(self.path):
            return False
        self.ctx.fs.rmtree(self.path)
        return True

    def get_config(self):
        from phen.util import config
        path = pj(self.path, "prefs.jcfg")
        return config.load(self.ctx.fs, path, abscence_ok=True)

    def set_config(self, config):
        path = pj(self.path, "prefs.jcfg")
        self.ctx.fs.json_write(path, config)

    def check_passphrase(self, passphrase, cfg=None):
        acc = cfg if cfg is not None else self.get_config()
        from hashlib import sha256
        passphrase = sha256(passphrase.encode("utf8")).hexdigest()
        return acc and passphrase == acc.get("passphrase")

    def change_passphrase(self, passphrase=None, cfg=None):
        acc = cfg if cfg is not None else self.get_config()
        if passphrase is None:
            acc["passphrase"] = ""
        else:
            from hashlib import sha256
            acc["passphrase"] = sha256(passphrase.encode("utf8")).hexdigest()
        self.set_config(acc)
        return True

    def identities(self):
        """
            List account identities
        """
        from phen.util import is_idhash
        files = self.ctx.fs.listdir(self.path)
        return [name for name in files if is_idhash(name)]

    def save_identity_key(self, pk, passphrase):
        path = pj(self.path, pk.pub.hash)
        with self.ctx.groups():  # make sure it will be private
            pk.fs_save(self.ctx.fs, path, passphrase)

    def get_identity_key(self, idhash):
        path = pj(self.path, idhash)
        if not self.ctx.fs.exists(path):
            raise LookupError("identity '{}' not found in account '{}'"
                              .format(idhash, self.name))
        return self.ctx.fs.json_read(path)

    def delete_identity_key(self, idhash):
        path = pj(self.path, idhash)
        if not self.ctx.fs.exists(path):
            raise LookupError("identity '{}' not found in account '{}'"
                              .format(idhash, self.name))
        self.ctx.fs.unlink(path)


unset = Account(None, "-=-")
device = Account(None, "dev")
invalid = (unset, device)


class Manager:
    def __init__(self, ctx):
        self.ctx = ctx
        self.path = ctx.cid.subpath(u"system/accounts")
        self.admin = Account(self.path, "admin")
        if not self.ctx.fs.exists(self.path):
            self.ctx.fs.mkdir(self.path)
            self.admin.create()

    def list(self):
        """
            List accounts
        """
        if self.ctx.cid is None:
            return []
        return self.ctx.fs.listdir(self.path)

    def __iter__(self):
        return (self[acc] for acc in self.list())

    def __getitem__(self, key):
        return Account(self.path, key)
