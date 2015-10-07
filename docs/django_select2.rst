API Documentation
=================

Configuration
-------------

.. automodule:: django_select2.conf
    :members:
    :undoc-members:
    :show-inheritance:

Widgets
-------

.. automodule:: django_select2.forms
    :members:
    :undoc-members:
    :show-inheritance:

URLs
----

.. automodule:: django_select2.urls
    :members:
    :undoc-members:
    :show-inheritance:

Views
-----

.. automodule:: django_select2.views
    :members:
    :undoc-members:
    :show-inheritance:

Cache
-----

.. automodule:: django_select2.cache
    :members:
    :undoc-members:
    :show-inheritance:


JavaScript
----------

DjangoSelect2 handles the initialization of select2 fields automatically. Just include
``{{ form.media.js }}`` in your template before the closing ``body`` tag. That's it!

If you insert forms after page load or if you want to handle the initialization
yourself, DjangoSelect2 provides a jQuery-Plugin. It will handle both normal and
heavy fields. Simply call ``djangoSelect2(options)`` on your select fields.::

        $('.django-select2').djangoSelect2();


You can pass see `Select2 options <https://select2.github.io/options.html>`_ if needed::

        $('.django-select2').djangoSelect2({placeholder: 'Select an option'});
