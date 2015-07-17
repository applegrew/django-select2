# -*- coding:utf-8 -*-
from __future__ import absolute_import, unicode_literals


def test_default_cache():
    from django_select2.cache import cache

    cache.set('key', 'value')

    assert cache.get('key') == 'value'
