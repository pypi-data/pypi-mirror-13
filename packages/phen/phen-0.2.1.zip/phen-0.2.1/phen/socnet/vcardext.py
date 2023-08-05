#!/usr/bin/env python
#-*- coding:utf-8 -*-

"""
    Extensions to python-vobject (GEO)
"""

from vobject import vcard
from vobject.vcard import splitFields, serializeFields, VCardBehavior


class Geo(object):
    def __init__(self, latitude='', longitude=''):
        self.latitude = latitude
        self.longitude = longitude

    def __str__(self):
        return vcard.ascii(";".join((self.latitude, self.longitude)))

    def __repr__(self):
        return "<Geo: %s>" % str(self)

    def __eq__(self, other):
        try:
            return (self.latitude == other.latitude and
                    self.longitude == other.longitude)
        except:
            return False


class GeoBehavior(VCardBehavior):
    """A structured name."""
    hasNative = True

    @staticmethod
    def transformToNative(obj):
        """Turn obj.value into a Geo."""
        if obj.isNative:
            return obj
        obj.isNative = True
        obj.value = Geo(**dict(zip(GEO_ORDER, splitFields(obj.value))))
        return obj

    @staticmethod
    def transformFromNative(obj):
        """Replace the Geo in obj.value with a string."""
        obj.isNative = False
        obj.value = serializeFields(obj.value, GEO_ORDER)
        return obj


vcard.VCard3_0.knownChildren['GEO'] = (0, None, None)
GEO_ORDER = ('latitude', 'longitude')
vcard.registerBehavior(GeoBehavior, 'GEO')
