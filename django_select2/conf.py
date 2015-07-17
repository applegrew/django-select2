# -*- coding: utf-8 -*-
from __future__ import absolute_import, unicode_literals

from appconf import AppConf
from django.conf import settings  # NOQA

__all__ = ['settings']


class Select2Conf(AppConf):
    CACHE_BACKEND = 'default'
    CACHE_PREFIX = 'select2_'

    class Meta:
        prefix = 'SELECT2'
