# -*- coding:utf-8 -*-

# note: "def." was used bellow so we can set the option values with defaults
# but not overwriting the ones defined in the config file
"""phen: runtime manager and plugin launcher

Usage:  phen [PLUGIN-HELP] (-h | --help) [-r ROOT-PATH] [-b] [-v | -vv]
        phen [--version]
        phen [-sb] [-v | -vv] [-w] [-f CONFIG-FILE] [--show-config]
             [-L FORMAT] [-l LOG-FILE]{drop}
             [-S] [-m METHOD] [-r ROOT-PATH] [-d KEY-FILE]
             [-i INCLUDE]... [-x EXCLUDE]...
             [(-c PLUGIN OPTION VALUE)]...

 Informative options:
  -h --help         show help about the plugin or this message and exit
  --version         show version and exit

 Basic system configuration options:
  -f, --cfg-file CFG-FILE   configuration file [default: {cfg-file}]
  -s, --save                update and save the configuration file; implied if
                            a config file was specified and it doesn't exist
  -L, --log-format FORMAT   log format (long or short) [def.: {log-format}]
  -l, --log-file LOG-FILE   set the output for log messages [def.: {log-file}]
  --show-config             print the final configuration (file + command line)
  -v                        be verbose
  -vv                       show debug messages if available{drop_long}

 Storage options:
  -r, --root-path ROOT-PATH   path to phen's storage folder [def.: {root-path}]
  -m, --method METHOD         storage method [def.: {method}]
  -S, --single-process        disable concurrent access to the filesystem
  -d, --device-key KEY-FILE   device key file name [def.: {device-key}]

 Runtime options:
  -c, --config (PLUGIN OPTION VALUE)    configure a plugin option
  -i, --include INCLUDE     load the specified plugin [def.: shell]
  -x, --exclude EXCLUDE     do not permit loading the specified plugin
  -b, --bypass-launcher     disable restart and upgradeable modules
  -w, --watch               automatically reload plugins on changes

"""

import os
import sys
import json
import time
import logging
from .docopt import docopt

import phen
import phen.storage
import phen.context
from phen.util import reactor


drop = """
                 [--user USER] [--group GROUP]"""

drop_long = """
  --user USER               user to set [def.: nobody]
  --group GROUP             group to set [def.: nogroup]
"""

log = logging.getLogger(__name__)


def parse_command_line():
    if not os.getuid():
        defaults = {
            "drop": drop, "drop_long": drop_long,
            "log-file": "/var/lib/phen/phen.log",
            "root-path": "/var/lib/phen",
            "cfg-file": "/etc/phen/config.json",
        }
    else:
        defaults = {
            "drop": "", "drop_long": "",
            "log-file": "stderr",
            "root-path": "~/.local/share/phen",
            "cfg-file": "~/.config/phen/config.json",
        }
    defaults.update({
        "device-key": "device.key",
        "log-format": "long",
        "method": "hostfs",
        "user": "nobody",
        "group": "nogroup",
    })
    if sys.platform.startswith("win"):
        defaults["root"] = "~/phen"
        defaults["cfg-file"] = "~/phen/config.json"
    elif sys.platform.startswith("darwin") and os.getuid():
        defaults["root"] = "~/phen"
        defaults["cfg-file"] = "~/phen/config.json"
    help_txt = __doc__.format(**defaults)
    defaults.pop("drop")
    defaults.pop("drop_long")
    opts = docopt(help_txt, help=False, version=phen.__version__)
    if opts["--help"]:
        name = opts["PLUGIN-HELP"]
        if name is None:
            print(help_txt)
        else:
            raise NotImplementedError("plugin help not implemented yet")
            # log_level = opts.get("-v", 0)
            # level = ['WARNING', 'INFO', 'DEBUG'][log_level]
            # logging.basicConfig(level=getattr(logging, level))
            # opts["--root-path"] = os.path.expanduser(opts["--root-path"])
            # phen.cfg["root-path"] = opts.get("--root-path")
            # phen.storage.setup()
            # plugin_doc = plugin_mgr.documentation(name)
            # if plugin_doc is None:
            #     print("Plugin '{}' could not be loaded.".format(name))
            # else:
            #     print(plugin_doc)
        exit(phen.retcodes.exit)
    del opts["--version"]
    del opts["--help"]
    del opts["PLUGIN-HELP"]
    del opts["--bypass-launcher"]
    cfgpath = os.path.expanduser(opts["--cfg-file"])
    if opts["--cfg-file"] is not None and not os.path.exists(cfgpath):
        opts["--save"] = True
    opts["--cfg-file"] = cfgpath
    return defaults, opts


def load_config_file(cfgpath):
    if os.path.exists(cfgpath):
        with open(cfgpath) as cfgfile:
            try:
                return json.load(cfgfile)
            except ValueError:
                print("Invalid config file, renamed to {}.invalid"
                      .format(cfgpath))
                os.rename(cfgpath, cfgpath + ".invalid")
                exit(phen.retcodes.exit)
    return {}


def merge_config(cfg, defaults, opts):
    for option in defaults:
        value = opts.pop("--" + option, None)
        if option not in cfg or value is not None:
            cfg[option] = value or defaults[option]


def merge_config_non_empty(cfg, opts):
    for option in list(opts.keys()):
        value = opts.pop(option)
        if option[2:] not in cfg or value:
            cfg[option[2:]] = value


def process_config(defaults, opts):
    opts["--verbosity"] = opts.pop("-v")
    save = opts.pop("--save")
    show_config = opts.pop("--show-config")
    plugin_cfg = opts.pop("--config")
    plugin_opt = opts.pop("OPTION")
    plugin_val = opts.pop("VALUE")
    cfgpath = opts.pop("--cfg-file")
    defaults.pop("cfg-file")
    cfg = load_config_file(cfgpath)
    merge_config(cfg, defaults, opts)
    merge_config_non_empty(cfg, opts)
    plugins = cfg.setdefault("plugins", {})
    for i, plugin in enumerate(plugin_cfg):
        popts = plugins.setdefault(plugin, {})
        popts[plugin_opt[i]] = plugin_val[i]
    if show_config:
        from pprint import pprint
        pprint(cfg)
    if save:
        folder = os.path.dirname(cfgpath)
        if not os.path.exists(folder):
            os.makedirs(folder)
        with open(cfgpath, 'w') as cfgfile:
            json.dump(cfg, cfgfile, indent=2)
    cfg["root-path"] = os.path.expanduser(cfg["root-path"])
    if not os.getuid():
        import pwd
        import grp
        cfg["user"] = pwd.getpwnam(cfg["user"]).pw_uid
        cfg["group"] = grp.getgrnam(cfg["group"]).gr_gid
    return cfg


def setup_logging():
    log_level = phen.cfg.get("verbosity", 0)
    log_output = phen.cfg.get("log-file", "stderr")
    log_format = phen.cfg.get("log-format", "long")
    if log_output != "stderr":
        if not os.path.exists(os.path.dirname(log_output)):
            return False
    level = ['WARNING', 'INFO', 'DEBUG'][log_level]
    if log_output != "stderr":
        logging.basicConfig(filename=log_output, level=getattr(logging, level))
        phen.chown(log_output)
    else:
        logging.basicConfig(level=getattr(logging, level))
        root = logging.getLogger()
        if not sys.platform.startswith("win"):
            from phen.util.colorlog import ColorFormatter
            root.handlers[0].setFormatter(ColorFormatter(log_format == "long"))
    return True


def interrupt():
    from signal import SIGINT
    os.kill(os.getpid(), SIGINT)


def drop_superuser():
    if not os.getuid():
        log.info("dropping superuser privileges")
        phen.context.device.fs.flush_cache()
        os.setgroups([])
        os.setgid(phen.cfg.get("group"))
        os.setuid(phen.cfg.get("user"))
        phen.storage.store.set_owner = False


def init_plugin_manager():
    from phen.plugin import Manager
    parts = os.path.realpath(__file__).split(os.path.sep)
    if parts[-3] == "phen":
        # development environment
        plugins_path = None
    else:
        plugins_path = os.path.join(phen.cfg.get("root-path"), "plugins")
    plugin_mgr = Manager(plugins_path)
    plugin_mgr.watch = phen.cfg.get("watch", False)
    plugin_mgr.exclude(phen.cfg.get("exclude"))
    plugin_mgr.bulk_load(phen.cfg.get("include"))
    return plugin_mgr


def unlock_device(plugin_mgr):
    try:
        log.info("unlocking device")
        try:
            phen.context.device.load_identity()
        except IOError:
            pass
        if not phen.context.device.cid:
            plugin_mgr.broadcast(
                "load_device",
                lambda: phen.context.device.cid
            )
        if not phen.context.device.cid:
            log.error("blocking until device has an identity")
            while not phen.context.device.cid:
                time.sleep(1)
    except KeyboardInterrupt:
        pass
    return phen.context.device.cid is not None


def execute_plugins():
    plugin_mgr = init_plugin_manager()
    if not plugin_mgr.plugins:
        log.error("useless to continue without plugins, quiting")
        return plugin_mgr.shutdown()
    if unlock_device(plugin_mgr):
        plugin_mgr.broadcast("device_loaded")
        drop_superuser()
        if not plugin_mgr.broadcast("main", first_only=True):
            log.info("main thread waiting for interruption")
            try:
                while True:
                    time.sleep(2 ** 22)
            except KeyboardInterrupt:
                pass
    plugin_mgr.shutdown()


def run():
    defaults, opts = parse_command_line()
    phen.cfg = process_config(defaults, opts)
    phen.storage.setup()
    setup_logging()
    log.info("initializing storage")
    phen.reactor_thread = reactor.run()
    phen.storage.store.lock_filesystem()
    phen.context.setup()
    phen.restart = False

    execute_plugins()

    log.info("shutting down")
    phen.context.device.shutdown()
    phen.storage.store.shutdown()
    reactor.stop()
    exit(phen.retcodes.restart if phen.restart else phen.retcodes.exit)
