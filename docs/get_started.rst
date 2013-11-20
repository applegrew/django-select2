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

``GENERATE_RANDOM_SELECT2_ID`` [Default ``False``]
..................................................

As of version 4.0.0 the field's Ids are their paths which have been hashed by SHA1. This Id generation scheme should be sufficient for most applications.

However, if you have a secret government project and fear that SHA1 hashes could be cracked (which is not impossible) to reveal the path and names of your fields then you can enable this mode. This will use timestamps as Ids which have no correlation to the field's name or path.

.. tip:: The field's paths are first salted with Django generated ``SECRET_KEY`` before hashing them.

``ENABLE_SELECT2_MULTI_PROCESS_SUPPORT`` [Default ``False``]
............................................................

This setting cannot be enabled as it is not required when ``GENERATE_RANDOM_SELECT2_ID`` is ``False``.

In production servers usually multiple server processes are run to handle the requests. This poses a problem for Django Select2's Auto fields since they generate unique Id at runtime when ``GENERATE_RANDOM_SELECT2_ID`` is enabled. The clients can identify the fields in ajax query request using only these generated ids. In multi-processes scenario there is no guarantee that the process which rendered the page is the one which will respond to ajax queries.

When this mode is enabled then Django Select2 maintains an id to field key mapping in DB for all processes. Whenever a process does not find an id in its internal map it looks-up in the central DB. From DB it finds the field key. Using the key, the process then looks-up a field instance with that key, since all instances with same key are assumed to be equivalent.

.. tip:: Make sure to run ``python manage.py syncdb`` to create the ``KeyMap`` table.

.. warning:: You need to write your own script to periodically purge old data from ``KeyMap`` table. You can take help of ``accessed_on`` column. You need to decide the criteria on which basis you will purge the rows.


``SELECT2_MEMCACHE_HOST`` [Default ``None``], ``SELECT2_MEMCACHE_PORT`` [Default ``None``], ``SELECT2_MEMCACHE_TTL`` [Default ``900``]
.......................................................................................................................................

When ``ENABLE_SELECT2_MULTI_PROCESS_SUPPORT`` is enabled then all processes will hit DB to get the mapping for the ids they are not aware of. For performance reasons it is recommended that you install Memcached and set the above settings appropriately.

Also note that, when you set the above you need to install ``python-memcached`` library too.

``SELECT2_BOOTSTRAP`` [Default ``False``]
............................................................

Setting to True will include the CSS for making Select2 fit in with Bootstrap a bit better using the css found here https://github.com/fk/select2-bootstrap-css.

External Dependencies
---------------------

* Django - This is obvious.
* jQuery - This is not included in the package since it is expected that in most scenarios this would already be available. The above template tags also won't output ``<script>`` tag to include this. You need to do this yourself.
* Memcached (python-memcached) - If you plan on running multiple python processes, which is usually the case in production, then you need to turn on ``ENABLE_SELECT2_MULTI_PROCESS_SUPPORT``. In that mode it is highly recommended that you use Memcached, to minimize DB hits.

Example Application
-------------------
Please see ``testapp`` application. This application is used to manually test the functionalities of this package. This also serves as a good example.

You need only Django 1.4 or above to run that. It might run on older versions but that is not tested.
