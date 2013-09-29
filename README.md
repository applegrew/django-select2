Django-Select2
==============

This is a [Django](https://www.djangoproject.com/) integration of [Select2](http://ivaynberg.github.com/select2/).

The app includes Select2 driven Django Widgets and Form Fields.

Installation
============

1. Install `django_select2`

        pip install django_select2

2. Add `django_select2` to your `INSTALLED_APPS` in your project settings.

3. When deploying on production server, run :-

        python manage.py collectstatic
        
4. Add `django_select` to your urlconf for Ajax support
   
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
* Memcached (python-memcached) - If you plan on running multiple python processes with `GENERATE_RANDOM_SELECT2_ID` enabled, then you need to turn on `ENABLE_SELECT2_MULTI_PROCESS_SUPPORT`. In that mode it is highly recommended that you use Memcached, to minimize DB hits.

Example Application
===================
Please see `testapp` application. This application is used to manually test the functionalities of this package. This also serves as a good example.

You need only Django 1.4 or above to run that. It might run on older versions but that is not tested.

Special Thanks
==============

* Samuel Goldszmidt (@ouhouhsami) for reporting many fundamental issues with the code, because of which versions 2.0 and 2.0.1 were released.

Changelog Summary
=================

### v4.2.1

* Finally fixed performance issue[#54](https://github.com/applegrew/django-select2/issues/54) (and issue[#41](https://github.com/applegrew/django-select2/issues/41)) in widgets when backing field is based on models and the field has an initial value.

### v4.2.0

* Updated Select2 to version 3.4.2. **Please note**, that if you need any of the Select2 locale files, then you need to download them yourself from http://ivaynberg.github.com/select2/ and add to your project.
* Tagging support added. See [Field API reference](http://django-select2.readthedocs.org/en/latest/ref_fields.html) in documentation.

### v4.1.0

* Updated Select2 to version 3.4.1. **Please note**, that if you need any of the Select2 locale files, then you need to download them yourself from http://ivaynberg.github.com/select2/ and add to your project.
* Address isssue[#36](https://github.com/applegrew/django-select2/issues/36) - Fix importerror under django1.6.
* Fuxed the way `setup.py` handles unicode files while minfying them during package build.
* Address isssue[#39](https://github.com/applegrew/django-select2/issues/39) - MultipleSelect2HiddenInput.render() should use mark_safe().
* Address isssue[#45](https://github.com/applegrew/django-select2/issues/45) - MultipleSelect2HiddenInput returns bad has_changed value.

### v4.0.0

* Main version number bumped to bring your attention to the fact that the default Id generation scheme has now changed. Now Django Select2 will use hashed paths of fields to generate their Ids. The old scheme of generating random Ids are still there. You can enable that by setting `GENERATE_RANDOM_SELECT2_ID` to `True`.

### v3.3.1

* Addressed issue[#30](https://github.com/applegrew/django-select2/issues/30).
* Merged pull request[#31](https://github.com/applegrew/django-select2/issues/31).
* Added `light` parameter to `import_django_select2_js`, `import_django_select2_css` and `import_django_select2_js_css` template tags. Please see doc's "Getting Started", for more details.

### v3.3.0

* Updated Select2 to version 3.3.1.
* Added multi-process support. ([Issue#28](https://github.com/applegrew/django-select2/issues/28)).
* Addressed issue[#26](https://github.com/applegrew/django-select2/issues/26).
* Addressed issue[#24](https://github.com/applegrew/django-select2/issues/24).
* Addressed issue[#23](https://github.com/applegrew/django-select2/issues/23).
* Addressed some typos.

### v3.2.0

* Fixed issue[#20](https://github.com/applegrew/django-select2/issues/20). Infact while fixing that I realised that heavy components do not need the help of cookies, infact due to a logic error in previous code the cookies were not being used anyway. Now Django Select2 does not use cookies etc.
* Few more bugs fixed in `heav_data.js`.
* Now production code will use minimized versions of js and css files.
* Codes added in `setup.py` to automate the task of minimizing js and css files, using a web service.

### v3.1.5

* Merged pull request (issue[#17](https://github.com/applegrew/django-select2/issues/17)). Which allows the user to pass some extra data to Select2 clients-side component.
* Updated License. The previous one was inadequently worded. Now this project use Apache 2.0 license.

### v3.1.4

* Manually merged changes from pull request (issue[#16](https://github.com/applegrew/django-select2/issues/16)).
* Django Select2 widgets now allow passing of any Select2 Js options. Previously it used to allow only white-listed options. Now it will block only black-listed options. For example, Light Select2 widgets won't allow you to set `multiple` option, since it is an error to set them when Select2 Js is bound to `<select>` fields.

### v3.1.3

* Addressed enhancement issue[#12](https://github.com/applegrew/django-select2/issues/12).
* Addressed enhancement issue[#11](https://github.com/applegrew/django-select2/issues/11).
* Addressed performance issue[#8](https://github.com/applegrew/django-select2/issues/8).

### v3.1.2

* Fixed issue[#7](https://github.com/applegrew/django-select2/issues/7).

### v3.1.1

* Bumping up minor version since Select2 JS has been updated to version 3.2. It seems Select2 JS now includes new higher resolution icons for [Retina displays](http://en.wikipedia.org/wiki/Retina_Display).
* Fixed an issue in `setup.py` because of which `templatetags` directory was not included in last PIP releases' tar file.

### v3.0.2

* Added `AUTO_RENDER_SELECT2_STATICS` settings. This, when specified and set to `False` in `settings.py` then Django_Select2 widgets won't automatically include the required scripts and stylesheets. When this setting is `True` (default) then every Select2 field on the page will output `<script>` and `<link>` tags to include the required JS and CSS files. This is convinient but will output the same JS and CSS files multiple times if there are more than one Select2 fields on the page.
* Added `django_select2_tags` template tags to manually include the required JS and CSS files, when `AUTO_RENDER_SELECT2_STATICS` is turned off.

### v3.0.1

* Revised the design of heavy fields. The previous design didn't quite make it easy to back heavy fields by big data sources. See `fields.HeavyChoiceField` class and its methods' docs for more info.
* Updated docs.
* Some more fixes for issue[#4](https://github.com/applegrew/django-select2/issues/4).
* Updated Select2 JS to version 3.1.

### v3.0

* Added docs.
* Some bug fixes. See issue[#4](https://github.com/applegrew/django-select2/issues/4).
* `widgets.Select2Mixin.__init__` now accepts `select2_options` kwarg to override its `options` settings. Previously `attrs` were being used for this too. This means backward compatibility has been broken here. `attrs` will no longer override `options` values. **The major release version has been changed to 3, because of this backward incompatible change.**

### v2.0.1

* Auto id registration fixes.

### v2.0

* Mostly major bug fixes in code and design. The changes were many, raising the possibility of backward incompatibility. However, the backward incompatibility would be subtle.

* Auto fields (sub-classes of AutoViewFieldMixin) now accepts `auto_id` parameter. This can be used to provide custom id for the field. The default is 'module.field_class_name'. Ideally only the first instance of an auto field is registered. This parameter can be used to force registration of additional instances by passing a unique value.

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
