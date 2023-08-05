# -*- coding:utf-8 -*-

"""
"""

import logging

from phen.crypto import asym


log = logging.getLogger(__name__)


def save_key(ctx, pk, passphrase):
    """
        Store the identity key.
    """
    from . import accounts
    if ctx.account is accounts.device:
        from six import BytesIO
        data = BytesIO()
        pk.save(data, passphrase)
        from phen.storage import store
        store.device_key(data.getvalue())
    else:
        if ctx.account == accounts.unset:
            raise ValueError("account not set")
        if not ctx.device.cid:
            raise RuntimeError("device not loaded")
        ctx.account.save_identity_key(pk, passphrase)


class Identity:
    def __init__(self, ctx, pk):
        self.ctx = ctx
        self.sync_status = None
        self.inverse_sync_status = None
        self.pk = pk
        self.pub = self.pk.pub
        self.AES_key = self.pk.AES_key
        self.hash = self.pub.hash

    def __repr__(self):
        return "<Id {}>".format(self.hash[:5])

    @staticmethod
    def new(ctx, passphrase, **kw):
        from phen.crypto import key_types
        key_type = kw.get("key_type")
        key_spec = kw.get("key_spec")
        aetherial = kw.get("aetherial")
        if not (key_type or key_spec):
            log.warn("Key type not specified, will chose one at random")
            key_type = next(iter(key_types.keys()))
        if not aetherial:
            pk = asym.PrivateKey.new(key_type, key_spec)
            save_key(ctx, pk, passphrase)
        else:
            if not key_spec:
                key_spec = key_types[key_type]
            if key_spec["type"] != 'ECC':
                raise ValueError("only ECC based identities can be aetherial")
            pk = asym.PrivateKey.new(None, key_spec, secret=passphrase)
        return Identity(ctx, pk)

    def change_passphrase(self, passphrase):
        save_key(self.ctx, self.pk, passphrase)

    @staticmethod
    def clone(ctx, identity):
        return Identity(ctx, identity.pk)

    @staticmethod
    def load(ctx, passphrase, filename=None, data=None, import_key=False):
        if filename:
            with open(filename) as key_file:
                pk = asym.PrivateKey.load(key_file, passphrase)
        else:
            pk = asym.PrivateKey.load_data(data, passphrase)
        if import_key:
            save_key(ctx, pk, passphrase)
        return Identity(ctx, pk)

    def device_list(self, include_in_use=True):
        path = self.subpath("system/devices")
        files = self.ctx.fs.listdir(path)
        if not include_in_use:
            did = self.ctx.device and self.ctx.device.cidhash
        from phen.util import is_idhash
        return [fname for fname in files
                if is_idhash(fname)
                and (include_in_use or did != fname)]

    def load_sync_status(self):
        dev = self.ctx.device
        self.sync_status = {}
        self.inverse_sync_status = {}
        if not dev or dev.cid == self:  # devices don't sync with themselves
            return
        for did in self.device_list():
            try:
                path = self.subpath("system/devices", did, "status")
                status = self.ctx.fs.json_read(path)
                if did == dev.cidhash:
                    self.sync_status = status
                elif dev.cidhash in status:
                    self.inverse_sync_status[did] = status[dev.cidhash]
            except IOError:
                pass
        if __debug__:
            self._debug_last_sync()

    def _debug_last_sync(self):
        dev = self.ctx.device
        from time import ctime
        log.debug("Last synchronizations <our> - <peer>")
        for did in self.sync_status:
            our = ctime(self.sync_status[did])
            if did in self.inverse_sync_status:
                peer = ctime(self.inverse_sync_status[did])
            else:
                peer = "unaware of us" if did == dev.cidhash else "self"
            log.debug("* {}: {} - {}".format(did, our, peer))
        log.debug("Oldest: " + ctime(self.oldest_sync))

    def is_known_by(self, did):
        """Check if the specified device is aware of the one in use."""
        return did in self.inverse_sync_status

    def update_sync_status(self, did, stime=None):
        import time
        if self.sync_status is None:
            self.load_sync_status()
        self.sync_status[did] = stime or time.time()
        dev = self.ctx.device
        assert dev, "update_sync_status requires an active device"
        path = self.subpath("system/devices", dev.cidhash, "status")
        self.ctx.fs.json_write(path, self.sync_status)

    def last_sync(self, did):
        if self.sync_status is None:
            self.load_sync_status()
        return self.sync_status[did] if did in self.sync_status else 0

    @property
    def oldest_sync(self):
        if self.inverse_sync_status is None:
            self.load_sync_status()
        if not self.inverse_sync_status or not self.sync_status:
            return 0
        our = min(self.sync_status.values())
        peers = min(self.inverse_sync_status.values())
        return min(our, peers)

    def subpath(self, *p, **kw):
        """
            Return the full path of a file hosted in this identity's folder.
        """
        if kw:
            return self.ctx.fs.subpath(self.hash, *p, **kw)
        return "/".join(["", self.hash] + list(p))

    def config_file(self, name, json=False):
        """
            Return a config file data from this identity.
        """
        try:
            cfgfn = self.subpath("system/config", name)
            if json:
                return self.ctx.fs.json_read(cfgfn)
            with self.ctx.fs.open(cfgfn) as infile:
                return infile.read().strip()
        except IOError:
            return None

    def sign(self, data):
        """
            Sign the data with the private key, and return the
            base64 representation of the signature
        """
        return self.pk.sign(data)

    def verify(self, data, sign):
        """
            Take the data in the same format it was signed, and
            verify the base64 signature
        """
        return self.pub.verify(data, sign)


class IdentityManager:
    """
        Class responsible for organizing local identities,
        creating new ones, and removing them.
    """

    def __init__(self, ctx):
        self.ctx = ctx
        self.loaded_identities = {}

    def create(self, passphrase, **kw):
        """
            Create a new identity and return its identity hash.
        """
        nid = Identity.new(self.ctx, passphrase, **kw)
        self.loaded_identities[nid.hash] = nid
        return nid

    def clone(self, identity):
        if identity.hash in self.loaded_identities:
            return self.loaded_identities[identity.hash]
        nid = Identity.clone(self.ctx, identity)
        self.loaded_identities[nid.hash] = nid
        return nid

    def load(self, idhash=None, passphrase=''):
        if idhash in self.loaded_identities:
            return self.loaded_identities[idhash]
        cid = self._load(idhash, passphrase)
        if cid is not None:
            self.loaded_identities[idhash] = cid
            return cid

    def _load(self, idhash, passphrase):
        """
            Load an identity or check its passphrase.
        """
        if idhash is None:
            idhash = self.ctx.cidhash
        key_data = self.ctx.account.get_identity_key(idhash)
        oid = Identity.load(self.ctx, passphrase, data=key_data)
        if oid.hash != idhash:
            raise ValueError("corrupted identity ({} != {})"
                             .format(oid.hash, idhash))
        return oid

    def change_id_passphrase(self, idhash=None, old='', passphrase=''):
        """
            Change identity's passphrase.
        """
        # the identity is loaded again to check the old passphrase
        oid = self._load(idhash, old)
        oid.change_passphrase(passphrase)

    def unload_identity(self, idhash=None):
        """
            Unload a previously loaded identity.
        """
        if idhash in self.loaded_identities:
            del self.loaded_identities[idhash]
            return True
        return False
