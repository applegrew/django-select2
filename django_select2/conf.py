# -*- coding: utf-8 -*-
"""Settings for Django-Select2."""
from __future__ import absolute_import, unicode_literals

from appconf import AppConf
from django.conf import settings  # NOQA

__all__ = ('settings', 'Select2Conf')


class Select2Conf(AppConf):

    """Settings for Django-Select2."""

    CACHE_BACKEND = 'default'
    """
    Django-Select2 uses Django's cache to sure a consistent state across multiple machines.

    Example of settings.py::

        CACHES = {
            "default": {
                "BACKEND": "django_redis.cache.RedisCache",
                "LOCATION": "redis://127.0.0.1:6379/1",
                "OPTIONS": {
                    "CLIENT_CLASS": "django_redis.client.DefaultClient",
                }
            },
            'select2': {
                'BACKEND': 'django.core.cache.backends.memcached.MemcachedCache',
                'LOCATION': '127.0.0.1:11211',
            }
        }

        # Set the cache backend to select2
        SELECT2_CACHE_BACKEND = 'select2'

    .. tip:: To ensure a consistent state across all you machines you need to user
        a consistent external cache backend like Memcached, Redis or a database.

    .. note:: The timeout of select2's caching backend determines
        how long a browser session can last.
        Once widget is dropped from the cache the json response view will return a 404.
    """
    CACHE_PREFIX = 'select2_'
    """
    If you caching backend doesn't support multiple databases
    you can isolate select2 using the cache prefix setting.
    It has set `select2_` as a default value, which you can change if needed.
    """

    MEDIA_PREFIX = getattr(settings, 'SELECT2_MEDIA_PREFIX', '//cdnjs.cloudflare.com/ajax/libs/select2/4.0.0/')
    """
    Normally external referenced JavaScript and StyleSheet files are loaded using a CDN. This may be
    unacceptable for some kind of applications, where no Internet connection is available.
    In settings.py, use ``SELECT2_MEDIA_PREFIX`` to override the location where external JS and CSS
    media files shall be loaded from.
    """

    class Meta:
        prefix = 'SELECT2'
