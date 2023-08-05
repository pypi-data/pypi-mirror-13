#!/usr/bin/env python
#-*- coding:utf-8 -*-

import json
import shlex

from phen.socnet.request import Dispatcher


class RequestCommands:
    def do_add_contact_request(self, line):
        """add_contact_request <idhash> [<route> ...]

        Requests to be added as a contact.

        """
        if not line:
            return self.do_help("add_contact_request")
        route = shlex.split(line)
        if route[0] in self.ctx.contacts.contacts:
            return self.send("You've already added this identity.")
        if len(route) == 1 and not self.can_request(route[0]):
            return self.send("You don't have permission to send request.")
        profile = self.get_profile(route[0])
        user = raw_input("Username ({}): ".format(profile[0])) or profile[0]
        name = raw_input("Name ({}): ".format(profile[1])) or profile[1]
        msg = raw_input("Message: ")
        self.ctx.contacts.add_contact_request(
            route, [user, name], msg)

    def complete_add_contact_request(self, text, line, start_index, end_index):
        ids = self.list_identities()
        if not text:
            return ids
        return [i for i in ids if i.startswith(text)]

    def do_list_contacts(self, line):
        fmt = "{idhash}: {username} - {name} ({state})"
        self.send("\n".join(
            fmt.format(**con.__dict__)
            for con in self.ctx.contacts.contacts.values()))

    def do_list_requests(self, line):
        d = Dispatcher(self.ctx.cid)
        d.refresh_requests()
        for rid in d.requests:
            if self.color:
                self.send("\x1b[1;32m{}\x1b[0m".format(rid))
            else:
                self.send(rid)
            self.send(json.dumps(d.requests[rid], indent=2))

    def do_request(self, line):
        """request <grant | deny> <request id>

        Perform or veto the action requested.
        """
        args = shlex.split(line)
        if len(args) < 2 or args[0] not in ('grant', 'deny'):
            return self.do_help("request")
        d = Dispatcher(self.ctx.cid)
        d.refresh_requests()
        if args[1] not in d.requests:
            return self.send("Invalid request id.")
        d.dispatch(args[1], args[0] == 'grant')

    def complete_request(self, text, line, start_index, end_index):
        args = line.split()
        word = line[start_index:end_index]
        d = Dispatcher(self.ctx.cid)
        d.refresh_requests()
        if len(args) < 2 or word == args[1]:
            words = ["grant", "deny"]
        else:
            words = d.requests
        return [i for i in words if i.startswith(word)]
