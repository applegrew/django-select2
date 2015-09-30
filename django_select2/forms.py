# -*- coding: utf-8 -*-
"""
Django-Select2 Widgets.

These components are responsible for rendering
the necessary HTML data markups. Since this whole
package is to render choices using Select2 JavaScript
library, hence these components are meant to be used
with choice fields.

Widgets are generally of two types:

    1. **Light** --
    They are not meant to be used when there
    are too many options, say, in thousands.
    This is because all those options would
    have to be pre-rendered onto the page
    and JavaScript would be used to search
    through them. Said that, they are also one
    the most easiest to use. They are a
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

    3. **Model** --
    Model-widgets are a further specialized versions of Heavies.
    These do not require views to serve Ajax requests.
    When they are instantiated, they register themselves
    with one central view which handles Ajax requests for them.

Heavy widgets have the word 'Heavy' in their name.
Light widgets are normally named, i.e. there is no
'Light' word in their names.

.. inheritance-diagram:: django_select2.forms
    :parts: 1

"""
from __future__ import absolute_import, unicode_literals

from functools import reduce

from django import forms
from django.core import signing
from django.core.urlresolvers import reverse_lazy
from django.db.models import Q
from django.forms.models import ModelChoiceIterator
from django.utils.encoding import force_text

from .cache import cache
from .conf import settings


class Select2Mixin(object):

    """
    The base mixin of all Select2 widgets.

    This mixin is responsible for rendering the necessary
    data attributes for select2 as well as adding the static
    form media.
    """

    def build_attrs(self, extra_attrs=None, **kwargs):
        """Add select2 data attributes."""
        attrs = super(Select2Mixin, self).build_attrs(extra_attrs=extra_attrs, **kwargs)
        if self.is_required:
            attrs.setdefault('data-allow-clear', 'false')
        else:
            attrs.setdefault('data-allow-clear', 'true')
            attrs.setdefault('data-placeholder', '')

        attrs.setdefault('data-minimum-input-length', 0)
        if 'class' in attrs:
            attrs['class'] += ' django-select2'
        else:
            attrs['class'] = 'django-select2'
        return attrs

    def render_options(self, choices, selected_choices):
        """Render options including an empty one, if the field is not required."""
        output = '<option></option>' if not self.is_required else ''
        output += super(Select2Mixin, self).render_options(choices, selected_choices)
        return output

    def _get_media(self):
        """
        Construct Media as a dynamic property.

        .. Note:: For more information visit
            https://docs.djangoproject.com/en/1.8/topics/forms/media/#media-as-a-dynamic-property
        """
        return forms.Media(
            js=('//cdnjs.cloudflare.com/ajax/libs/select2/4.0.0/js/select2.min.js',
                'django_select2/django_select2.js'),
            css={'screen': ('//cdnjs.cloudflare.com/ajax/libs/select2/4.0.0/css/select2.min.css',)}
        )

    media = property(_get_media)


class Select2Widget(Select2Mixin, forms.Select):

    """
    Select2 drop in widget.

    Example usage::

        class MyModelForm(forms.ModelForm):
            class Meta:
                model = MyModel
                fields = ('my_field', )
                widgets = {
                    'my_field': Select2Widget
                }

    or::

        class MyForm(forms.Form):
            my_choice = forms.ChoiceField(widget=Select2Widget)

    """

    pass


class Select2MultipleWidget(Select2Mixin, forms.SelectMultiple):

    """
    Select2 drop in widget for multiple select.

    Works just like :class:`.Select2Widget` but for multi select.
    """

    pass


class HeavySelect2Mixin(Select2Mixin):

    """Mixin that adds select2's ajax options and registers itself on django's cache."""

    def __init__(self, **kwargs):
        """
        Return HeavySelect2Mixin.

        :param data_view: url pattern name
        :type data_view: str
        :param data_url: url
        :type data_url: str
        :return:
        """
        self.data_view = kwargs.pop('data_view', None)
        self.data_url = kwargs.pop('data_url', None)
        if not (self.data_view or self.data_url):
            raise ValueError('You must ether specify "data_view" or "data_url".')
        self.userGetValTextFuncName = kwargs.pop('userGetValTextFuncName', 'null')
        super(HeavySelect2Mixin, self).__init__(**kwargs)

    def get_url(self):
        """Return url from instance or by reversing :attr:`.data_view`."""
        if self.data_url:
            return self.data_url
        return reverse_lazy(self.data_view)

    def build_attrs(self, extra_attrs=None, **kwargs):
        """Set select2's ajax attributes."""
        attrs = super(HeavySelect2Mixin, self).build_attrs(extra_attrs=extra_attrs, **kwargs)

        # encrypt instance Id
        self.widget_id = signing.dumps(id(self))

        attrs['data-field_id'] = self.widget_id
        attrs.setdefault('data-ajax--url', self.get_url())
        attrs.setdefault('data-ajax--cache', "true")
        attrs.setdefault('data-ajax--type', "GET")
        attrs.setdefault('data-minimum-input-length', 2)

        attrs['class'] += ' django-select2-heavy'
        return attrs

    def render(self, name, value, attrs=None, choices=()):
        """Render widget and register it in Django's cache."""
        output = super(HeavySelect2Mixin, self).render(name, value, attrs=attrs, choices=choices)
        self.set_to_cache()
        return output

    def _get_cache_key(self):
        return "%s%s" % (settings.SELECT2_CACHE_PREFIX, id(self))

    def set_to_cache(self):
        """Add widget object to Djnago's cache."""
        cache.set(self._get_cache_key(), self)

    def render_options(self, choices, selected_choices):
        """Render only selected options."""
        output = ['<option></option>' if not self.is_required else '']
        choices = {(k, v) for k, v in choices if k in selected_choices}
        selected_choices = {force_text(v) for v in selected_choices}
        for option_value, option_label in choices:
            output.append(self.render_option(selected_choices, option_value, option_label))
        return '\n'.join(output)


class HeavySelect2Widget(HeavySelect2Mixin, forms.Select):

    """
    Select2 widget with AJAX support that registers itself to Django's Cache.

    Usage example::

        class MyWidget(HeavySelectWidget):
            data_view = 'my_view_name'

    or::

        class MyForm(forms.Form):
            my_field = forms.ChoicesField(
                widget=HeavySelectWidget(
                    data_url='/url/to/json/response'
                )
            )

    """

    pass


class HeavySelect2MultipleWidget(HeavySelect2Mixin, forms.SelectMultiple):

    """Select2 multi select widget similar to :class:`.HeavySelect2Widget`."""

    pass


class HeavySelect2TagWidget(HeavySelect2MultipleWidget):

    """Mixin to add select2 tag functionality."""

    def build_attrs(self, extra_attrs=None, **kwargs):
        """Add select2's tag attributes."""
        attrs = super(HeavySelect2TagWidget, self).build_attrs(extra_attrs, **kwargs)
        attrs['data-minimum-input-length'] = 1
        attrs['data-tags'] = 'true'
        attrs['data-token-separators'] = [",", " "]
        return attrs


# Auto Heavy widgets


class ModelSelect2Mixin(object):

    """Widget mixin that provides attributes and methods for :class:`.AutoResponseView`."""

    model = None
    queryset = None
    search_fields = []
    """
    Model lookups that are used to filter the queryset.

    Example::

        search_fields = [
                'title__icontains',
            ]

    """

    max_results = 25
    """Maximal results returned by :class:`.AutoResponseView`."""

    def __init__(self, *args, **kwargs):
        """
        Overwrite class parameters if passed as keyword arguments.

        :param model: model to select choices from
        :type model: django.db.models.Model
        :param queryset: queryset to select choices from
        :type queryset: django.db.models.query.QuerySet
        :param search_fields: list of model lookup strings
        :type search_fields: list
        :param max_results: max. JsonResponse view page size
        :type max_results: int
        """
        self.model = kwargs.pop('model', self.model)
        self.queryset = kwargs.pop('queryset', self.queryset)
        self.search_fields = kwargs.pop('search_fields', self.search_fields)
        self.max_results = kwargs.pop('max_results', self.max_results)
        defaults = {'data_view': 'django_select2-json'}
        defaults.update(kwargs)
        super(ModelSelect2Mixin, self).__init__(*args, **defaults)

    def filter_queryset(self, term):
        """
        Return queryset filtered by search_fields matching the passed term.

        :param term: Search term
        :type term: str
        :return: Filtered queryset
        :rtype: :class:`.django.db.models.QuerySet`
        """
        qs = self.get_queryset()
        search_fields = self.get_search_fields()
        select = reduce(lambda x, y: x | Q(**{y: term}), search_fields,
                        Q(**{search_fields.pop(): term}))
        return qs.filter(select).distinct()

    def get_queryset(self):
        """
        Return queryset based on :attr:`.queryset` or :attr:`.model`.

        :return: queryset of available choices
        :rtype: :class:`.django.db.models.QuerySet`
        """
        if self.queryset is not None:
            queryset = self.queryset
        elif self.model is not None:
            queryset = self.model._default_manager.all()
        else:
            raise NotImplementedError(
                "%(cls)s is missing a QuerySet. Define "
                "%(cls)s.model, %(cls)s.queryset, or override "
                "%(cls)s.get_queryset()." % {
                    'cls': self.__class__.__name__
                }
            )
        return queryset

    def get_search_fields(self):
        """Return list of lookup names."""
        if self.search_fields:
            return self.search_fields
        raise NotImplementedError('%s, must implement "search_fields".' % self.__class__.__name__)

    def render_options(self, choices, selected_choices):
        """Render only selected options and set queryset from :class:`ModelChoicesIterator`."""
        output = ['<option></option>' if not self.is_required else '']
        if isinstance(self.choices, ModelChoiceIterator):
            if not self.queryset:
                self.queryset = self.choices.queryset
            selected_choices = {c for c in selected_choices
                                if c not in self.choices.field.empty_values}
            choices = {self.choices.choice(obj)
                       for obj in self.choices.queryset.filter(pk__in=selected_choices)}
        else:
            choices = {(k, v) for k, v in choices if k in selected_choices}
        selected_choices = {force_text(v) for v in selected_choices}
        for option_value, option_label in choices:
            output.append(self.render_option(selected_choices, option_value, option_label))
        return '\n'.join(output)


class ModelSelect2Widget(ModelSelect2Mixin, HeavySelect2Widget):

    """
    Select2 drop in model select widget.

    Example usage::

        class MyWidget(ModelSelect2Widget):
            search_fields = [
                'title__icontians',
            ]

        class MyModelForm(forms.ModelForm):
            class Meta:
                model = MyModel
                fields = ('my_field', )
                widgets = {
                    'my_field': MyWidget,
                }

    or::

        class MyForm(forms.Form):
            my_choice = forms.ChoiceField(
                widget=ModelSelect2Widget(
                    model=MyOtherModel,
                    search_fields=['title__icontains']
                )
            )

    .. tip:: The ModelSelect2(Multiple)Widget will try
        to get the queryset from the fields choices.
        Therefore you don't need to define a queryset,
        if you just drop in the widget for a ForeignKey field.
    """

    pass


class ModelSelect2MultipleWidget(ModelSelect2Mixin, HeavySelect2MultipleWidget):

    """
    Select2 drop in model multiple select widget.

    Works just like :class:`.ModelSelect2Widget` but for multi select.
    """

    pass


class ModelSelect2TagWidget(ModelSelect2Mixin, HeavySelect2TagWidget):

    """
    Select2 model field with tag support.

    This it not a simple drop in widget.
    It requires to implement you own :func:`.value_from_datadict`
    that adds missing tags to you queryset.

    Example::

        class MyModelSelect2TagWidget(ModelSelect2TagWidget):
            queryset = MyModel.objects.all()

            def value_from_datadict(self, data, files, name):
                values = super().value_from_datadict(self, data, files, name):
                qs = self.queryset.filter(**{'pk__in': list(values)})
                pks = set(force_text(getattr(o, pk)) for o in qs)
                cleaned_values = []
                for val in value:
                    if force_text(val) not in pks:
                        val = queryset.create(title=val).pk
                    cleaned_values.append(val)
                return cleaned_values

    """

    pass
