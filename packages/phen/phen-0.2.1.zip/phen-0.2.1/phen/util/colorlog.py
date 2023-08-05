#!/usr/bin/env python
#-*- coding:utf-8 -*-

import logging


class ColorFormatter(logging.Formatter):

    colors = "black red green yellow blue magenta cyan white".split()
    mapping = dict(D='blue', I='white', W='yellow', E='red')

    def __init__(self, layout=1):
        if layout == 0:
            fmt = ("%(asctime)s\x1b[37;2m%(name)s\x1b[0m"
                   "%(levelname)s: \x1b[{}m%(message)s\x1b[0m")
            self.format = self.format0
        else:
            fmt = ("\n\x1b[37;2m%(asctime)s   %(lineno)4s "
                   "%(name)s    %(levelname)-8s"
                   "%(threadName)s\n\x1b[0;{}m%(message)s\x1b[0m")
            self.format = self.format1
        logging.Formatter.__init__(self, fmt)

    def format0(self, record):
        lvl = record.levelname = record.levelname[:1]
        short_name = ".".join(part[:4] for part in record.name.split('.')[1:])
        record.name = short_name.ljust(15)
        color = str(30 + self.colors.index(self.mapping.get(lvl, 'red')))
        if lvl == 'I':
            color = "1;" + color
        m = str(record.msg).replace("\n", "\\n")
        record.msg = ("\n" + " " * 41).join(m[i:i + 64]
                                            for i in range(0, len(m), 64))
        record.msg = record.msg.replace("{", "{{").replace("}", "}}")
        retv = logging.Formatter.format(self, record)
        return retv.format(color)

    def format1(self, record):
        lvl = record.levelname[:1]
        short_name = ".".join(part for part in record.name.split('.')[1:])
        record.name = short_name.ljust(30)
        color = str(30 + self.colors.index(self.mapping.get(lvl, 'red')))
        if lvl == 'I':
            color = "1;" + color
        m = str(record.msg).replace("\n", "\\n")
        record.msg = "\n" .join(m[i:i + 100] for i in range(0, len(m), 100))
        record.msg = record.msg.replace("{", "{{").replace("}", "}}")
        retv = logging.Formatter.format(self, record)
        return retv.format(color)
