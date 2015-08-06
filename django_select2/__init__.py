# -*- coding: utf-8 -*-
"""
This is a Django_ integration of Select2_.

The app includes Select2 driven Django Widgets and Form Fields.

.. _Django: https://www.djangoproject.com/
.. _Select2: http://ivaynberg.github.com/select2/

Widgets
-------

These components are responsible for rendering
the necessary JavaScript and HTML markups. Since this whole
package is to render choices using Select2 JavaScript
library, hence these components are meant to be used
with choice fields.

Widgets are generally of two types :-

    1. **Light** --
    They are not meant to be used when there
    are too many options, say, in thousands.
    This is because all those options would
    have to be pre-rendered onto the page
    and JavaScript would be used to search
    through them. Said that, they are also one
    the most easiest to use. They are almost
    drop-in-replacement for Django's default
    select widgets.

    2. **Heavy** --
    They are suited for scenarios when the number of options
    are large and need complex queries (from maybe different
    sources) to get the options.
    This dynamic fetching of options undoubtedly requires
    Ajax communication with the server. Django-Select2 includes
    a helper JS file which is included automatically,
    so you need not worry about writing any Ajax related JS code.
    Although on the server side you do need to create a view
    specifically to respond to the queries.

    Heavies have further specialized versions called -- **Auto Heavy**.
    These do not require views to serve Ajax requests.
    When they are instantiated, they register themselves
    with one central view which handles Ajax requests for them.

Heavy widgets have the word 'Heavy' in their name.
Light widgets are normally named, i.e. there is no
'Light' word in their names.

**Available widgets:**

:py:class:`.Select2Widget`,
:py:class:`.Select2MultipleWidget`,
:py:class:`.HeavySelect2Widget`,
:py:class:`.HeavySelect2MultipleWidget`,
:py:class:`.AutoHeavySelect2Widget`,
:py:class:`.AutoHeavySelect2MultipleWidget`,
:py:class:`.HeavySelect2TagWidget`,
:py:class:`.AutoHeavySelect2TagWidget`

`Read more`_

Views
-----

The view - `Select2View`, exposed here is meant
to be used with 'Heavy' fields and widgets.

**Imported:**

:py:class:`.Select2View`, :py:data:`.NO_ERR_RESP`

`Read more`_

.. _Read more: http://blog.applegrew.com/2012/08/django-select2/

"""

__version__ = "5.0.0"
