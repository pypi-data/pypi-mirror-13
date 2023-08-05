# -*- coding:utf-8 -*-

from twisted.web import resource, static
# from phen.util import path_join as pj


# class InternalFile(static.File):
#     sep = u"/"
#
#     def __init__(self, path, *p, **kw):
#         static.File.__init__(self, "", *p, **kw)
#         self.path = path
#         from phen.context import device
#         self.__fs = device.fs
#         print(self.__fs.curdir)
#         try:
#             self.__fmeta = device.fs.filemeta(self.path)
#         except IOError:
#             from traceback import print_exc
#             print_exc()
#             self.__fmeta = None
#         print(self.__fmeta)
#
#     def open(self):
#         return self.__fmeta and self.__fs.open(self.path)
#
#     def isdir(self):
#         return self.__fmeta and self.__fmeta.is_folder
#
#     def getsize(self):
#         """Return file size."""
#         return self.__fmeta and self.__fmeta.size
#
#     def exists(self):
#         return self.__fmeta is not None
#
#     def listdir(self):
#         return self.__fs.listdir(self.path)
#
#     def child(self, path):
#         if not self.isdir:
#             return
#         return path in self.listdir() and InternalFile(pj(self.path, path))
#
#     def restat(self, reraise):
#         pass


class Root(resource.Resource):
    def __init__(self):
        resource.Resource.__init__(self)
        from .default import Page
        self.index = Page()
        self.domains = {}

    def set_domains(self, domains):
        self.domains = {}
        for d, subdomains in domains.items():
            if not isinstance(subdomains, dict):
                self.domains[d] = subdomains.split("/")  # actually path
                continue
            for s, path in subdomains.items():
                full = ".".join((s, d)) if s else d
                self.domains[full] = path.split("/")

    def mount_statics(self, statics):
        for point, path in statics.items():
            if path.startswith(">"):
                self.putChild(point, static.File(path[1:].encode("utf8")))
            else:
                raise NotImplementedError
                # self.putChild(point, InternalFile(path))

    def getChild(self, path, request):
        # plugins should putChild("") to override the default
        if not path:
            return self.index
        return resource.NoResource()

    def getChildWithDefault(self, path, request):
        host = request.received_headers["host"].split(":", 1)[0]
        if host not in self.domains:
            return resource.Resource.getChildWithDefault(self, path, request)
        parts = self.domains[host][:]
        retv = resource.Resource.getChildWithDefault(
            self, parts.pop(0), request
        )
        for part in parts:
            if retv.isLeaf:
                return retv
            retv = retv.getChildWithDefault(part, request)
        return retv.getChildWithDefault(path, request)
