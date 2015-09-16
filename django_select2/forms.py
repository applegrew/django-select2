# -*- coding: utf-8 -*-
"""Contains all the Django widgets for Select2."""
from __future__ import absolute_import, unicode_literals

import logging
from functools import reduce

from django import forms
from django.core import signing
from django.core.urlresolvers import reverse_lazy
from django.db.models import Q
from django.forms.models import ModelChoiceIterator
from django.utils.encoding import force_text

from .cache import cache
from .conf import settings

logger = logging.getLogger(__name__)


# ## Light mixin and widgets ##


class Select2Mixin(object):

    """
    The base mixin of all Select2 widgets.

    This mixin is responsible for rendering the necessary
    data attributes for select2 as well as adding the static
    form media.
    """

    def build_attrs(self, extra_attrs=None, **kwargs):
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
        output = '<option></option>' if not self.is_required else ''
        output += super(Select2Mixin, self).render_options(choices, selected_choices)
        return output

    def _get_media(self):
        """
        Construct Media as a dynamic property.

        This is essential because we need to check RENDER_SELECT2_STATICS
        before returning our assets.

        for more information:
        https://docs.djangoproject.com/en/1.8/topics/forms/media/#media-as-a-dynamic-property
        """
        return forms.Media(
            js=('//cdnjs.cloudflare.com/ajax/libs/select2/4.0.0/js/select2.min.js',
                'django_select2/django_select2.js'),
            css={'screen': ('//cdnjs.cloudflare.com/ajax/libs/select2/4.0.0/css/select2.min.css',)}
        )

    media = property(_get_media)


class Select2Widget(Select2Mixin, forms.Select):
    pass


class Select2MultipleWidget(Select2Mixin, forms.SelectMultiple):
    pass


class HeavySelect2Mixin(Select2Mixin):

    """Mixin that adds select2's ajax options and registers itself on django's cache."""

    def __init__(self, **kwargs):
        self.data_view = kwargs.pop('data_view', None)
        self.data_url = kwargs.pop('data_url', None)
        if not (self.data_view or self.data_url):
            raise ValueError('You must ether specify "data_view" or "data_url".')
        self.userGetValTextFuncName = kwargs.pop('userGetValTextFuncName', 'null')
        super(HeavySelect2Mixin, self).__init__(**kwargs)

    def get_url(self):
        if self.data_url:
            return self.data_url
        return reverse_lazy(self.data_view)

    def build_attrs(self, extra_attrs=None, **kwargs):
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
        output = super(HeavySelect2Mixin, self).render(name, value, attrs=attrs, choices=choices)
        self.set_to_cache()
        return output

    def _get_cache_key(self):
        return "%s%s" % (settings.SELECT2_CACHE_PREFIX, id(self))

    def set_to_cache(self):
        """Add widget object to Djnago's cache."""
        cache.set(self._get_cache_key(), self)

    def render_options(self, choices, selected_choices):
        output = ['<option></option>' if not self.is_required else '']
        choices = {(k, v) for k, v in choices if k in selected_choices}
        selected_choices = {force_text(v) for v in selected_choices}
        for option_value, option_label in choices:
            output.append(self.render_option(selected_choices, option_value, option_label))
        return '\n'.join(output)


class HeavySelect2Widget(HeavySelect2Mixin, forms.Select):
    pass


class HeavySelect2MultipleWidget(HeavySelect2Mixin, forms.SelectMultiple):
    pass


class HeavySelect2TagWidget(HeavySelect2MultipleWidget):
    def build_attrs(self, extra_attrs=None, **kwargs):
        attrs = super(HeavySelect2TagWidget, self).build_attrs(extra_attrs, **kwargs)
        attrs['data-minimum-input-length'] = 1
        attrs['data-tags'] = 'true'
        attrs['data-token-separators'] = [",", " "]
        return attrs


# Auto Heavy widgets


class ModelSelect2Mixin(object):
    model = None
    queryset = None
    search_fields = []
    max_results = 25

    def __init__(self, *args, **kwargs):
        self.model = kwargs.pop('model', self.model)
        self.queryset = kwargs.pop('queryset', self.queryset)
        self.search_fields = kwargs.pop('search_fields', self.search_fields)
        self.max_results = kwargs.pop('max_results', self.max_results)
        defaults = {'data_view': 'django_select2-json'}
        defaults.update(kwargs)
        super(ModelSelect2Mixin, self).__init__(*args, **defaults)

    def filter_queryset(self, term):
        qs = self.get_queryset()
        search_fields = self.get_search_fields()
        select = reduce(lambda x, y: Q(**{x: term}) | Q(**{y: term}), search_fields,
                        Q(**{search_fields.pop(): term}))
        return qs.filter(select).distinct()

    def get_queryset(self):
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
        if self.search_fields:
            return self.search_fields
        raise NotImplementedError('%s, must implement "search_fields".' % self.__class__.__name__)

    def render_options(self, choices, selected_choices):
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

    """Auto version of :py:class:`.HeavySelect2Widget`."""

    pass


class ModelSelect2MultipleWidget(ModelSelect2Mixin, HeavySelect2MultipleWidget):

    """Auto version of :py:class:`.HeavySelect2MultipleWidget`."""

    pass


class ModelSelect2TagWidget(ModelSelect2Mixin, HeavySelect2TagWidget):

    """Auto version of :py:class:`.HeavySelect2TagWidget`."""

    pass
