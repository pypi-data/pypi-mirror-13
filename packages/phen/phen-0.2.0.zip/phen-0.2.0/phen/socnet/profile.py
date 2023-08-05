#!/usr/bin/env python
#-*- coding:utf-8 -*-

"""
    Profile - VCard manipulation
"""

import re
import imghdr

from six import StringIO

from . import vcardext as vobject


fields = ('tel adr n fn nickname email version '
          'label rev url x-evolution-blog-url caluri '
          'bday tz anniversary x-evolution-anniversary '
          'note geo photo x-skype x-jabber x-icq').split()


def convert_field(v):
    if isinstance(v.value, str):
        retv = {"value": v.value}
    else:
        retv = v.value.__dict__.copy()
    retv.update(v.params)
    return retv


def vcard_to_json(data):
    vcard = vobject.readOne(data)
    retv = {
        field: [
            convert_field(v)
            for v in getattr(vcard, field + '_list', [])
            if v.value
        ]
        for field in fields
    }
    if 'x-evolution-anniversary' in retv:
        retv['anniversary'] = retv.pop('x-evolution-anniversary')
    if 'photo' in retv and retv['photo']:
        if retv['photo'][0].get('ENCODING') == 'b':
            retv.pop('photo')
    return retv


def json_to_vcard(data):
    special = {
        'geo': vobject.Geo,
        'adr': vobject.vcard.Address,
        'n': vobject.vcard.Name,
    }
    vcard = vobject.vCard()
    for field in data:
        for inst in data[field]:
            vinst = vcard.add(field)
            vinst.value = special[field]() if field in special else ''
            for key in inst:
                if key == 'value':
                    setattr(vinst, key, inst[key])
                elif key.isupper():
                    setattr(vinst, key + '_param', inst[key])
                else:
                    if vinst.value != '':
                        setattr(vinst.value, key, inst[key])
                    else:
                        print(field, key, "'pau'")
    return vcard.serialize()


def split_photo(data, img_fname):
    """
        Split a possibly embedded photo, discarding the
        photo data if invalid, otherwise returning its data
        and format, and updating the vcard.
    """
    vcard = vobject.readOne(data)
    if hasattr(vcard, 'photo') and vcard.photo.ENCODING_param[0] == 'b':
        photo = vcard.photo.value
        fmt = imghdr.what(StringIO(photo))
        if not fmt:
            photo = None
            del vcard.photo
        else:
            del vcard.photo.ENCODING_param
            vcard.photo.TYPE_param = fmt.upper()
            vcard.photo.value = img_fname + "." + fmt
        data = vcard.serialize()
    else:
        photo, fmt = None
    return data, photo, fmt


def get_profile(fs, idhash, preferred=None):
    """
        Try to get basic profile information from an identity.
    """
    # todo: cache
    subpath = fs.subpath
    try:
        files = fs.listdir(subpath(idhash, "profile"))
    except IOError:
        files = []
    # try preferred first
    if files and preferred:
        vcards = [f for f in files
                  if f.startswith("vcard.") and f.endswith(".vcf")
                  and f[6:-4] == preferred]
    else:
        vcards = None
    # if not found, get any
    if not vcards:
        vcards = [f for f in files
                  if f.startswith("vcard.") and f.endswith(".vcf")]
    # none found
    if not vcards:
        return {"idhash": idhash, "username": "anonymous",
                "name": "Anonymous", "photo": None}
    # get vcard data
    with fs.open(subpath(idhash, "profile", vcards[0])) as vcf:
        vcard = vcf.read()
    # find username
    matches = re.findall(r"(?m)^NICKNAME:(.*?)\r?\n", vcard)
    username = matches[0] if matches else 'anonymous'
    # find name
    matches = re.findall(r"(?m)^FN:(.*?)\r?\n", vcard)
    name = matches[0] if matches else 'Anonymous'
    # find photo
    #photo_re = r"(?m)^PHOTO(?:.*?)(http|ENCOD.*?:|base64,)(.*$(?:\n .*$)*)"
    photo_re = r"(?m)^PHOTO(?:.*:)(.*\.\w{3,4})\r?\n"
    matches = re.findall(photo_re, vcard)
    photo = matches[0] if matches else None
    return {"idhash": idhash, "username": username,
            "name": name, "photo": photo}


def get_profiles(fs, idhash_list):
    return [get_profile(fs, idhash) for idhash in idhash_list]
