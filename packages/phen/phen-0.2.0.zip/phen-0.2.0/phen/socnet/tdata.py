#!/usr/bin/env python
#-*- coding:utf-8 -*-

"""
    Temporal Data Manipulation Objects.
"""

from datetime import datetime


class TemporalData:
    daily, monthly, yearly = (0, 1, 2)
    formats = ("/%Y/%m/%d", "/%Y/%m", "/%Y")

    def __init__(self, fs, root_path, ext, frequency=0):
        self.fs = fs
        self.root_path = root_path
        self.ext = ext
        self.frequency = frequency

    def fmt_time(self, date, frequency=None):
        fmt = self.formats[frequency or self.frequency]
        return self.root_path + date.strftime(fmt)

    def filter_num(self, path):
        for fname in self.fs.listdir(path):
            if not fname.isdigit():
                continue
            fpath = path + "/" + fname
            if not self.fs.filemeta(fpath).is_folder():
                continue
            yield int(fname)

    def filter_ext(self, path):
        for fname in self.fs.listdir(path):
            if fname.endswith(self.ext):
                fpath = path + "/" + fname
                mtime = self.fs.filemeta(fpath).mtime
                yield mtime, fpath

    def entry_path(self, date, name):
        return self.fmt_time(date) + "/" + name + self.ext

    def exists(self, date, name):
        return self.fs.exists(self.entry_path(date, name))

    def create_entry(self, date=None, name=None):
        """
            Create the temporal folder hierarchy, optionally
            creating a folder for the content if `name` is specified.
        """
        if date is None:
            date = datetime.now()
        full_path = self.fmt_time(date)
        if name is not None:
            full_path += "/" + name + self.ext
        self.fs.makedirs(full_path)
        return full_path

    def set_cursor(self, timeref=None, to_past=False, limit=None):
        self.to_past = to_past
        timeref = timeref or datetime.now()
        self.cursor = iter(self.retrieve(timeref, limit))
        self.collected = []

    def retrieve(self, timeref, limit):
        years = [f for f in self.filter_num(self.root_path)
                 if (self.to_past and f <= timeref.year)
                 or (not self.to_past and f >= timeref.year)]
        years.sort(reverse=self.to_past)
        if timeref.year not in years:
            rmonth = 12 if self.to_past else 1
            rday = 31 if self.to_past else 1
        else:
            rmonth = timeref.month
            rday = timeref.day
        for year in years:
            if limit is not None:
                if self.to_past:
                    if year < limit.year:
                        return
                else:
                    if year > limit.year:
                        return
            path = "{}/{}".format(self.root_path, year)
            if self.frequency == self.yearly:
                for entry in self.filter_ext(path):
                    yield entry
                continue
            months = [f for f in self.filter_num(path)
                      if (self.to_past and f <= rmonth)
                      or (not self.to_past and f >= rmonth)]
            months.sort(reverse=self.to_past)
            if rmonth not in months:
                rday = 31 if self.to_past else 1
            for month in months:
                if limit is not None and year == limit.year:
                    if self.to_past:
                        if month < limit.month:
                            return
                    else:
                        if month > limit.month:
                            return
                mpath = "{}/{:02d}".format(path, month)
                if self.frequency == self.monthly:
                    for entry in self.filter_ext(mpath):
                        yield entry
                    continue
                days = [f for f in self.filter_num(mpath)
                        if (self.to_past and f <= rday)
                        or (not self.to_past and f >= rday)]
                days.sort(reverse=self.to_past)
                for day in days:
                    if limit and year == limit.year and month == limit.month:
                        if self.to_past:
                            if day < limit.day:
                                return
                        else:
                            if day > limit.day:
                                return
                    entries = self.filter_ext("{}/{:02d}".format(mpath, day))
                    for entry in entries:
                        yield entry
                rday = 31 if self.to_past else 1
            rmonth = 12 if self.to_past else 1

    def get_more(self, count):
        """
            Retrieve more items, or all if count is None.
            Note: set_cursor must be called when direction changes.
        """
        while count is None or len(self.collected) < count:
            try:
                self.collected.append(next(self.cursor))
            except StopIteration:
                break
        self.collected.sort(reverse=self.to_past)
        retv = self.collected[:count]
        self.collected = self.collected[count:]
        return retv


class TemporalCursor:
    def __init__(self, data=None):
        if data is None:
            data = []
        elif not isinstance(data, list):
            data = [data]
        self.data = data
        self.collected = []

    def aggregate(self, data):
        if isinstance(data, list):
            self.data += data
        else:
            self.data.append(data)

    def set_cursor(self, timeref=None, to_past=False, limit=None):
        self.to_past = to_past
        for src in self.data:
            src.set_cursor(timeref, to_past, limit)
        self.collected = []

    def get_more(self, count):
        if count is None or len(self.collected) < count:
            for src in self.data:
                self.collected += src.get_more(count)
        self.collected.sort(reverse=self.to_past)
        retv = self.collected[:count]
        self.collected[count:]
        return retv
