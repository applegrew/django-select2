Django-Select2
==============

[![PyPi Version](https://img.shields.io/pypi/v/Django-Select2.svg)](https://pypi.python.org/pypi/Django-Select2/)
[![Build Status](https://travis-ci.org/applegrew/django-select2.svg?branch=master)](https://travis-ci.org/applegrew/django-select2)
[![Code Health](https://landscape.io/github/applegrew/django-select2/master/landscape.svg?style=flat)](https://landscape.io/github/applegrew/django-select2/master)
[![Test Coverage](https://coveralls.io/repos/applegrew/django-select2/badge.png?branch=master)](https://coveralls.io/r/applegrew/django-select2)
[![GitHub license](https://img.shields.io/badge/license-APL2-blue.svg)](https://raw.githubusercontent.com/applegrew/django-select2/master/LICENSE.txt)
[![Join the chat at https://gitter.im/applegrew/django-select2](https://badges.gitter.im/Join%20Chat.svg)](https://gitter.im/applegrew/django-select2?utm_source=badge&utm_medium=badge&utm_campaign=pr-badge&utm_content=badge)

This is a [Django](https://www.djangoproject.com/) integration of [Select2](http://ivaynberg.github.com/select2/).

The app includes Select2 driven Django Widgets and Form Fields.

Installation
============

1. Install `django_select2`

        pip install django_select2

2. Add `django_select2` to your `INSTALLED_APPS` in your project settings.

3. When deploying on production server, run :-

        python manage.py collectstatic

4. Add `django_select` to your urlconf if you use any 'Auto' fields.

        url(r'^select2/', include('django_select2.urls')),


Documentation
=============

Documentation available at http://django-select2.readthedocs.org/.

More details
============

More details can be found on my blog at - http://blog.applegrew.com/2012/08/django-select2/.

External Dependencies
=====================

* Django - This is obvious.
* jQuery - This is not included in the package since it is expected that in most scenarios this would already be available.
* Memcached or Redis - If you run more than one node, you'll need a shared memory.


Example Application
===================
Please see `testapp` application. This application is used to manually test the functionalities of this package. This also serves as a good example.

You need only Django 1.4 or above to run that. It might run on older versions but that is not tested.

Special Thanks
==============

* Samuel Goldszmidt (@ouhouhsami) for reporting many fundamental issues with the code, because of which versions 2.0 and 2.0.1 were released.

Official Contributors
=====================

* Johannes Hoppe (@codingjoe)

[Changelog](CHANGELOG.md)
=========================

License
=======

Copyright 2012 Nirupam Biswas

Licensed under the Apache License, Version 2.0 (the "License");
you may not use this project except in compliance with the License.
You may obtain a copy of the License at

[http://www.apache.org/licenses/LICENSE-2.0](http://www.apache.org/licenses/LICENSE-2.0)

Unless required by applicable law or agreed to in writing, software
distributed under the License is distributed on an "AS IS" BASIS,
WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
See the License for the specific language governing permissions and
limitations under the License.
