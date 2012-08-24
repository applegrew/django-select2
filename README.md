Django-Select2
==============

This is a [Django](https://www.djangoproject.com/) integration of [Select2](http://ivaynberg.github.com/select2/).

The app includes Select2 driven Django Widgets and Form Fields.

Installation
============

1. Install `django_select2`

        pip install django_select2

1. Add `django_select2` to your `INSTALLED_APPS` in your project settings.
1. When deploying on production server, run :-

        python manage.py collectstatic

More details
============

More details can be found on my blog at - [http://blog.applegrew.com/2012/08/django-select2/](http://blog.applegrew.com/2012/08/django-select2/).

External Dependencies
=====================

* Django - This is obvious.
* jQuery - This is not included in the package since it is expected that in most scenarios this would already be available.

Example Application
===================
Please checkout `testapp` application. This application is used to manually test the functionalities of this component. This also serves as a good example.

You need only django 1.4 or above to run that.

Changelog Summary
=================

### v2.0.1

* Auto id registration fixes.

### v2.0

* Mostly major bug fixes in code and design. The changes were many, raising the possibility of backward incompatibility. However, the backward incompatibility would be subtle.

* Auto fields (sub-classes of AutoViewFieldMixin) now accepts `auto_id` parameter. This can be used to provide custom id for the field. The default is 'module.field_class_name'. Ideally only the first instance of an auto field is registered. This parameter can be used to force registration of additional instances by passing a unique value.
