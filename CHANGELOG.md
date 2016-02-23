Changelog Summary
=================

### v5.8.2
* Fixes #260 -- Fixes bug in render choices

### v5.8.0
* Changed signature of `render` and `render_choices` to satisfy Django 1.10 changes.
* Changed widgets' inheritance tree to be more consistent.

### v5.7.1
* Fixes pickle bug of lazy object

### v5.7.0
* Security fix that allows a `field_id` to only be used for the intended JSON endpoint.
  
      Prior to that change you could use any `field_id` on any select2 JSON endpoint.
      Even if the id was intended to be used on a private endpoint if could be used on
      the default one and therefore leak sensitive data.
      
* Breaking change on how `Heavy` widgets are being cached.
      
      Heavy widgets used to add themselves to the cache. Now they add a dictionary to
      the cache containing themselves and the target url.
      
      ```python
      {
          'widget': self,
          'url': self.get_url(),
      }
      ```

### v5.6.0
* Added `label_from_instance` method for model widgets to define custom option labels.

### v5.5.0
* Added settings to delivery static assets from different source.

### v5.4.2
* Fixed initial data not being shown for heavy widgets.

### v5.4.1
* Fixed memory leak in `ModelSelect2Mixin` and subclasses

### v5.4.0
* Added `Select2TagWidget` a light widget with tagging support

### v5.3.0
* Added djangoSelect2 jQuery plugin to support
  dynamic field initialisation

### v5.2.0
* Added pagination

### v5.1.0
* Added search term splitting
* Model widgets get smarter pickling to reduce size and avoid pickling issues

### v5.0.0
Version 5 is a complete rewrite of the package to drastically reduce
the code base and to ensure a future maintainability.

While we feature set remained unchanged, the API changed completely.
Major changes:
* Fields have been removed in favor of widgets.
* All version 4 settings have been removed.
* Template tags have been removed.
* 3rd party javascript is served by a CDN.
* No more inline javascript code.

### v4.3.2

* Use `django.contrib.staticfiles.templatetags.staticfiles.static` over `django.templatetags.static.static` to allow hashing.
* Py23 unicode fixes


### v4.3.1

* Build failure fix.

### v4.3.0

* Now the package supports both Python2 and Python3.
* Django 1.8 support added.
* Many bug fixes.

### v4.2.2

* Misc fixes and enhancements - [61](https://github.com/applegrew/django-select2/pull/61), [64](https://github.com/applegrew/django-select2/issues/64).

### v4.2.1

* Finally fixed performance issue[#54](https://github.com/applegrew/django-select2/issues/54) (and issue[#41](https://github.com/applegrew/django-select2/issues/41)) in widgets when backing field is based on models and the field has an initial value.

### v4.2.0

* Updated Select2 to version 3.4.2. **Please note**, that if you need any of the Select2 locale files, then you need to download them yourself from http://ivaynberg.github.com/select2/ and add to your project.
* Tagging support added. See [Field API reference](http://django-select2.readthedocs.org/en/latest/ref_fields.html) in documentation.

### v4.1.0

* Updated Select2 to version 3.4.1. **Please note**, that if you need any of the Select2 locale files, then you need to download them yourself from http://ivaynberg.github.com/select2/ and add to your project.
* Address isssue[#36](https://github.com/applegrew/django-select2/issues/36) - Fix importerror under django1.6.
* Fixed the way `setup.py` handles Unicode files while minifying them during package build.
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
