# -*- coding: utf-8 -*-
"""Contains all the Django widgets for Select2."""
from __future__ import absolute_import, unicode_literals

import logging
from functools import reduce

from django import forms
from django.core import signing
from django.core.urlresolvers import reverse_lazy

from django.db.models import Q

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
        attrs = super(Select2Mixin, self).build_attrs(extra_attrs=None, **kwargs)
        attrs.setdefault('data-allowClear', 'true' if self.is_required else 'false')
        attrs.setdefault('data-closeOnSelect', 'false')
        if 'class' in attrs:
            attrs['class'] += ' django-select2'
        else:
            attrs['class'] = 'django-select2'
        return attrs

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


class HeavySelect2Mixin(object):

    """Mixin that adds select2's ajax options and registers itself on django's cache."""

    def __init__(self, **kwargs):
        self.data_view = kwargs.pop('data_view')
        self.userGetValTextFuncName = kwargs.pop('userGetValTextFuncName', 'null')
        super(HeavySelect2Mixin, self).__init__(**kwargs)

    def get_url(self):
        return reverse_lazy(self.data_view)

    def build_attrs(self, extra_attrs=None, **kwargs):
        attrs = super(HeavySelect2Mixin, self).build_attrs(extra_attrs, **kwargs)

        # encrypt instance Id
        widget_id = signing.dumps(id(self))
        # add widget object to cache
        cache.set(self._get_cache_key(), self)

        attrs['data-field_id'] = widget_id
        attrs.setdefault('data-ajax--url', self.get_url())
        attrs.setdefault('data-ajax--cache', "true")
        attrs.setdefault('data-ajax--type', "GET")
        attrs.setdefault('data-minimumInputLength', 2)
        return attrs

    def _get_cache_key(self):
        return "%s%s" % (settings.SELECT2_CACHE_PREFIX, id(self))

    def value_from_datadict(self, *args, **kwargs):
        return super(HeavySelect2Mixin, self).value_from_datadict(*args, **kwargs)

    def render_options(self, choices, selected_choices):
        selected_choices = set(force_text(v) for v in selected_choices)
        output = []
        for option_value, option_label in selected_choices:
            output.append(self.render_option(selected_choices, option_value, option_label))
        return '\n'.join(output)


class HeavySelect2Widget(HeavySelect2Mixin, forms.Select):
    pass


class HeavySelect2MultipleWidget(HeavySelect2Mixin, forms.SelectMultiple):
    pass


class HeavySelect2TagWidget(HeavySelect2MultipleWidget):
    def build_attrs(self, extra_attrs=None, **kwargs):
        attrs = super(HeavySelect2TagWidget, self).build_attrs(self, extra_attrs, **kwargs)
        attrs['data-minimumInputLength'] = 1
        attrs['data-tags'] = 'true'
        attrs['data-tokenSeparators'] = [",", " "]
        return attrs


# Auto Heavy widgets


class ModelSelect2Mixin(object):

    """Mixin for """

    model = None
    queryset = None
    search_fields = []
    max_results = 25

    def __init__(self, *args, **kwargs):
        self.model = kwargs.pop('model', self.model)
        self.queryset = kwargs.pop('queryset', self.queryset)
        self.search_fields = kwargs.pop('search_fields', self.search_fields)
        self.max_results = kwargs.pop('max_results', self.max_results)
        defaults = {'data_view': 'django_select2_central_json'}
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


class ModelSelect2Widget(ModelSelect2Mixin, HeavySelect2Widget):

    """Auto version of :py:class:`.HeavySelect2Widget`."""

    pass


class ModelSelect2MultipleWidget(ModelSelect2Mixin, HeavySelect2MultipleWidget):

    """Auto version of :py:class:`.HeavySelect2MultipleWidget`."""

    pass


class ModelSelect2TagWidget(ModelSelect2Mixin, HeavySelect2TagWidget):

    """Auto version of :py:class:`.HeavySelect2TagWidget`."""

    pass
