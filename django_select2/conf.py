"""Settings for Django-Select2."""
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
                "BACKEND": "django_redis.cache.RedisCache",
                "LOCATION": "redis://127.0.0.1:6379/2",
                "OPTIONS": {
                    "CLIENT_CLASS": "django_redis.client.DefaultClient",
                }
            }
        }

        # Set the cache backend to select2
        SELECT2_CACHE_BACKEND = 'select2'

    .. tip:: To ensure a consistent state across all you machines you need to user
        a consistent external cache backend like Memcached, Redis or a database.

    .. note::
        Should you have copied the example configuration please make sure you
        have Redis setup. It's recommended to run a separate Redis server in a
        production environment.

    .. note:: The timeout of select2's caching backend determines
        how long a browser session can last.
        Once widget is dropped from the cache the json response view will return a 404.
    """
    CACHE_PREFIX = 'select2_'
    """
    If you caching backend does not support multiple databases
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

    I18N_PATH = '//cdnjs.cloudflare.com/ajax/libs/select2/4.0.3/js/i18n'
    """
    The base URI for the Select2 i18n files. By default this points to the Cloudflare CDN.

    If you want to select the version of the I18N library used, or want to serve it from
    the local 'static' resources, add a line to your settings.py like so::

        SELECT2_I18N_PATH = 'assets/js/i18n'

    .. tip:: Change this setting to a local asset in your development environment to
        develop without an Internet connection.
    """

    I18N_AVAILABLE_LANGUAGES = [
        'ar',
        'az',
        'bg',
        'ca',
        'cs',
        'da',
        'de',
        'el',
        'en',
        'es',
        'et',
        'eu',
        'fa',
        'fi',
        'fr',
        'gl',
        'he',
        'hi',
        'hr',
        'hu',
        'id',
        'is',
        'it',
        'ja',
        'km',
        'ko',
        'lt',
        'lv',
        'mk',
        'ms',
        'nb',
        'nl',
        'pl',
        'pt-BR',
        'pt',
        'ro',
        'ru',
        'sk',
        'sr-Cyrl',
        'sr',
        'sv',
        'th',
        'tr',
        'uk',
        'vi',
        'zh-CN',
        'zh-TW',
    ]
    """
    List of available translations.

    List of ISO 639-1 language codes that are supported by Select2.
    If currently set language code (e.g. using the HTTP ``Accept-Language`` header)
    is in this list, Django-Select2 will use the language code to create load
    the proper translation.

    The full path for the language file consists of::

        from django.utils import translations

        full_path = "{i18n_path}/{language_code}.js".format(
            i18n_path=settings.DJANGO_SELECT2_I18N,
            language_code=translations.get_language(),
        )

    ``settings.DJANGO_SELECT2_I18N`` refers to :attr:`.I18N_PATH`.
    """

    class Meta:
        """Prefix for all Django-Select2 settings."""

        prefix = 'SELECT2'
