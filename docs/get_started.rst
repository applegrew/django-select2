===========
Get Started
===========

Overview
--------

.. automodule:: django_select2
    :members:

Installation
------------

1. Install ``django_select2``::

        pip install django_select2

2. Add ``django_select2`` to your ``INSTALLED_APPS`` in your project settings.


3. Add ``django_select`` to your ``urlconf`` **if** you use any
:class:`ModelWidgets <.django_select2.forms.ModelSelect2Mixin>`::

        url(r'^select2/', include('django_select2.urls')),


External Dependencies
---------------------

* jQuery version 2
    This is not included in the package since it is expected
    that in most scenarios this would already be available.

Example Application
-------------------
Please see ``tests/testapp`` application.
This application is used to manually test the functionalities of this package.
This also serves as a good example.
