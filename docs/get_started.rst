===========
Get Started
===========

Overview
--------

.. automodule:: django_select2
    :members:

Assumptions
-----------

* You have a running Django up and running.
* You have form fully working without Django-Select2.

Installation
------------

1. Install ``django_select2``::

        pip install django_select2

2. Add ``django_select2`` to your ``INSTALLED_APPS`` in your project settings.

3. Add ``django_select`` to your ``urlconf``::

        path('select2/', include('django_select2.urls')),

   You can safely skip this one if you do not use any
   :class:`ModelWidgets <.django_select2.forms.ModelSelect2Mixin>`

Quick Start
-----------

Here is a quick example to get you started:

0. Follow the installation instructions above.

1. Replace native Django forms widgets with one of the several ``django_select2.form`` widgets.
   Start by importing them into your ``forms.py``, right next to Django own ones::

     from django import forms
     from django_select2 import forms as s2forms

   Then let's assume you have a model with a choice, a :class:`.ForeignKey`, and a
   :class:`.ManyToManyField`, you would add this information to your Form Meta
   class::

        widgets = {
            'category': s2forms.Select2Widget,
            'author': s2forms.ModelSelect2Widget(model=auth.get_user_model(),
                                                 search_fields=['first_name__istartswith', 'last_name__icontains']),
            'attending': s2forms.ModelSelect2MultipleWidget …
        }

2. Add the CSS to the ``head`` of your Django template::

        {{ form.media.css }}

3. Add the JavaScript to the end of the ``body`` of your Django template::

        {{ form.media.js }}

4. Done - enjoy the wonders of Select2!

External Dependencies
---------------------

* jQuery (version >=2)
    jQuery is not included in the package since it is expected
    that in most scenarios jQuery is already loaded.

Example Application
-------------------
Please see ``tests/testapp`` application.
This application is used to manually test the functionalities of this package.
This also serves as a good example.
