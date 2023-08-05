# -*- coding:utf-8 -*-

from ..protocol import rh


block_size = 1 << 20


@rh.request(4)
def file_request(conn, data):
    from .upload import upload_mgr
    return upload_mgr.file_request(conn, data)


@rh.response(4)
def r_file_request(conn, data):
    from .download import download_mgr
    download_mgr.r_file_request(conn, data)


@rh.request(5)
def block_request(conn, data):
    from .upload import upload_mgr
    return upload_mgr.block_request(conn, data)


@rh.response(5)
def r_block_request(conn, data):
    from .download import download_mgr
    download_mgr.r_block_request(conn, data)


@rh.request(6)
def block_data(conn, data):
    from .download import download_mgr
    download_mgr.r_block_data(conn, data)
