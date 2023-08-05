#!/usr/bin/env python
#-*- coding:utf-8 -*-

import re
import random
import string

from hashlib import sha256
from binascii import b2a_base64


def generate_access_key(domain="gmail.com"):
    from urllib2 import urlopen
    from urllib import urlencode
    url = "http://www.google.com/recaptcha/mailhide/"
    response_re = re.compile(r"textarea.*?>(.*?)<")
    user = [random.choice(string.letters + string.digits)
            for i in range(random.randint(6, 10))]
    email = ''.join(user) + "@" + domain
    ehash = b2a_base64(sha256(email).digest())[:-1]
    mailhide = urlopen(url, urlencode([("emails", email)]))
    link = response_re.findall(mailhide.read())[0].replace("&amp;", "&")
    return link, ehash


def check_access_key(email, hashes):
    if email.startswith("mailto:"):
        email = email[7:]
    return b2a_base64(sha256(email).digest())[:-1] in hashes
