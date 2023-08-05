# -*- coding:utf-8 -*-


class ChannelNotFound(RuntimeError):
    """The specified path is not configured as a channel"""


class IncorrectChannel(RuntimeError):
    """The specified path is configured with a different type of channel"""


class Channel:
    channel_type = 'channel'

    def __init__(self, ctx, path, new=False):
        self.ctx = ctx
        self.path = path
        self.data = {}
        self.private = {}
        if new:
            self.data["type"] = self.channel_type
            if not self.ctx.fs.exists(path):
                self.ctx.fs.makedirs(path)
            else:
                try:
                    self.load()
                except Exception:
                    return
                raise IOError("Channel already exists")
        else:
            self.load()

    def load(self):
        fullpath = self.ctx.fs.subpath(self.path, "channel.json")
        try:
            self.data = self.ctx.fs.json_read(fullpath)
        except IOError:
            raise ChannelNotFound
        if self.channel_type != Channel.channel_type:
            if self.data["type"] != self.channel_type:
                raise IncorrectChannel("expected {}, got {}".format(
                    self.channel_type, self.data["type"]
                ))
        fullpath = self.ctx.fs.subpath(self.path, "chn-private.json")
        try:
            self.private = self.ctx.fs.json_read(fullpath)
        except IOError:
            pass

    def commit(self):
        fullpath = self.ctx.fs.subpath(self.path, "channel.json")
        self.ctx.fs.json_write(fullpath, self.data)
        fullpath = self.ctx.fs.subpath(self.path, "chn-private.json")
        if self.private:
            with self.ctx.groups():
                self.ctx.fs.json_write(fullpath, self.private)
        else:
            if self.ctx.fs.exists(fullpath):
                self.ctx.fs.unlink(fullpath)
