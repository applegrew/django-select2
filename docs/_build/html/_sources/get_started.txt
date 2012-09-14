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

Available Setting
-----------------

``AUTO_RENDER_SELECT2_STATICS`` [Default ``True``]

This, when specified and set to ``False`` in ``settings.py`` then Django_Select2 widgets won't automatically include the required scripts and stylesheets. When this setting is ``True`` then every Select2 field on the page will output ``<script>`` and ``<link>`` tags to include the required JS and CSS files. This is convinient but will output the same JS and CSS files multiple times if there are more than one Select2 fields on the page.

When this settings is ``False`` then you are responsible for including the JS and CSS files. To help you with this the following template tags are available in ``django_select2_tags``.

	* ``import_django_select2_js`` - Outputs ``<script>`` tags to include all the JS files, required by Light and Heavy widgets.
	* ``import_django_select2_css`` - Outputs ``<link>`` tags to include all the CSS files, required by Light and Heavy widgets.
	* ``import_django_select2_js_css`` - Outputs both ``<script>`` and ``<link>`` tags to include all the JS and CSS files, required by Light and Heavy widgets.

Make sure to include them at the top of the page, prefereably in ``<head>...</head>``.

External Dependencies
---------------------

* Django - This is obvious.
* jQuery - This is not included in the package since it is expected that in most scenarios this would already be available. The above template tags also won't out ``<script>`` tag to include this. You need to do this yourself.

Example Application
-------------------
Please see ``testapp`` application. This application is used to manually test the functionalities of this package. This also serves as a good example.

You need only Django 1.4 or above to run that. It might run on older versions but that is not tested.
