# -*- coding:utf-8 -*-

"""
    Miscelaneous utilities.
"""

import os
import re
import six
import random
import base64


def path_join(*p):
    return u"/".join(p)


def bin2idhash(bin):
    return base64.urlsafe_b64encode(bin)[:-1].decode("ascii")


def idhash2bin(idhash):
    return base64.urlsafe_b64decode(idhash.encode("ascii") + b"=")


def obscure(text):
    if not text:
        return text
    if isinstance(text, bytes):
        text = bytearray(text)
    else:
        text = bytearray(text, "utf8")
    pad = 0x10 - (len(text) & 0xf)
    pad += 3 - (len(text) + pad) % 3
    text = text[::-1] + bytearray(range(1, pad + 1))
    for i in range(1, len(text)):
        text[i] ^= text[i - 1] ^ 42
    return base64.b64encode(text)


def clarify(obscured):
    try:
        tmp = bytearray(base64.b64decode(obscured))
        for i in range(len(tmp) - 1, 0, -1):
            tmp[i] ^= tmp[i - 1] ^ 42
        tmp = tmp[:-tmp[-1]]
    except:
        return obscured
    return tmp[::-1].decode("utf8")


def convert_to_unicode(string):
    """
        Convert the given string to unicode if it is not already.
    """
    if not isinstance(string, six.text_type):
        for enc in "utf8", "iso-8859-1":
            try:
                string_ = string.decode(enc)
                break
            except UnicodeDecodeError:
                pass
    return string_


hash_re = re.compile(r"[0-9a-zA-Z_-]{43}")
idhash_re = re.compile(r"^[0-9a-zA-Z_-]{43}$")


def is_idhash(s):
    return idhash_re.match(s) is not None


def shorten_hashes(msg):
    return hash_re.sub(lambda m: "[" + m.group(0)[:5] + "]", msg)


def fill_io_error(code, *path):
    """
        Return an appropriately filled IOError exception.
    """
    if path and isinstance(path[0], list):
        path = (o.name for o in path[0])  # assume it is a traversed path
    path = "/".join(path)
    return IOError(code, os.strerror(code), shorten_hashes(path))


def cvt_to_zipfile(out):
    import zipfile
    if not hasattr(out, 'write'):
        out = open(out, 'wb')
    # now out should be one of: file, StringIO, ByteIO, or ZipFile
    if not isinstance(out, zipfile.ZipFile):
        out = zipfile.ZipFile(out, 'w', zipfile.ZIP_DEFLATED)
    return out


fid_names = {}


def fid2name(fid_pair, name=None):
    """
        Convert a fid pair to a file name, if it is known.

        Helper function to show more meaningful debug messages,
        but should not be used in production for privacy.
    """
    if name is not None:
        if fid_pair not in fid_names:
            fid_names[fid_pair] = name
        return
    if __debug__ and fid_pair in fid_names:
        return fid_names[fid_pair]
    return fid_pair[0][:5] + "::" + fid_pair[1][:5]


def hex_suffix(txt):
    """
        Append a random hex suffix.
        Note that it has variable length.
    """
    return txt + hex(random.getrandbits(64))[1:-1]


def strip_hex_suffix(txt):
    """
        Strip a suffix generated with `hex_suffix`.
    """
    return txt[:txt.rfind("x")]


seconds = [
    (("y", "year"), 365 * 24 * 60 * 60),
    (("mon", "month"), 30 * 24 * 60 * 60),
    (("w", "week"), 7 * 24 * 60 * 60),
    (("d", "day"), 24 * 60 * 60),
    (("h", "hour"), 60 * 60),
    (("min", "minute"), 60),
    (("s", "sec", "second"), 1),
]

seconds_by_unit = dict(sum(
    [[(k, s) for k in tup] for tup, s in seconds],
    []
))


def str_to_seconds(spec):
    """
        Convert a time specification to number of seconds.
        Months and years are defined as 30 and 365 days.

        Examples:
            "2 days, 1 hour, and 32 seconds", "2d 1h 32s", "2d1h32"
    """
    retv = 0
    for value, unit in re.findall(r"\s*(\d+)\s*([a-z]*),?", spec.lower()):
        value = int(value)
        if unit != "s":
            unit = unit.rstrip("s")
        retv += value * seconds_by_unit.get(unit, 1)
    return retv


def seconds_to_str(secs, abbr=False, sep=", ", last="and ", ignore=()):
    parts = []
    for tup, s in seconds:
        if tup[0] in ignore:
            continue
        value, secs = divmod(secs, s)
        if not value:
            continue
        if abbr:
            unit = tup[0]
        else:
            unit = tup[-1] + ("s" if value > 1 else "")
        parts.append("%i %s" % (value, unit))
    if not parts:
        return "0 " + ("s" if abbr else "seconds")
    if last:
        if len(parts) > 2:
            parts[-1] = last + parts[-1]
        else:
            return (" " + last).join(parts)
    return sep.join(parts)
