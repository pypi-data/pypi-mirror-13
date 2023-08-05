# -*- coding:utf-8 -*-

"""
    Configuration loading utilities
"""

import re
import json
import logging

from . import shorten_hashes as shh


log = logging.getLogger(__name__)

comments_re = re.compile(r"""^
  (                         # group for the the actual content
    (?:                     # which is a series of ((pre-quote)(quote)?)*
      [^"\#]*               # pre-quote
      (?:"                  # quote (optional)
        ([^"]|(?<=\\)")*    # anything but ", or escaped "
      ")?
    )*
  )
  (\#.*)?                 # comment (optional)
$""", re.MULTILINE | re.VERBOSE)


def remove_comments(text):
    return comments_re.sub(r"\1", text)


def merge_dict(dct1, dct2):
    for k, v in dct2.items():
        if k not in dct1:
            dct1[k] = v
            continue
        if isinstance(dct1[k], dict) and isinstance(v, dict):
            merge_dict(dct1[k], v)
        elif isinstance(dct1[k], list) and isinstance(v, list):
            dct1[k].extend(v)
        # otherwise dct1[k] has priority and is kept, dct2[k] ignored
    return dct1


def load(fs, path, init=None, abscence_ok=False, keep_comments=False):
    if not fs.exists(path):
        if init is not None:
            log.warn("Default config file '%s' created." % shh(path))
            fs.json_write(path, init, indent=2)
            return init
        if not abscence_ok:
            log.error("Config file '%s' not found." % shh(path))
        return ({}, []) if keep_comments else {}
    try:
        with fs.open(path, "rd") as in_:
            data = in_.read()
        if keep_comments:
            comment_pairs = comments_re.findall(data)
        cfg = json.loads(remove_comments(data))
    except IOError:
        log.exception("Could not read config file " + shh(path))
        return ({}, []) if keep_comments else {}
    except ValueError:
        log.exception("Config file '{}' is not valid JSON.".format(shh(path)))
        return ({}, []) if keep_comments else {}
    for inc_type in ("include", "include-overwrite"):
        if not cfg.get(inc_type):
            continue
        includes = cfg.pop(inc_type)
        if not isinstance(includes, list):
            includes = [includes]
        for filepath in includes:
            if keep_comments:
                inc_cfg, icp = load(fs, filepath, keep_comments=keep_comments)
                comment_pairs.extend(icp)
            else:
                inc_cfg = load(fs, filepath)
            if inc_type == "include":
                merge_dict(cfg, inc_cfg)
            else:
                cfg = merge_dict(inc_cfg, cfg)
    log.debug("Successfully read config file '%s'." % shh(path))
    return (cfg, comment_pairs) if keep_comments else cfg
