# -*- coding:utf-8 -*-
from __future__ import absolute_import, unicode_literals

from .models import KeyMap


class Client(object):
    def set(self, key, value):
        """
        This method is used to set a new value
        in the db.
        """
        o = self.get(key)
        if o is None:
            o = KeyMap()
            o.key = key

        o.value = value
        o.save()

    def get(self, key):
        """
        This method is used to retrieve a value
        from the db.
        """
        try:
            return KeyMap.objects.get(key=key).value
        except KeyMap.DoesNotExist:
            return None
