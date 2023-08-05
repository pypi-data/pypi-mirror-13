# -*- coding:utf-8 -*-

from phen.event import Event


certificate_renewed = Event()


def create_self_signed_crt(key_path, certificate_path):
    from OpenSSL import crypto
    from random import randint
    key = crypto.PKey()
    key.generate_key(crypto.TYPE_RSA, 2048)
    crt = crypto.X509()
    crt.get_subject().CN = "localhost"
    crt.set_serial_number(randint(0, 2**159))
    crt.gmtime_adj_notBefore(0)
    crt.gmtime_adj_notAfter(50 * 365 * 24 * 60 * 60)
    crt.set_issuer(crt.get_subject())
    crt.set_pubkey(key)
    crt.sign(key, 'sha256')
    with open(key_path, "wt") as out:
        out.write(crypto.dump_privatekey(crypto.FILETYPE_PEM, key))
    with open(certificate_path, "wt") as out:
        out.write(crypto.dump_certificate(crypto.FILETYPE_PEM, crt))
    import phen
    phen.chown(key_path)
    phen.chown(certificate_path)


def get_paths(create=True):
    """
    Return a tuple of key and certificate paths, optionally
    creating a self-signed certificate if the files don't exist
    """
    import os
    import phen
    root = phen.cfg.get("root-path")
    key, crt = (os.path.join(root, "server." + ext) for ext in ("key", "crt"))
    if create and not all(os.path.exists(path) for path in (key, crt)):
        create_self_signed_crt(key, crt)
    return key, crt


def get_ctx(key_path=None, certificate_path=None):
    """
    Return a Twisted SSL Context for servers
    """
    from twisted.internet import ssl
    if None in (key_path, certificate_path):
        key_path, certificate_path = get_paths()
    return ssl.DefaultOpenSSLContextFactory(key_path, certificate_path)
