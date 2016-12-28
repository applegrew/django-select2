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

    JS = '//cdnjs.cloudflare.com/ajax/libs/select2/4.0.3/js/select2.min.js'
    """
    The URI for the Select2 JS file. By default this points to the Cloudflare CDN.

    If you want to select the version of the JS library used, or want to serve it from
    the local 'static' resources, add a line to your settings.py like so::

        SELECT2_JS = 'assets/js/select2.min.js'

    .. tip:: Change this setting to a local asset in your development environment to
        develop without an Internet connection.
    """

    CSS = '//cdnjs.cloudflare.com/ajax/libs/select2/4.0.3/css/select2.min.css'
    """
    The URI for the Select2 CSS file. By default this points to the Cloudflare CDN.

    If you want to select the version of the library used, or want to serve it from
    the local 'static' resources, add a line to your settings.py like so::

        SELECT2_CSS = 'assets/css/select2.css'

    .. tip:: Change this setting to a local asset in your development environment to
        develop without an Internet connection.
    """

    class Meta:
        """Prefix for all Django-Select2 settings."""

        prefix = 'SELECT2'
