# -*- coding:utf-8 -*-

"""Request Handlers:

- handshake:
     0. identification: discovers peer idhash;
     1. essentials: retrieves identity's essentials (during handshake only
        the peer identity [corresponding to the idhash] may be retrieved);
     2. authentication: ensures the peer owns the identity's private key
        and sets the cipher key for subsequent communications;
     3. latency: discovers the roundtrip time and the time offset to the
        peer's system time.

- filexchg:
     4. file: requests the download of a file
     5. block: requests one block for the previously requested file
     6. block data: requests the receival of a block fraction, sent
        repeatedly by the uploader until the block is complete, in
        response to request 5

- protocol:
    7f. in_use: tell the peer that the connection is in use and
        should not be closed
"""

from .protocol import rh, disconnected, ldbg    # noqa
from .handshake import handshake_successful     # noqa
from .filexchg import download                  # noqa
