# -*- coding:utf-8 -*-

from .util import input_passphrase, input_key_specs
from .base import ProtectedSubCmd, requires_cid


class Identities(ProtectedSubCmd):
    """
        Identity management.
    """
    cmdname = "id"

    def __init__(self, parent, *p, **kw):
        ProtectedSubCmd.__init__(self, *p, **kw)
        self.parent = parent
        self.ctx = parent.ctx

    def preloop(self):
        self.update_prompt()

    def update_prompt(self):
        if self.color:
            pfmt = "\x1b[1;32mid)\x1b[1;34m{}\x1b[0m$ "
        else:
            pfmt = "id){}$ "
        idhash = self.ctx.cidhash or "-=-=-"
        self.prompt = pfmt.format(idhash[:5])

    @requires_cid
    def do_who(self, line):
        """who

        Tell what is the identity in use.

        """
        user, name = self.ctx.pim.get_names(self.ctx.cidhash)
        self.send("{}: {} - {}".format(self.ctx.cidhash, user, name))

    def do_default(self, line):
        """default

        Set the current identity as the default to be loaded
        at startup for the current account.

        """
        self.ctx.set_default()
        if self.ctx.cid is None:
            self.send("No identity will be loaded when starting.")
        else:
            self.send("Will load [{}] when starting (must not be protected)."
                      .format(self.ctx.cidhash[:5]))

    def do_list(self, line):
        """list

        List all identities from the current account

        """
        ids = self.ctx.list_identities()
        if self.ctx.account.is_admin:
            self.send("Can load device identity {}"
                      .format(self.ctx.device.cidhash))
        if not ids:
            return self.send("The '{}' account has no identities yet"
                             .format(self.ctx.account))
        for idhash in ids:
            user, name = self.ctx.pim.get_names(idhash)
            self.send("{}: {} - {}".format(idhash, user, name))

    def _load_devid(self, line):
        if line not in (u'device', self.ctx.device.cidhash):
            return False
        idhash = self.ctx.device.cidhash
        if idhash in self.ctx.identities.loaded_identities:
            self.ctx.load_identity(idhash)
        else:
            self.ctx.clone(self.ctx.device.cid)
        self.update_prompt()
        self.send("Device identity '{}' selected".format(idhash))
        return True

    def _load_id(self, line, passphrase):
        idhash = self.ctx.load_by_prefix(line, passphrase)
        if not idhash:
            for idhash2 in self.ctx.list_identities():
                user, name = self.ctx.pim.get_names(idhash2)
                if line == user or line == name:
                    idhash = self.ctx.load_identity(idhash2, passphrase)
                    break
        return idhash

    def _load_id_interaction(self, line):
        idhash = None
        passphrase = ""
        for cnt in range(4):
            try:
                idhash = self._load_id(line, passphrase)
            except IOError:
                if cnt:
                    self.send("Incorrect pass phrase.")
                if cnt != 3:
                    passphrase = input_passphrase(self)
            except ValueError:
                self.send("Corrupted identity.")
            if idhash:
                break
        return idhash

    def do_load(self, line):
        """load (<fingerprint-prefix> | <user-name> | device)

        Load the specified identity

        """
        if not line:
            self.do_help("load")
            return self.onecmd("list")
        if self.ctx.account.is_admin and self._load_devid(line):
            return
        idhash = self._load_id_interaction(line)
        if not idhash:
            return self.send("Could not load the specified identity")
        self.update_prompt()
        self.send("Identity '{}' loaded".format(idhash))

    def complete_load(self, text, *p):
        if self.ctx.account.is_admin:
            devid = ['device', self.ctx.device.cidhash]
        else:
            devid = []
        return [idhash for idhash in self.ctx.list_identities() + devid
                if idhash.startswith(text)]

    def do_unload(self, line):
        """unload [<fingerprint-prefix>]

        Unload an identity; unload the one currently loaded if none specified.

        """
        if not (line or self.ctx.cid):
            return self.send("No identity currently in use")
        idhash = line or self.ctx.cidhash
        self.ctx.unload_identity(idhash)
        self.send("Identity '{}' unloaded".format(idhash))
        self.update_prompt()

    def do_create(self, line):
        """create

        Create a new identity

        """
        if line:
            return self.do_help("create")
        key_type, passphrase, aetherial = input_key_specs(self)
        if key_type is None:
            return self.send("Pass-phrases did not match")
        idhash = self.ctx.create_identity(passphrase, key_type=key_type,
                                          aetherial=aetherial)
        if not idhash:
            return self.send("Could not create the identity")
        self.update_prompt()
        self.send("Identity '{}' created".format(idhash))

    def do_destroy(self, line):
        """destroy <fingerprint-prefix>

        Destroy an identity (its data are kept)

        """
        if not line:
            return self.do_help("destroy")
        ids = self.ctx.list_identities()
        if line not in ids:
            return self.send(line, "not in", repr(ids))
        self.ctx.delete_identity(line)
        return self.send("Identity '{}' destroyed".format(line))

    complete_destroy = complete_load

    @requires_cid
    def do_passwd(self, line):
        """passwd

        Change the current identity's pass-phrase.

        """
        curpp = input_passphrase(self, "Type in the current pass-phrase: ")
        isdev = self.ctx.cidhash == self.ctx.device.cidhash
        try:
            if isdev:
                pk = self.ctx.device.load_device_key(curpp)
            else:
                self.ctx.identities._load(self.ctx.cidhash, curpp)
        except IOError:
            return self.send("Incorrect pass-phrase")
        newpp = input_passphrase(self, "Type in the new pass-phrase: ")
        confirm = input_passphrase(self, "Confirm the new pass-phrase: ")
        if newpp != confirm:
            return self.send("Pass-phrases did not match")
        if isdev:
            self.ctx.device.change_device_passphrase(pk, newpp)
        else:
            self.ctx.identities.change_id_passphrase(
                self.ctx.cidhash, curpp, newpp
            )
        self.send("Pass-phrase updated")
