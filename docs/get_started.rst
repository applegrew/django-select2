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

Quick Start
-----------

Here is a quick example to get you started:

0. Follow the installation instructions above.

1. Add a select2 widget to the form. For example if you wanted Select2 with multi-select you would use
``Select2MultipleWidget``
Replacing::

        class MyForm(forms.Form):
            things = ModelMultipleChoiceField(queryset=Thing.objects.all())

with::

        from django_select2.forms import Select2MultipleWidget
        
        class MyForm(forms.Form):
            things = ModelMultipleChoiceField(queryset=Thing.objects.all(), widget=Select2MultipleWidget)

2. Add the CSS to the ``head`` of your Django template::

        {{ form.media.css }}

3. Add the JavaScript to the end of the ``body`` of your Django template::

        {{ form.media.js }}

4. Done - enjoy the wonders of Select2!

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
