"""
This is a Django_ integration of Select2_.

The app includes Select2 driven Django Widgets and Form Fields.

.. _Django: https://www.djangoproject.com/
.. _Select2: http://ivaynberg.github.com/select2/

Widgets
-------

These components are responsible for rendering the necessary Javascript and HTML markups. Since this whole
package is to render choices using Select2 Javascript library, hence these components are meant to be used
with choice fields.

Widgets are generally of two types :-

    1. **Light** --
    They are not meant to be used when there are too many options, say, in thousands. This
    is because all those options would have to be pre-rendered onto the page and Javascript would
    be used to search through them. Said that, they are also one the most easiest to use. They are almost
    drop-in-replacement for Django's default select widgets.

    2. **Heavy** --
    They are suited for scenarios when the number of options are large and need complex queries
    (from maybe different sources) to get the options. This dynamic fetching of options undoubtably requires
    Ajax communication with the server. Django-Select2 includes a helper JS file which is included automatically,
    so you need not worry about writing any Ajax related JS code. Although on the server side you do need to
    create a view specifically to respond to the queries.

    Heavies have further specialized versions called -- **Auto Heavy**. These do not require views to server Ajax
    request. When they are instantiated, they register themselves with one central view which handels Ajax requests
    for them.

Heavy widgets have the word 'Heavy' in their name. Light widgets are normally named, i.e. there is no 'Light' word
in their names.

**Available widgets:**

:py:class:`.Select2Widget`, :py:class:`.Select2MultipleWidget`, :py:class:`.HeavySelect2Widget`, :py:class:`.HeavySelect2MultipleWidget`,
:py:class:`.AutoHeavySelect2Widget`, :py:class:`.AutoHeavySelect2MultipleWidget`

`Read more`_

Fields
------

These are pre-implemented choice fields which use the above widgets. It is highly recommended that you use them
instead of rolling your own.

The fields available are good for general purpose use, although more specialized versions too are available for
your ease.

**Available fields:**

:py:class:`.Select2ChoiceField`, :py:class:`.Select2MultipleChoiceField`, :py:class:`.HeavySelect2ChoiceField`,
:py:class:`.HeavySelect2MultipleChoiceField`, :py:class:`.HeavyModelSelect2ChoiceField`,
:py:class:`.HeavyModelSelect2MultipleChoiceField`, :py:class:`.ModelSelect2Field`, :py:class:`.ModelSelect2MultipleField`,
:py:class:`.AutoSelect2Field`, :py:class:`.AutoSelect2MultipleField`, :py:class:`.AutoModelSelect2Field`,
:py:class:`.AutoModelSelect2MultipleField`

Views
-----

The view - `Select2View`, exposed here is meant to be used with 'Heavy' fields and widgets.

**Imported:**

:py:class:`.Select2View`, :py:data:`.NO_ERR_RESP`

`Read more`_

.. _Read more: http://blog.applegrew.com/2012/08/django-select2/

"""

__version__ = "3.1.1"

__RENDER_SELECT2_STATICS = False

from django.conf import settings
if settings.configured:
    __RENDER_SELECT2_STATICS = getattr(settings, 'AUTO_RENDER_SELECT2_STATICS', True)

    from .widgets import Select2Widget, Select2MultipleWidget, HeavySelect2Widget, HeavySelect2MultipleWidget, \
        AutoHeavySelect2Widget, AutoHeavySelect2MultipleWidget
    from .fields import Select2ChoiceField, Select2MultipleChoiceField, HeavySelect2ChoiceField, \
        HeavySelect2MultipleChoiceField, HeavyModelSelect2ChoiceField, HeavyModelSelect2MultipleChoiceField, \
        ModelSelect2Field, ModelSelect2MultipleField, AutoSelect2Field, AutoSelect2MultipleField, \
        AutoModelSelect2Field, AutoModelSelect2MultipleField 
    from .views import Select2View, NO_ERR_RESP


