# -*- coding:utf-8 -*-

"""
    Phen main module
"""

import os
import six
import locale
import gettext


__appname__     = "phen"
__version__     = "0.2.0"
__idhash__      = "mlUDK5IPJYwAD0D6aINCAIbcc20QFqw4CHqwaUSJSIk"

phen_path = os.path.dirname(os.path.realpath(__file__))
language = gettext.translation(
    __appname__, os.path.join(phen_path, "i18n"), fallback=True
)
_ = language.gettext if six.PY3 else language.ugettext

language_code = locale.getdefaultlocale(('LANGUAGE', 'LANG'))[0]
try:
    longdesc = open(
        os.path.join(phen_path, "i18n", language_code, "DESCRIPTION.rst")
    ).read()
except:
    longdesc = open(os.path.join(phen_path, "data/DESCRIPTION.rst")).read()

__longname__    = _("Phen - Private Heterogeneous Emergent Network")
__description__ = _("Decentralized platform for social applications")
__longdesc__    = longdesc
__author__      = _("Daniel Monteiro Basso and contributors")
__copyright__   = _(u"Copyright © {0}").format("2013-2016")
__credits__     = {
    "coding": [
        "Daniel Monteiro Basso",
    ],
    "translations": [
        "Daniel Monteiro Basso",
        "Miloš Zdravković",
    ],
    "documentation": [
        "Daniel Monteiro Basso",
    ],
    "art": [
        "Daniel Monteiro Basso",
    ],
}

__shortlic__    = "AGPLv3+ and others from incorporated modules"
__license__     = "\n\n".join(
    open(os.path.join(phen_path, "data", license)).read()
    for license in [
        "LICENSE",
        "docopt-license",
    ])

__website__     = "https://phen.eu"
__maintainer__  = "Daniel Monteiro Basso"
__email__       = "daniel@basso.inf.br"


# default config for testing
cfg = {
    'root-path': '/tmp/phen',
    'exclude': [],
    'include': [],
    'log-file': 'stderr',
    'log-format': 'long',
    'method': 'hostfs',
    'plugins': {},
    'single-process': True,
    'verbosity': 2
}


def plugin_cfg(name, opt, default):
    popts = cfg["plugins"].get(name)
    if popts is None:
        return default
    return popts.get(opt, default)


def chown(path):
    if not os.getuid() and cfg.get("user"):
        os.chown(path, cfg.get("user"), cfg.get("group"))


class retcodes:
    exit = 0
    error = 1
    start = restart = 10
