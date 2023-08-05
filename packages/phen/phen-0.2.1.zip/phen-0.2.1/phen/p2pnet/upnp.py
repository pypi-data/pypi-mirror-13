# -*- coding:utf-8 -*-

import re
from subprocess import check_output

external_ip_re = re.compile(r"\nExternalIPAddress.*?(\d+\.\d+\.\d+\.\d+)")
local_ip_re = re.compile(r"\nLocal LAN ip address.*?(\d+\.\d+\.\d+\.\d+)")
mappings_re = re.compile(r"\n\s*(?P<idx>\d+)\s+(?P<prot>UDP|TCP)\s+"
                         r"(?P<port>\d+)->(?P<ip>\d+\.\d+\.\d+\.\d+):"
                         r"(?P<local_port>\d+)\s+'(?P<desc>.*?)'")
upnp_rpc_re = re.compile(r"\n desc: (http:.*?)\n")


class uPNP:
    external_ip = None
    local_ip = None
    mappings = None
    upnp_rpc = None

    def get_state(self):
        if self.upnp_rpc:
            return True
        try:
            out = check_output(["upnpc", "-l"])
        except OSError:
            return False
        matches = upnp_rpc_re.findall(out)
        self.upnp_rpc = len(matches) == 1 and matches[0]
        matches = local_ip_re.findall(out)
        self.local_ip = len(matches) == 1 and matches[0]
        matches = external_ip_re.findall(out)
        self.external_ip = len(matches) == 1 and matches[0]
        matches = [m.groupdict() for m in mappings_re.finditer(out)]
        self.mappings = {int(m["port"]): m for m in matches}
        return True

    def forward(self, port, prot="tcp"):
        self.get_state()
        if not self.upnp_rpc:
            return False
        if port in self.mappings:
            return self.mappings[port]["local_port"] == str(port)
        out = check_output(["upnpc", "-u", self.upnp_rpc, "-a", self.local_ip,
                            str(port), str(port), prot.upper()])
        success = "is redirected to internal" in out
        return success


upnp = uPNP()


if __name__ == '__main__':
    print(upnp.get_state())
    print(upnp.upnp_rpc)
    print(upnp.external_ip)
    print(upnp.local_ip)
    print(upnp.mappings)
    print(upnp.forward(12345))
