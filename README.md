Django-Select2
==============

[![PyPi Version](https://img.shields.io/pypi/v/Django-Select2.svg)](https://pypi.python.org/pypi/Django-Select2/)
[![Build Status](https://travis-ci.org/applegrew/django-select2.svg?branch=master)](https://travis-ci.org/applegrew/django-select2)
[![Test Coverage](https://coveralls.io/repos/applegrew/django-select2/badge.svg?branch=master)](https://coveralls.io/r/applegrew/django-select2)
[![GitHub license](https://img.shields.io/badge/license-APL2-blue.svg)](https://raw.githubusercontent.com/applegrew/django-select2/master/LICENSE.txt)
[![Join the chat at https://gitter.im/applegrew/django-select2](https://badges.gitter.im/Join%20Chat.svg)](https://gitter.im/applegrew/django-select2?utm_source=badge&utm_medium=badge&utm_campaign=pr-badge&utm_content=badge)

This is a [Django](https://www.djangoproject.com/) integration of [Select2](http://ivaynberg.github.com/select2/).

The app includes Select2 driven Django Widgets.

## Installation


1. Install `django_select2`

        pip install django_select2

2. Add `django_select2` to your `INSTALLED_APPS` in your project settings.

3. Add `django_select` to your urlconf if you use any 'Auto' fields.

        url(r'^select2/', include('django_select2.urls')),


### Upgrade from Version 4

Version 5 is a complete rewrite of the package to drastically reduce
the code base and to ensure a future maintainability.

While we feature set remained unchanged, the API changed completely.
Major changes:
- Fields have been removed in favor of widgets.
- All version 4 settings have been removed.
- Template tags have been removed.
- 3rd party javascript is served by a CDN.
- No more inline javascript code.

#### Upgrade can be done in 5 simple steps:

1. Remove all existing and to setup the new cache backend.
2. Remove the old template tags from your templates:
 1. `import_django_select2_js`
 2. `import_django_select2_css`
 3. `import_django_select2_js_css`
3. Add `form.media.css` to the top and `form.media.js`
 to the bottom of your base template.
4. Upgrade to jQuery version 2, if you are still running version 1.
5. Replace old fields with new widgets.


## Documentation


Documentation available at http://django-select2.readthedocs.io/.

## External Dependencies


* jQuery version 2
    This is not included in the package since it is expected
    that in most scenarios this would already be available.


## Example Application

Please see `tests/testapp` application.
This application is used to manually test the functionalities of this package.
This also serves as a good example.

## Special Thanks


* Samuel Goldszmidt (@ouhouhsami) for reporting many fundamental issues with the code, because of which versions 2.0 and 2.0.1 were released.

## Official Contributors

* Johannes Hoppe (@codingjoe)

## Changelog

See [CHANGELOG.md](CHANGELOG.md)

## License

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
