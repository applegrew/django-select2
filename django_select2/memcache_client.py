# -*- coding: utf-8 -*-
from __future__ import unicode_literals

import memcache


class Client(object):
    host = ""
    server = ""
    expiry = 900

    def __init__(self, hostname="127.0.0.1", port="11211", expiry=900):
        self.host = "%s:%s" % (hostname, port)
        self.server = memcache.Client([self.host])
        self.expiry = expiry

    def set(self, key, value):
        """
        This method is used to set a new value
        in the memcache server.
        """
        self.server.set(self.normalize_key(key), value, self.expiry)

    def get(self, key):
        """
        This method is used to retrieve a value
        from the memcache server.
        """
        return self.server.get(self.normalize_key(key))

    def normalize_key(self, key):
        key = str(key)
        key = key.replace(' ', '-')
        return key
