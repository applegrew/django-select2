Django-Select2
==============

|version| |ci| |coverage| |license|

This is a `Django`_ integration of `Select2`_.

The app includes Select2 driven Django Widgets.

.. note::
    Django's admin comes with builtin support for Select2
    since version 2.0 via the `autocomplete_fields`_ feature.

Installation
------------

1. Install ``django_select2``

.. code:: python

    pip install django_select2

2. Add ``django_select2`` to your ``INSTALLED_APPS`` in your project
   settings.

3. Add ``django_select`` to your urlconf if you use any "Auto" fields.

.. code:: python

    url(r'^select2/', include('django_select2.urls')),

Documentation
-------------

Documentation available at http://django-select2.readthedocs.io/.

External Dependencies
---------------------

-  jQuery version 2 This is not included in the package since it is
   expected that in most scenarios this would already be available.

Example Application
-------------------

Please see ``tests/testapp`` application. This application is used to
manually test the functionalities of this package. This also serves as a
good example.

Changelog
---------

See `Github releases`_


.. _Django: https://www.djangoproject.com/
.. _Select2: http://ivaynberg.github.com/select2/
.. _autocomplete_fields: https://docs.djangoproject.com/en/stable/ref/contrib/admin/#django.contrib.admin.ModelAdmin.autocomplete_fields
.. _CHANGELOG.md: CHANGELOG.md
.. _Github releases: https://github.com/applegrew/django-select2/releases

.. |version| image:: https://img.shields.io/pypi/v/Django-Select2.svg
   :target: https://pypi.python.org/pypi/Django-Select2/
.. |ci| image:: https://travis-ci.org/applegrew/django-select2.svg?branch=master
   :target: https://travis-ci.org/applegrew/django-select2
.. |coverage| image:: https://codecov.io/gh/applegrew/django-select2/branch/master/graph/badge.svg
   :target: https://codecov.io/gh/applegrew/django-select2
.. |license| image:: https://img.shields.io/badge/license-APL2-blue.svg
   :target: https://raw.githubusercontent.com/applegrew/django-select2/master/LICENSE.txt
