# -*- coding:utf-8 -*-

import logging
from twisted.internet import defer

from phen.util import fid2name

from .upload import upload_mgr  # noqa
from .download import download_mgr, Download


log = logging.getLogger(__name__)


def download(fid_pair, **kw):
    df = defer.Deferred()
    if download_mgr.already_requested(fid_pair):
        log.debug(fid2name(fid_pair) + " was already requested")
        download_mgr.by_fid_pair[fid_pair].deferred.append(df)
        return df
    log.debug("starting download of " + fid2name(fid_pair))
    download_mgr.by_fid_pair[fid_pair] = Download(fid_pair, df, **kw)
    return df
