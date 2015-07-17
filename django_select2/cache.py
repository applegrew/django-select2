# -*- coding: utf-8 -*-
"""
Shared memory across multiple machines to the heavy ajax lookups.

Select2 uses django.core.cache_ to share fields across
multiple threads and even machines.

Select2 uses the cabhe backend defind in the setting
``SELECT2_CACHE_BACKEND`` [default=``default``].

It is advised to always setup a separate cache server for Select2.

.. _django.core.cache: https://docs.djangoproject.com/en/dev/topics/cache/
"""
from __future__ import absolute_import, unicode_literals

from django.core.cache import _create_cache, caches

from . import __MEMCACHE_HOST as MEMCACHE_HOST
from . import __MEMCACHE_PORT as MEMCACHE_PORT
from . import __MEMCACHE_TTL as MEMCACHE_TTL
from .conf import settings

__all__ = ('cache', )

if MEMCACHE_HOST and MEMCACHE_PORT:
    # @todo: Deprecated and to be removed in v5
    location = ':'.join((MEMCACHE_HOST, MEMCACHE_PORT))
    cache = _create_cache('django.core.cache.backends.memcached.MemcachedCache',
                          LOCATION=MEMCACHE_HOST, TIMEOUT=MEMCACHE_TTL)
else:
    cache = caches[settings.SELECT2_CACHE_BACKEND]
