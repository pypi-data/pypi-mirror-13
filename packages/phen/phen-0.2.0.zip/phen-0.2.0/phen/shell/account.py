# -*- coding:utf-8 -*-

import json
import shlex

from .util import input_passphrase
from .base import ProtectedSubCmd, protected, shlexed


class Accounts(ProtectedSubCmd):
    """
        Account management.
    """
    cmdname = "acc"

    def __init__(self, parent, *p, **kw):
        ProtectedSubCmd.__init__(self, *p, **kw)
        self.parent = parent
        self.ctx = parent.ctx

    def preloop(self):
        self.update_prompt()

    def update_prompt(self):
        if self.color:
            pfmt = "\x1b[1;32macc)\x1b[1;34m{}\x1b[0m$ "
        else:
            pfmt = "acc){}$ "
        self.prompt = pfmt.format(self.ctx.account.name)

    def do_switch(self, line):
        """switch <account>

        Switch to the specified account

        """
        if not self.ctx.account.is_admin:
            if not line:
                return self.send("Specify the account to switch to.")
            passphrase = input_passphrase(self)
            account = self.ctx.device.accounts[line]
            if not account.check_passphrase(passphrase):
                return self.send("Incorrect pass-phrase")
        else:
            if not line:
                return self.onecmd("list")
            accounts = self.ctx.device.accounts.list()
            if line not in accounts:
                return self.send(line, "not in", repr(accounts))
            account = self.ctx.device.accounts[line]
        self.ctx.switch_account(account)
        self.update_prompt()
        self.send("Switched to account '{}'".format(line))

    @protected
    def complete_switch(self, text, *p):
        return [acc for acc in self.ctx.device.accounts.list()
                if acc.startswith(text)]

    @protected
    def do_create(self, line):
        """create <account>

        Create a new account

        """
        if not line:
            return self.do_help("create")
        account = self.ctx.device.accounts[line]
        if not account.create():
            return self.send("Account '{}' already existed".format(line))
        return self.send("Account '{}' successfully created".format(line))

    @protected
    def do_destroy(self, line):
        """destroy <account>

        Destroy an account and all its identities (their data are kept)

        """
        if not line:
            return self.do_help("destroy")
        accounts = self.ctx.device.accounts.list()
        if line not in accounts:
            return self.send(line, "not in", repr(accounts))
        self.ctx.device.accounts[line].destroy()
        return self.send("Account '{}' successfully destroyed".format(line))

    complete_destroy = complete_switch

    @protected
    def do_list(self, line):
        """list

        Lists all registered accounts

        """
        for account in self.ctx.device.accounts.list():
            self.send(account)
            for idhash in self.ctx.device.accounts[account].identities():
                user, name = self.ctx.pim.get_names(idhash)
                self.send("   {}: {} - {}".format(idhash, user, name))

    def do_passwd(self, line):
        """Usage: passwd [<account>] [-d]

        Change the current (or other) account's pass-phrase.
        To remove access to the account, include the -d option.

        """
        from phen.docopt import docopt, DocoptExit
        try:
            args = shlex.split(line)
            opts = docopt(self.do_passwd.__doc__, args, help=False)
        except DocoptExit:
            return self.do_help("passwd")
        if opts['<account>']:
            account = self.ctx.device.accounts[opts['<account>']]
        else:
            account = self.ctx.account
        cfg = account.get_config()
        if not self.ctx.account.is_admin:
            if account != self.ctx.account:
                return self.send("Only admin can change other accounts")
            curpp = input_passphrase(self, "Type in the current pass-phrase: ")
            if not account.check_passphrase(curpp, cfg):
                return self.send("Incorrect pass-phrase")
        if opts['-d']:
            account.change_passphrase(cfg=cfg)
            self.send("Access to account '{}' removed".format(account.name))
            return
        passphrase = input_passphrase(self, "Type in the new pass-phrase: ")
        confirm = input_passphrase(self, "Confirm the new pass-phrase: ")
        if passphrase != confirm:
            return self.send("Pass-phrases did not match")
        account.change_passphrase(passphrase, cfg)
        self.send("Pass-phrase updated")

    def do_config(self, line):
        """Usage: config [(<option> <value>)] [<account>]
                  config [(-d <option>)] [<account>]

        Show, change, or remove (-d) account configuration options.

        """
        from phen.docopt import docopt, DocoptExit
        try:
            args = shlex.split(line)
            opts = docopt(self.do_config.__doc__, args, help=False)
        except DocoptExit:
            return self.do_help("config")
        if opts['<account>']:
            account = self.ctx.device.accounts[opts['<account>']]
        else:
            account = self.ctx.account
        if not self.ctx.account.is_admin and account != self.ctx.account:
            return self.send("Only admin can change other accounts")
        if not account.exists():
            return self.send("Account must be created first")
        cfg = account.get_config()
        if opts['-d']:
            cfg.pop(opts['<option>'], None)
            account.set_config(cfg)
        elif opts['<option>'] is not None:
            try:
                value = json.loads(opts['<value>'])
            except:
                value = opts['<value>']
            cfg[opts['<option>']] = value
            account.set_config(cfg)
        return self.send(json.dumps(cfg, indent=2))

    @shlexed
    def do_motd(self, args):
        """Usage: motd <+ | * | - | account> ["message" | -f file]

        Change or erase the message of the day.
        Examples:
          motd -                # clears the motd from the current account
          motd *                # clears the motd from all accounts
          motd * "Welcome!"     # sets the motd for all accounts
          motd + "Hello!"       # sets the motd for all but the admin account
          motd bob -f motd.txt  # sets bob's motd with a message from a file

        """
        if not args:
            return self.do_help("motd")
        message = ""
        if args[0] == '-':
            accounts = [self.ctx.account]
        else:
            if not self.ctx.account.is_admin:
                if args[0] != self.ctx.account.name:
                    return self.send("Only admin can change other accounts")
            if args[0] not in '*+':
                accounts = [self.ctx.account]
            else:
                accounts = list(self.ctx.device.accounts)
            if len(args) > 1:
                if args[1] == '-f':
                    if len(args) < 3:
                        return self.send("Message file path missing")
                    try:
                        message = self.ctx.fs.open(args[2], 'rd').read()
                    except IOError as exc:
                        return self.send(exc)
                else:
                    message = args[1]
        for account in accounts:
            if account.is_admin and args[0] == '+':
                continue
            cfg = account.get_config()
            if message:
                cfg["motd"] = message
            else:
                cfg.pop("motd", None)
            account.set_config(cfg)
            self.send(account.name + ": motd updated")
