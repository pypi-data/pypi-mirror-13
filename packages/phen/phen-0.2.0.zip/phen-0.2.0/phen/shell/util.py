# -*- coding:utf-8 -*-

import sys
from getpass import getpass
from phen.crypto import key_types


def input_question(obj, question, nolf=True, insert=None):
    if not getattr(obj, "use_rawinput", False):
        if insert:
            question += " [{}]".format(insert)
        obj.send(question, nolf=nolf)
        return obj.stdin.readline()[:-1] or insert
    if not insert:
        return raw_input(question)
    try:
        import readline
        readline.set_startup_hook(lambda: readline.insert_text(insert))
        return raw_input(question)
    except ImportError:
        return raw_input(question)
    finally:
        readline.set_startup_hook()


def input_passphrase(obj, msg=None):
    obj.send(msg or "Type in your pass phrase: ", nolf=True)
    if obj.stdin == sys.stdin:
        return getpass("")
    else:
        if hasattr(obj.stdin, "hidden"):
            obj.stdin.hidden()
        elif hasattr(obj.stdin, "echo"):
            obj.stdin.echo(False)
        retv = obj.stdin.readline()[:-1]
        if hasattr(obj.stdin, "hidden"):
            obj.stdin.hidden(False, len(retv))
        elif hasattr(obj.stdin, "echo"):
            obj.stdin.echo()
        return retv


def input_key_specs(obj):
    passphrase = input_passphrase(obj, "Type in a pass phrase: ")
    confirm = input_passphrase(obj, "Please confirm the pass phrase: ")
    if passphrase != confirm:
        return None, None, None
    default = 3
    ordered_kt = sorted(key_types)
    types = "".join("{}{} - {}\n".format(i, '*' if i == default else ' ', kt)
                    for i, kt in enumerate(ordered_kt))
    obj.send("Select the new key type (*default):\n" + types)
    try:
        key_type = ordered_kt[int(obj.stdin.readline()[:-1])]
    except ValueError:
        key_type = ordered_kt[default]
    except LookupError:
        key_type = ordered_kt[default]
    if passphrase and not key_type.startswith("RSA"):
        obj.send("Aetherial? (y/N) ", nolf=True)
        aetherial = obj.stdin.readline()[:-1]
        aetherial = aetherial and aetherial[0].lower() == 'y'
    else:
        aetherial = False
    return key_type, passphrase, aetherial


def file_complete(fs, text, filtdir=False):
    path = text.split("/")
    if len(path) > 1:
        folder = u"/".join(path[:-1])
        files = [folder + "/" + f for f in fs.listdir(folder)]
    else:
        files = [f for f in fs.listdir(u".")]

    def isfolder(f):
        try:
            return fs.filemeta(f).is_folder()
        except:
            return True  # idfolder

    if filtdir:
        files = [f for f in files if isfolder(f)]
    if not text:
        return files
    return [f + ("/" if isfolder(f) else "")
            for f in files if f.startswith(text)]
