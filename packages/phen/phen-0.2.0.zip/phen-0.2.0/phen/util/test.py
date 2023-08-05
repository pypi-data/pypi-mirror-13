# -*- coding:utf-8 -*-

import os
import shutil

import phen.context
import phen.storage


def get_ctx(request):
    if os.path.exists("/tmp/phen-template"):
        shutil.rmtree("/tmp/phen")
        shutil.copytree("/tmp/phen-template", "/tmp/phen")
    else:
        try:
            shutil.rmtree("/tmp/phen")
        except:
            pass
    phen.storage.setup()
    phen.storage.store.lock_filesystem()
    phen.context.setup()
    phen.context.device.setup_test()
    phen.context.device.fs.flush_cache()
    ctx = phen.context.Context.get_admin()
    ctx.ids = [
        ctx.create_identity(i, key_type='ECC secp192r1',
                            populate=1, aetherial=True)
        for i in ("id2", "id1")
    ][::-1]
    if not os.path.exists("/tmp/phen-template"):
        phen.context.device.fs.flush_cache()
        ctx.fs.flush_cache()
        shutil.copytree("/tmp/phen", "/tmp/phen-template")
        os.unlink("/tmp/phen-template/in-use")

    def fin():
        ctx.shutdown()
        phen.context.device.shutdown()
        phen.storage.store.shutdown()

    request.addfinalizer(fin)
    return ctx
