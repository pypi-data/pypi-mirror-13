# -*- coding:utf-8 -*-

"""
    Context - manager of all objects relevant to the life-cycle of an Identity.
"""

import json
import errno
import logging

from .filesystem import FileSystem, ChangeLogger
from .event import Event
from .socnet import accounts
from .socnet import (
    Identity,
    IdentityManager,
    GroupManager,
    ContactManager,
    PersonalInfoMgr,
)


log = logging.getLogger(__name__)

device_loaded = Event()


class Context(object):
    __service_contexts = {}
    __user_sessions = {}
    __contexts = []
    is_service_ctx = False
    created = Event()
    destroyed = Event()

    @classmethod
    def get_session(cls, sid=None, create=True):
        __debug__ and log.debug("session requested: " + (sid or "new"))
        if sid in cls.__user_sessions:
            return None, cls.__user_sessions[sid]
        if not create:
            return None, None
        from phen.util import hex_suffix
        sid = hex_suffix("SID")
        cls.__user_sessions[sid] = retv = Context()
        log.info("new session: " + sid)
        return sid, retv

    @staticmethod
    def call_with_sctx(func, tag="twisted", *p, **kw):
        for key in Context.__service_contexts:
            if tag and not key.endswith(tag):
                continue
            func(Context.__service_contexts[key], *p, **kw)

    @staticmethod
    def get_service_context(idhash, account=None, tag="twisted"):
        key = idhash + tag
        ctx = Context.__service_contexts.get(key)
        if ctx:
            return ctx
        ctx = Context.clone_identity_context(idhash, service=True)
        if ctx:
            Context.__service_contexts[key] = ctx
            return ctx
        if not account:
            return
        ctx = Context(account, service=True)
        try:
            if not ctx.load_identity(idhash):
                return
        except:
            return
        Context.__service_contexts[key] = ctx
        return ctx

    @staticmethod
    def clone_identity_context(idhash, prefix=False, service=False):
        for ctx in Context.__contexts[:]:
            # get the identity from the loaded ones
            identity = ctx[idhash, True] if prefix else ctx[idhash]
            if identity is None:
                continue
            new_ctx = Context(ctx.account, service)
            new_ctx.clone(identity)
            return new_ctx
        return None

    @staticmethod
    def get_admin():
        """Return a context with the admin account"""
        if device is None:
            raise RuntimeError("system not yet initialized")
        return Context(device.accounts.admin)

    def __init__(self, account=accounts.unset, service=False):
        if not isinstance(account, accounts.Account):
            raise TypeError("an Account instance was expected")
        self.identity_loaded = Event()
        self.identity_unloaded = Event()
        self.account = account
        self.cid = None
        self.is_service_ctx = service
        self.fs = FileSystem(self)
        self.pim = PersonalInfoMgr(self)
        self.logger = ChangeLogger(self)
        self.identities = IdentityManager(self)
        self.contacts = ContactManager(self)
        self.groups = GroupManager(self)
        self.groups.groups_modified.subscribe(self.fs.rescan_tables)
        self.fs.folder_modified.subscribe(self.groups.folder_modified)
        Context.__contexts.append(self)
        Context.created(self)

        def refresh(*p):
            # print "ref cb:", self, p
            self.contacts.refresh()
            self.groups.refresh()

        self.identity_loaded.subscribe(refresh)
        self.identity_unloaded.subscribe(refresh)

    def __repr__(self):
        return "<ctx {} cid:{} obj:{:x}>".format(
            self.account, self.cidhash[:5] if self.cid else "-----",
            id(self) >> 4
        )

    @property
    def device(self):
        """
            Convenience property to access phen.context.device
        """
        return device

    @property
    def cidhash(self):
        """
            Shortcut to the current identity's hash, evaluating
            to None if there is no identity currently set.
        """
        return self.cid.hash if self.cid else None

    def switch_account(self, account):
        if account == self.account:
            return
        for idhash in list(self.identities.loaded_identities):
            self.unload_identity(idhash)
        self.account = account

    def startup_identity(self):
        self.fs.startup()
        self.logger.setup()
        self.identity_loaded(self)

    def shutdown_identity(self):
        # self.identity_pre_unload(self)
        self.fs.flush()
        self.logger.shutdown()
        self.fs.shutdown()
        cid = self.cid
        self.cid = None
        self.identity_unloaded(self, cid)

    def create_identity(self, passphrase, device=False, **kw):
        if self.cid is not None:
            self.shutdown_identity()
        else:
            self.fs.flush()
        self.cid = self.identities.create(passphrase, **kw)
        exists = self.fs.create_identity_root(device)
        populate = kw.get("populate", 0)
        if not exists and populate:
            from .socnet.initfolder import initialize_identity
            initialize_identity(self, populate)
        log.info("identity '{}' created".format(self.cidhash))
        self.startup_identity()
        return self.cidhash

    def set_default(self):
        if self.account in accounts.invalid:
            raise accounts.InvalidAccount
        cfg = self.account.get_config()
        if not cfg:
            return
        if self.cid is None:
            cfg.pop("default-id", None)
        else:
            cfg["default-id"] = self.cidhash
        self.account.set_config(cfg)

    def clone(self, identity):
        self.identities.clone(identity)
        log.info("identity '{}' cloned".format(identity.hash))
        self.load_identity(identity.hash)

    def load_default(self):
        if self.account in accounts.invalid:
            raise accounts.InvalidAccount
        cfg = self.account.get_config()
        if cfg and "default-id" in cfg:
            return self.load_identity(cfg["default-id"])
        return None

    def get_loaded_identity(self, idhash):
        return self.identities.loaded_identities.get(idhash)

    def get_identity_by_prefix(self, prefix, loaded=False):
        """Search the account for identities with fingerprint starting
        with prefix. Return the Identity object if requested for
        loaded identities, otherwise return its full fingerprint."""
        if loaded:
            idlist = list(self.identities.loaded_identities)
        else:
            idlist = self.account.identities()
        for idhash in idlist:
            if idhash.startswith(prefix):
                return idhash if not loaded else self[idhash]
        return None

    def __getitem__(self, idx):
        if isinstance(idx, tuple):
            return self.get_identity_by_prefix(idx[0], loaded=idx[1])
        return self.get_loaded_identity(idx)

    def load_by_prefix(self, prefix, passphrase=''):
        idhash = self[prefix, False]
        if idhash is not None:
            return self.load_identity(idhash, passphrase)
        return None

    def load_identity(self, idhash, passphrase=''):
        if idhash == self.cidhash:
            return idhash
        if self.cid is not None:
            self.shutdown_identity()
        else:
            self.fs.shutdown()  # folders opened without identity
        self.cid = self.identities.load(idhash, passphrase)
        if self.cid is None:
            log.error("failed to load identity '{}'".format(idhash))
            return None
        log.info("identity '{}' loaded".format(idhash))
        self.startup_identity()
        return idhash

    def unload_identity(self, idhash=None):
        if idhash is None:
            idhash = self.cidhash
        if idhash is None:
            return
        log.info("unloading identity '{}'".format(idhash))
        if not self.identities.unload_identity(idhash):
            log.error("failed to unload identity '{}'".format(idhash))
        else:
            if idhash == self.cidhash:
                self.shutdown_identity()

    def delete_identity(self, idhash=None):
        """
            Remove the identity from the keyring.
        """
        if self.account in accounts.invalid:
            raise accounts.InvalidAccount
        idhash = idhash or self.cidhash
        self.unload_identity(idhash)
        self.account.delete_identity_key(idhash)

    def list_identities(self):
        if self.account in accounts.invalid:
            raise accounts.InvalidAccount
        return self.account.identities()

    def shutdown(self):
        Context.destroyed(self)
        self.unload_identity()
        if self in Context.__contexts:
            Context.__contexts.remove(self)


class DeviceContext(Context):
    def __init__(self):
        Context.__init__(self, accounts.device)
        device_loaded.subscribe(self.device_loaded)

    def device_loaded(self):
        self.accounts = accounts.Manager(self)
        from phen.util import config
        self.cfg = config.load(self.fs, u"device.jcfg", abscence_ok=True)
        self._run_startup_script()
        self._start_service_contexts()

    def _run_startup_script(self):
        startup = self.cfg.get("startup-script")
        if not startup:
            return
        log.info("executing startup script '{}'".format(startup))
        try:
            code = self.fs.open(startup).read()
            exec code in {"device": self}
        except:
            log.exception("while trying to execute startup script")

    def _start_service_contexts(self):
        for account in self.accounts:
            cfg = account.get_config()
            serviced_ids = cfg.get("serviced-ids", [])
            if serviced_ids == "*":
                serviced_ids = account.identities()
            elif not isinstance(serviced_ids, list):
                serviced_ids = [serviced_ids]
            for idhash in serviced_ids:
                Context.get_service_context(idhash, account=account)

    def load_identity(self, passphrase=""):
        """
            Load the device identity from the store.
        """
        if self.cidhash:
            return self.cidhash
        from phen.storage import store
        data = store.device_key()
        if data is None:
            return
        try:
            self.cid = Identity.load(self, passphrase, data=json.loads(data))
            self.identities.loaded_identities[self.cidhash] = self.cid
        except IOError as exc:
            if exc.errno != errno.EACCES:
                raise
            if not passphrase:
                log.error("device is pass-phrase protected, try again")
            else:
                log.error("incorrect pass-phrase")
            raise
        self.fs.startup()
        self.fs.chdir(u"system")  # most files should go here - keep root lean
        device_loaded()
        return self.cidhash

    def load_device_key(self, passphrase=""):
        from phen.storage import store
        from phen.crypto import asym
        data = store.device_key()
        return asym.PrivateKey.load_data(json.loads(data), passphrase)

    def change_device_passphrase(self, pk, passphrase):
        from phen.socnet.identity import save_key
        save_key(self, pk, passphrase)

    def create_identity(self, passphrase, **kw):
        kw["populate"] = 2
        Context.create_identity(self, passphrase, True, **kw)
        log.info("device identity created '{}'".format(self.cidhash))
        device_loaded()
        return self.cidhash

    def setup_test(self):
        self.create_identity("test", key_type='ECC secp192r1', aetherial=True)


device = None


def setup():
    global device
    if device is None:
        device = DeviceContext()
