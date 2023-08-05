#!/usr/bin/env python
# -*- coding:utf-8 -*-

import os
import sys
from setuptools import setup

import phen


packages = [
    "phen",
    "phen.crypto",
    "phen.db",
    "phen.db.composable",
    "phen.db.layout",
    "phen.filesystem",
    "phen.filesystem.folder",
    "phen.http",
    "phen.p2pnet",
    "phen.p2pnet.filexchg",
    "phen.p2pnet.shell",
    "phen.plugin",
    "phen.plugins",  # install point for other packages
    "phen.shell",
    "phen.socnet",
    "phen.ssh",
    "phen.storage",
    "phen.util",
]

data = sum((
    [os.path.join(root, f)[5:] for f in files]  # strip leading 'phen/'
    for root, dirs, files in os.walk('phen/data')
), [])

scripts = ["bin/phen"]

requires = open("requirements.txt").read().split()
devel_req = open("devel-req.txt").read().split()

if sys.platform.startswith("win"):
    import py2exe  # noqa
else:
    scripts.append("bin/su-phen-config")

if "sdist" in sys.argv:
    idx = sys.argv.index("sdist")
    sys.argv.insert(idx + 1, "--formats")
    sys.argv.insert(idx + 2, "zip")


setup(
    name=phen.__appname__,
    version=phen.__version__,
    author=phen.__author__,
    author_email=phen.__email__,
    maintainer=phen.__maintainer__,
    maintainer_email=phen.__email__,
    url=phen.__website__,
    license=phen.__shortlic__,
    description=phen.__description__,
    long_description=phen.__longdesc__,
    install_requires=requires,
    scripts=scripts,
    packages=packages,
    package_dir={"phen": "phen"},
    package_data={"phen": ["i18n/*/*.rst", "i18n/*/*/*.mo"] + data},
    classifiers=[
        'Development Status :: 3 - Alpha',
        'Intended Audience :: Developers',
        'Topic :: Communications',
        'Topic :: Database :: Database Engines/Servers',
        'Topic :: Security :: Cryptography',
        'Topic :: Sociology',
        'Topic :: Software Development :: Libraries :: Application Frameworks',
        'Topic :: System :: Filesystems',
        'Topic :: System :: Shells',
        'Framework :: Twisted',
        'License :: OSI Approved :: '
        'GNU Affero General Public License v3 or later (AGPLv3+)',
        'Programming Language :: Python :: 2',
        'Programming Language :: Python :: 3',
    ],
    keywords='decentralization social-networks',
    extras_require={
        'devel': devel_req,
    },
)
