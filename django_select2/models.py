# -*- coding:utf-8 -*-
from __future__ import absolute_import, unicode_literals

from django.db import models
from django.utils.encoding import force_text, python_2_unicode_compatible


@python_2_unicode_compatible
class KeyMap(models.Model):
    key = models.CharField(max_length=40, unique=True)
    value = models.CharField(max_length=100)
    accessed_on = models.DateTimeField(auto_now=True)

    def __str__(self):
        return force_text("%s => %s" % (self.key, self.value))
