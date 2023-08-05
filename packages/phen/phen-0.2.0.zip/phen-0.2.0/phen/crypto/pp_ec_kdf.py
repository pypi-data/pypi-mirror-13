# -*- coding:utf-8 -*-

from hashlib import sha256
from cryptography.hazmat.backends import openssl
from cryptography.hazmat.primitives import ciphers


b = openssl.backend


def ec_passphrase_to_key(curve, passphrase):
    pp_dig = sha256(passphrase).digest()
    ctr = b"\0" * 16
    cipher = ciphers.Cipher(
        ciphers.algorithms.AES(pp_dig), ciphers.modes.CTR(ctr), backend=b
    )
    enc = cipher.encryptor()

    curve_nid = b._elliptic_curve_to_nid(curve)
    group = b._lib.EC_GROUP_new_by_curve_name(curve_nid)
    ec_cdata = b._lib.EC_KEY_new_by_curve_name(curve_nid)
    point = b._lib.EC_POINT_new(group)

    with b._tmp_bn_ctx() as bn_ctx:
        a = b._lib.BN_CTX_get(bn_ctx)
        tmp = b._lib.BN_CTX_get(bn_ctx)
        one = b._lib.BN_CTX_get(bn_ctx)
        order = b._lib.BN_CTX_get(bn_ctx)
        assert b._ffi.NULL not in (a, tmp, one, order)

        assert b._lib.EC_GROUP_get_order(group, tmp, bn_ctx)
        order_bytes = (b._lib.BN_num_bits(tmp) + 7) // 8
        buf = enc.update(b'\0' * order_bytes) + enc.finalize()

        b._lib.BN_bin2bn(buf, 24, a)
        b._lib.BN_bin2bn(b"\x01", 1, one)
        b._lib.BN_sub(order, tmp, one)
        b._lib.BN_nnmod(tmp, a, order, bn_ctx)
        b._lib.BN_add(a, tmp, one)
        assert b._lib.EC_KEY_set_private_key(ec_cdata, a)

        assert b._lib.EC_POINT_mul(
            group, point, a, b._ffi.NULL, b._ffi.NULL, bn_ctx
        )
        assert b._lib.EC_KEY_set_public_key(ec_cdata, point)
        assert b._lib.EC_KEY_check_key(ec_cdata)
        evp_pkey = b._ec_cdata_to_evp_pkey(ec_cdata)

    return openssl.ec._EllipticCurvePrivateKey(b, ec_cdata, evp_pkey)
