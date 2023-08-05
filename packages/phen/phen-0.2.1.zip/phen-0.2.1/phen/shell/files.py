# -*- coding:utf-8 -*-

import os
import six
import time
import json
import tempfile

from binascii import a2b_base64

from .base import shlexed, protected, requires_cid
from .util import file_complete


def parse_json(shell, data):
    try:
        return json.loads(data)
    except Exception as e:
        shell.send(e)
        return data


def check_format(shell, name, data):
    if not name.lower().endswith((".json", ".jcfg")):
        return
    from phen.util.config import remove_comments
    try:
        if name[-1] == "g":
            data = remove_comments(data)
        json.loads(data)
        if name[-1] == "g":
            shell.send("JCFG format ok.")
        else:
            shell.send("JSON format ok.")
    except ValueError as exc:
        shell.send("Note: %s" % exc)


def cat(shell, name, dec):
    try:
        with shell.ctx.fs.open(name, 'rd') as infile:
            content = infile.read()
        if dec:
            if not bin:
                content = a2b_base64(content)
            try:
                content = shell.ctx.cid.pk.decrypt(content)
            except:  # IOError (RSA) or seccure.IntegrityError
                return shell.send("Wrong decryption key.")
        shell.send(content.decode("utf8") if six.PY3 else content)
    except Exception as e:
        shell.send(e)


class FileCommands:
    @shlexed
    def do_cat(self, args):
        """cat [-d [-b]] <file path> [<file path> ... ]

        Prints the contents of the file.
        Options:
            -d  decrypts with the private key
            -b  if file is not base64 encoded (bin)
        """
        dec = "-d" in args
        if dec:
            args.remove("-d")
        bin = "-b" in args
        if bin:
            args.remove("-b")
        if not args:
            return self.do_help("cat")
        if len(args) > 1:
            for name in args:
                if self.color:
                    fmtname = "Contents of \x1b[1;33m{}\x1b[0m".format(name)
                else:
                    fmtname = "Contents of " + name
                self.send(fmtname)
                cat(self, name, dec)
        else:
            cat(self, args[0], dec)

    def complete_cat(self, text, line, start_index, end_index):
        return file_complete(self.ctx.fs, text)

    @protected
    @shlexed
    @requires_cid
    def do_nano(self, args):
        """nano <file path>

        Edits the file using the nano text editor.
        """
        if not args:
            return self.do_help("nano")
        try:
            with tempfile.NamedTemporaryFile() as tmp:
                if self.ctx.fs.exists(args[0]):
                    with self.ctx.fs.open(args[0], 'rd') as infile:
                        tmp.write(infile.read())
                    tmp.seek(0)
                st = os.stat(tmp.name)
                self.send("nano " + tmp.name)
                from subprocess import call
                call(["nano", tmp.name], env={"TERM": "xterm"})
                if st.st_mtime != os.stat(tmp.name).st_mtime:
                    tmp.seek(0)
                    data = tmp.read()
                    with self.ctx.fs.open(args[0], 'wd') as out:
                        out.write(data)
                    check_format(self, args[0], data)
                else:
                    self.send("No changes.")
        except Exception as e:
            self.send(e)

    complete_nano = complete_cat

    def do_stat(self, line):
        """stat <file path>

        Prints the file metadata.
        """
        if not line:
            return self.do_help("stat")
        try:
            fmeta = self.ctx.fs.filemeta(line)
            if not fmeta:
                return self.send("No metadata.")
            if hasattr(fmeta, "to_dict"):
                self.send(json.dumps(fmeta.to_dict(), indent=4))
            else:
                self.send(fmeta)
        except Exception as e:
            self.send(e)

    complete_stat = complete_cat

    @requires_cid
    def do_rm(self, line):
        """rm <file path>

        Removes the file.
        """
        if not line:
            return self.do_help("rm")
        try:
            self.ctx.fs.unlink(line)
        except Exception as e:
            self.send(e)

    complete_rm = complete_cat

    @shlexed
    @requires_cid
    def do_write(self, args):
        """write <file path> [limit]

        Write into a file.
        `limit` may be:
            - a text delimiter indicating the end of input, which will
              not be included in the file (default to blank line);
            - an integer indicating the number of bytes to be read from
              the standard input.
        """
        if not args or len(args) > 2:
            return self.do_help("write")
        fname, limit = args if len(args) > 1 else (args[0], "")
        try:
            limit = int(limit)
            lines = [self.stdin.read(limit)]
        except ValueError:
            lines = []
        try:
            if not lines:
                from .shell import readline
                from .util import input_question
                self.send("Write or paste the file contents:")
                while True:
                    line = input_question(self, "|")
                    if line and readline and self.hist_path:
                        x = readline.get_current_history_length()
                        readline.remove_history_item(x - 1)
                    if line == limit:
                        break
                    lines.append(line)
            content = "\n".join(lines)
            self.ctx.fs.open(fname, 'wd').write(
                content.encode("utf8") if six.PY3 else content
            )
            check_format(self, fname, content)
        except KeyboardInterrupt:
            self.send("\nCancelled by the user.\n")
        except Exception as e:
            self.send(e)

    @shlexed
    @requires_cid
    def do_touch(self, args):
        """touch <file path>

        Create an empty file.
        """
        if len(args) > 1:
            return self.do_help("touch")
        try:
            self.ctx.fs.open(args[0], 'wd').close()
        except Exception as e:
            self.send(e)

    @shlexed
    @requires_cid
    def do_xattr(self, args):
        """xattr <file path> [-d <attribute> | <attribute> <value>]

        Change the file's extended attributes.
        `value` should be in JSON format, otherwise it is interpreted
        as regular text. Use simple quotes to frame the value, as JSON
        requires strings to be double quoted (e.g.: '{"key":"value"}')
        """
        if not args or len(args) > 3 or len(args) == 2:
            return self.do_help("xattr")
        try:
            if len(args) > 1 and args[1] != '-d':
                xad = self.ctx.fs.xattr(
                    args[0], {args[1]: parse_json(self, args[2])}, True
                )
            else:
                xad = self.ctx.fs.xattr(args[0])
            if len(args) > 1 and args[1] == '-d' and args[2] in xad:
                xad.pop(args[2])
                xad = self.ctx.fs.xattr(args[0], xad)
        except Exception as e:
            return self.send(e)
        self.send(json.dumps(xad, indent=4))

    complete_xattr = complete_cat

    @shlexed
    @requires_cid
    def do_utime(self, args):
        """utime <file path> [time]

        Sets the file's modification time.
        """
        if not args:
            return self.do_help("utime")
        if len(args) > 2:
            self.send("Ignored:", ", ".join(args[2:]))
        if len(args) > 1:
            try:
                ftime = float(args[1])
            except ValueError:
                self.send("Must be a UNIX timestamp (i.e. an integer)")
                return
        else:
            ftime = time.time()
        try:
            self.ctx.fs.utime(args[0], ftime)
        except Exception as e:
            self.send(e)

    complete_utime = complete_cat

    @shlexed
    @requires_cid
    def do_mv(self, args):
        """mv <old file path> <new file path>

        Renames the file.
        """
        if len(args) != 2:
            return self.do_help("mv")
        try:
            self.ctx.fs.rename(args[0], args[1])
        except Exception as e:
            self.send(e)

    complete_mv = complete_cat
