===========
Get Started
===========

Overview
--------

.. automodule:: django_select2
    :members:

Installation
------------

1. Install `django_select2`::

        pip install django_select2

2. Add `django_select2` to your `INSTALLED_APPS` in your project settings.

3. When deploying on production server, run::

        python manage.py collectstatic

4. Add `django_select` to your urlconf **if** you use any 'Auto' fields::

        url(r'^select2/', include('django_select2.urls')),

5. (Optionally) If you need multiple processes support, then::

        python manage.py syncdb

Available Settings
------------------

``AUTO_RENDER_SELECT2_STATICS`` [Default ``True``]
..................................................

This, when specified and set to ``False`` in ``settings.py`` then Django_Select2 widgets won't automatically include the required scripts and stylesheets. When this setting is ``True`` then every Select2 field on the page will output ``<script>`` and ``<link>`` tags to include the required JS and CSS files. This is convenient but will output the same JS and CSS files multiple times if there are more than one Select2 fields on the page.

When this settings is ``False`` then you are responsible for including the JS and CSS files. To help you with this the following template tags are available in ``django_select2_tags``.

    * ``import_django_select2_js`` - Outputs ``<script>`` tags to include all the JS files, required by Light and Heavy widgets.
    * ``import_django_select2_css`` - Outputs ``<link>`` tags to include all the CSS files, required by Light and Heavy widgets.
    * ``import_django_select2_js_css`` - Outputs both ``<script>`` and ``<link>`` tags to include all the JS and CSS files, required by Light and Heavy widgets.

.. tip:: Make sure to include them at the top of the page, preferably in ``<head>...</head>``.

.. note:: (Since version 3.3.1) The above template tags accept one argument ``light``. Default value for that is ``0``.
    If that is set to ``1`` then only the JS and CSS libraries needed by Select2Widget (Light fields) are rendered.
    That effectively leaves out ``heavy.js`` and ``extra.css``.

``SELECT2_CACHE_BACKEND`` [Default ``default``]
...............................................

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

.. note:: Select2 requires the cache to never expire. Therefore you should avoid clearing the cache.
As third party apps might add unpredictable behavior we recommend to always use an separate cache server.

``ENABLE_SELECT2_MULTI_PROCESS_SUPPORT`` [Default ``False``]
............................................................

.. warning:: Deprecated in favour of ``SELECT2_CACHE_BACKEND``. Will be removed in version 5.

Since version 4.3 django-select2 supports multiprocessing support out of the box.
If you want to have multiple machine support take a look at ``SELECT2_CACHE_BACKEND``.


``SELECT2_MEMCACHE_HOST`` [Default ``None``], ``SELECT2_MEMCACHE_PORT`` [Default ``None``]
..........................................................................................

.. warning:: Deprecated in favour of ``SELECT2_CACHE_BACKEND``. Will be removed in version 5.

Since version 4.3 dajngo-select2 uses Django's own caching solution.
The hostname and port will be used to create a new django cache backend.

.. note:: It is recommended to upgrade to ``SELECT2_CACHE_BACKEND`` to avoid cache consistency issues.

``SELECT2_BOOTSTRAP`` [Default ``False``]
.........................................

Setting to True will include the CSS for making Select2 fit in with Bootstrap a bit better using the css found here https://github.com/fk/select2-bootstrap-css.

External Dependencies
---------------------

* Django - This is obvious.
* jQuery - This is not included in the package since it is expected that in most scenarios this would already be available. The above template tags also won't output ``<script>`` tag to include this. You need to do this yourself.
* Memcached (python-memcached) - If you plan on running multiple Python processes, which is usually the case in production, then you need to turn on ``ENABLE_SELECT2_MULTI_PROCESS_SUPPORT``. In that mode it is highly recommended that you use Memcached, to minimize DB hits.

Example Application
-------------------
Please see ``testapp`` application. This application is used to manually test the functionalities of this package. This also serves as a good example.

You need only Django 1.4 or above to run that. It might run on older versions but that is not tested.
