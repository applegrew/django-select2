# -*- coding: utf-8 -*-
"""
Contains all the Django fields for Select2.
"""
from __future__ import absolute_import, unicode_literals

import copy
import logging
import warnings
from functools import reduce

from django import forms
from django.core import validators
from django.core.exceptions import ValidationError
from django.db.models import Q
from django.forms.models import ModelChoiceIterator
from django.utils.encoding import force_text, smart_text
from django.utils.translation import ugettext_lazy as _

from .types import NO_ERR_RESP
from .util import extract_some_key_val
from .widgets import AutoHeavySelect2Mixin  # NOQA
from .widgets import (AutoHeavySelect2MultipleWidget,
                      AutoHeavySelect2TagWidget, AutoHeavySelect2Widget,
                      HeavySelect2MultipleWidget, HeavySelect2TagWidget,
                      HeavySelect2Widget, Select2MultipleWidget, Select2Widget)

logger = logging.getLogger(__name__)


class AutoViewFieldMixin(object):
    """
    Registers itself with AutoResponseView.

    All Auto fields must sub-class this mixin, so that they are registered.

    .. warning:: Do not forget to include ``'django_select2.urls'`` in your url conf, else,
        central view used to serve Auto fields won't be available.
    """

    def __init__(self, *args, **kwargs):
        kwargs.pop('auto_id', None)
        super(AutoViewFieldMixin, self).__init__(*args, **kwargs)

    def get_results(self, *args, **kwargs):
        raise NotImplementedError


# ## Light general fields ##


class Select2ChoiceField(forms.ChoiceField):
    """
    Drop-in Select2 replacement for :py:class:`forms.ChoiceField`.
    """
    widget = Select2Widget


class Select2MultipleChoiceField(forms.MultipleChoiceField):
    """
    Drop-in Select2 replacement for :py:class:`forms.MultipleChoiceField`.
    """
    widget = Select2MultipleWidget


# ## Model fields related mixins ##


class ModelResultJsonMixin(object):
    """
    Makes ``heavy_data.js`` parsable JSON response for queries on its model.

    On query it uses :py:meth:`.prepare_qs_params` to prepare query attributes
    which it then passes to ``self.queryset.filter()`` to get the results.

    It is expected that sub-classes will defined a class field variable
    ``search_fields``, which should be a list of field names to search for.

    .. note:: As of version 3.1.3, ``search_fields`` is optional if sub-class
        overrides ``get_results``.
    """

    max_results = 25
    to_field_name = 'pk'
    queryset = {}
    search_fields = ()

    def __init__(self, *args, **kwargs):
        self.search_fields = kwargs.pop('search_fields', self.search_fields)
        super(ModelResultJsonMixin, self).__init__(*args, **kwargs)

    def get_search_fields(self):
        if self.search_fields:
            return self.search_fields
        raise NotImplementedError('%s must implement "search_fields".' % self.__class__.__name__)

    def get_queryset(self):
        """
        Return the list of model choices.

        The return value must be an iterable and may be an instance of
        `QuerySet` in which case `QuerySet` specific behavior will be enabled.
        """
        if self.queryset:
            return self.queryset
        raise NotImplementedError('%s must implement "queryset".' % self.__class__.__name__)

    def label_from_instance(self, obj):
        """
        Sub-classes should override this to generate custom label texts for values.

        :param obj: The model object.
        :type obj: :py:class:`django.model.Model`

        :return: The label string.
        :rtype: :py:obj:`unicode`
        """
        warnings.warn(
            '"label_from_instance" is deprecated and will be removed in version 5.',
            DeprecationWarning
        )
        return smart_text(obj)

    def extra_data_from_instance(self, obj):
        """
        Sub-classes should override this to generate extra data for values. These are passed to
        JavaScript and can be used for custom rendering.

        :param obj: The model object.
        :type obj: :py:class:`django.model.Model`

        :return: The extra data dictionary.
        :rtype: :py:obj:`dict`
        """
        return {}

    def prepare_qs_params(self, request, search_term, search_fields):
        """
        Prepare queryset parameter to use for searching.

        :param search_term: The search term.
        :type search_term: :py:obj:`str`

        :param search_fields: The list of search fields. This is same as ``self.search_fields``.
        :type search_term: :py:obj:`list`

        :return: A dictionary of parameters to 'or' and 'and' together. The output format should
            be ::

                {
                    'or': [
                    Q(attr11=term11) | Q(attr12=term12) | ...,
                    Q(attrN1=termN1) | Q(attrN2=termN2) | ...,
                    ...],

                    'and': {
                        'attrX1': termX1,
                        'attrX2': termX2,
                        ...
                    }
                }

            The above would then be coaxed into ``filter()`` as below::

                queryset.filter(
                    Q(attr11=term11) | Q(attr12=term12) | ...,
                    Q(attrN1=termN1) | Q(attrN2=termN2) | ...,
                    ...,
                    attrX1=termX1,
                    attrX2=termX2,
                    ...
                    )

            In this implementation, ``term11, term12, termN1, ...`` etc., all are actually ``search_term``.
            Also then ``and`` part is always empty.

            So, let's take an example.

            | Assume, ``search_term == 'John'``
            | ``self.search_fields == ['first_name__icontains', 'last_name__icontains']``

            So, the prepared query would be::

                {
                    'or': [
                        Q(first_name__icontains=search_term) | Q(last_name__icontains=search_term)
                    ],
                    'and': {}
                }
        :rtype: :py:obj:`dict`
        """
        q = reduce(lambda x, y: y | Q({x: search_term}), search_fields)
        return {'or': [q], 'and': {}}

    def filter_queryset(self, request, term):
        """
        See :py:meth:`.views.Select2View.get_results`.

        This implementation takes care of detecting if more results are available.
        """
        qs = self.get_queryset()
        params = self.prepare_qs_params(request, term, self.search_fields)

        return qs.filter(*params['or'], **params['and']).distinct()

    def get_results(self, request, term, page, context):
        warnings.warn(
            '"get_results" is deprecated and will be removed in version 5.',
            DeprecationWarning
        )
        self.widget.queryset = self.get_queryset()
        self.widget.search_fields = self.get_search_fields()
        qs = self.widget.filter_queryset(term)

        if self.max_results:
            min_ = (page - 1) * self.max_results
            max_ = min_ + self.max_results + 1  # fetching one extra row to check if it has more rows.
            res = qs[min_:max_]
            has_more = len(res) == (max_ - min_)
            if has_more:
                res = list(res)[:-1]
        else:
            res = qs
            has_more = False

        res = [
            (
                getattr(obj, self.to_field_name),
                self.label_from_instance(obj),
                self.extra_data_from_instance(obj)
            )
            for obj in res
        ]
        return NO_ERR_RESP, has_more, res


class ChoiceMixin(object):
    """
    Simple mixin which provides a property -- ``choices``. When ``choices`` is set,
    then it sets that value to ``self.widget.choices`` too.
    """

    def _get_choices(self):
        if hasattr(self, '_choices'):
            return self._choices
        return []

    def _set_choices(self, value):
        # Setting choices also sets the choices on the widget.
        # choices can be any iterable, but we call list() on it because
        # it will be consumed more than once.
        self._choices = self.widget.choices = list(value)

    choices = property(_get_choices, _set_choices)

    def __deepcopy__(self, memo):
        result = super(ChoiceMixin, self).__deepcopy__(memo)
        if hasattr(self, '_choices'):
            result._choices = copy.deepcopy(self._choices, memo)
        return result


class FilterableModelChoiceIterator(ModelChoiceIterator):
    """
    Extends ModelChoiceIterator to add the capability to apply additional
    filter on the passed queryset.
    """

    def set_extra_filter(self, **filter_map):
        """
        Applies additional filter on the queryset. This can be called multiple times.

        :param filter_map: The ``**kwargs`` to pass to :py:meth:`django.db.models.query.QuerySet.filter`.
            If this is not set then additional filter (if) applied before is removed.
        """
        if not hasattr(self, '_original_queryset'):
            import copy

            self._original_queryset = copy.deepcopy(self.queryset)
        if filter_map:
            self.queryset = self._original_queryset.filter(**filter_map)
        else:
            self.queryset = self._original_queryset


class QuerysetChoiceMixin(ChoiceMixin):
    """
    Overrides ``choices``' getter to return instance of :py:class:`.FilterableModelChoiceIterator`
    instead.
    """

    def _get_choices(self):
        # If self._choices is set, then somebody must have manually set
        # the property self.choices. In this case, just return self._choices.
        if hasattr(self, '_choices'):
            return self._choices

        # Otherwise, execute the QuerySet in self.queryset to determine the
        # choices dynamically. Return a fresh ModelChoiceIterator that has not been
        # consumed. Note that we're instantiating a new ModelChoiceIterator *each*
        # time _get_choices() is called (and, thus, each time self.choices is
        # accessed) so that we can ensure the QuerySet has not been consumed. This
        # construct might look complicated but it allows for lazy evaluation of
        # the queryset.
        return FilterableModelChoiceIterator(self)

    choices = property(_get_choices, ChoiceMixin._set_choices)

    def __deepcopy__(self, memo):
        result = super(QuerysetChoiceMixin, self).__deepcopy__(memo)
        # Need to force a new ModelChoiceIterator to be created, bug #11183
        result.queryset = result.queryset
        return result


class ModelChoiceFieldMixin(QuerysetChoiceMixin):
    def __init__(self, queryset=None, **kwargs):
        # This filters out kwargs not supported by Field but are still passed as it is required
        # by other codes. If new args are added to Field then make sure they are added here too.
        kargs = extract_some_key_val(kwargs, [
            'empty_label', 'cache_choices', 'required', 'label', 'initial', 'help_text',
            'validators', 'localize',
        ])
        kargs['widget'] = kwargs.pop('widget', getattr(self, 'widget', None))
        kargs['to_field_name'] = kwargs.pop('to_field_name', 'pk')

        queryset = queryset or self.get_queryset()

        # If it exists then probably it is set by HeavySelect2FieldBase.
        # We are not gonna use that anyway.
        if hasattr(self, '_choices'):
            del self._choices
        super(ModelChoiceFieldMixin, self).__init__(queryset, **kargs)

        if hasattr(self, 'set_placeholder'):
            self.widget.set_placeholder(self.empty_label)

    def get_pk_field_name(self):
        return self.to_field_name


# ## Slightly altered versions of the Django counterparts with the same name in forms module. ##


class ModelChoiceField(ModelChoiceFieldMixin, forms.ModelChoiceField):

    def get_queryset(self):
        if self.queryset:
            return self.queryset
        elif self.model:
            return self.model._default_queryset
        raise NotImplementedError('%s must implement "model" or "queryset".' % self.__class__.__name__)


class ModelMultipleChoiceField(ModelChoiceFieldMixin, forms.ModelMultipleChoiceField):
    pass


# ## Light Fields specialized for Models ##


class ModelSelect2Field(ModelChoiceField):
    """
    Light Select2 field, specialized for Models.

    Select2 replacement for :py:class:`forms.ModelChoiceField`.
    """
    widget = Select2Widget


class ModelSelect2MultipleField(ModelMultipleChoiceField):
    """
    Light multiple-value Select2 field, specialized for Models.

    Select2 replacement for :py:class:`forms.ModelMultipleChoiceField`.
    """
    widget = Select2MultipleWidget


# ## Heavy fields ##


class HeavySelect2FieldBaseMixin(object):
    """
    Base mixin field for all Heavy fields.

    .. note:: Although Heavy fields accept ``choices`` parameter like all Django choice fields, but these
        fields are backed by big data sources, so ``choices`` cannot possibly have all the values.

        For Heavies, consider ``choices`` to be a subset of all possible choices. It is available because users
        might expect it to be available.

    """

    def __init__(self, *args, **kwargs):
        """
        Class constructor.

        :param data_view: A :py:class:`~.views.Select2View` sub-class which can respond to this widget's Ajax queries.
        :type data_view: :py:class:`django.views.generic.base.View` or None

        :param widget: A widget instance.
        :type widget: :py:class:`django.forms.widgets.Widget` or None

        .. warning:: Either of ``data_view`` or ``widget`` must be specified, else :py:exc:`ValueError` would
            be raised.

        """
        data_view = kwargs.pop('data_view', None)
        choices = kwargs.pop('choices', [])

        widget = kwargs.pop('widget', None)
        widget = widget or self.widget
        if isinstance(widget, type):
                self.widget = widget(data_view=data_view)
        else:
            self.widget.data_view = data_view

        super(HeavySelect2FieldBaseMixin, self).__init__(*args, **kwargs)

        # Widget should have been instantiated by now.
        self.widget.field = self

        # ModelChoiceField will set self.choices to ModelChoiceIterator
        if choices and not (hasattr(self, 'choices') and isinstance(self.choices, forms.models.ModelChoiceIterator)):
            self.choices = choices


class HeavyChoiceField(ChoiceMixin, forms.Field):
    """
    Reimplements :py:class:`django.forms.TypedChoiceField` in a way which suites the use of big data.

    .. note:: Although this field accepts ``choices`` parameter like all Django choice fields, but these
        fields are backed by big data sources, so ``choices`` cannot possibly have all the values. It is meant
        to be a subset of all possible choices.
    """
    default_error_messages = {
        'invalid_choice': _('Select a valid choice. %(value)s is not one of the available choices.'),
    }
    empty_value = ''
    "Sub-classes can set this other value if needed."

    def __init__(self, *args, **kwargs):
        super(HeavyChoiceField, self).__init__(*args, **kwargs)
        # Widget should have been instantiated by now.
        self.widget.field = self

    def to_python(self, value):
        if value == self.empty_value or value in validators.EMPTY_VALUES:
            return self.empty_value
        try:
            value = self.coerce_value(value)
        except (ValueError, TypeError, ValidationError):
            raise ValidationError(self.error_messages['invalid_choice'] % {'value': value})
        return value

    def validate(self, value):
        super(HeavyChoiceField, self).validate(value)
        if value and not self.valid_value(value):
            raise ValidationError(self.error_messages['invalid_choice'] % {'value': value})

    def valid_value(self, value):
        uvalue = smart_text(value)
        for k, v in self.choices:
            if uvalue == smart_text(k):
                return True
        return self.validate_value(value)

    def coerce_value(self, value):
        """
        Coerces ``value`` to a Python data type.

        Sub-classes should override this if they do not want Unicode values.
        """
        return smart_text(value)

    def validate_value(self, value):
        """
        Sub-classes can override this to validate the value entered against the big data.

        :param value: Value entered by the user.
        :type value: As coerced by :py:meth:`.coerce_value`.

        :return: ``True`` means the ``value`` is valid.
        """
        return True

    def _get_val_txt(self, value):
        try:
            value = self.coerce_value(value)
            self.validate_value(value)
        except Exception:
            logger.exception("Exception while trying to get label for value")
            return None
        return self.get_val_txt(value)

    def get_val_txt(self, value):
        """
        If Heavy widgets encounter any value which it can't find in ``choices`` then it calls
        this method to get the label for the value.

        :param value: Value entered by the user.
        :type value: As coerced by :py:meth:`.coerce_value`.

        :return: The label for this value.
        :rtype: :py:obj:`unicode` or None (when no possible label could be found)
        """
        return None


class HeavyMultipleChoiceField(HeavyChoiceField):
    """
    Reimplements :py:class:`django.forms.TypedMultipleChoiceField` in a way which suites the use of big data.

    .. note:: Although this field accepts ``choices`` parameter like all Django choice fields, but these
        fields are backed by big data sources, so ``choices`` cannot possibly have all the values. It is meant
        to be a subset of all possible choices.
    """
    hidden_widget = forms.MultipleHiddenInput
    default_error_messages = {
        'invalid_choice': _('Select a valid choice. %(value)s is not one of the available choices.'),
        'invalid_list': _('Enter a list of values.'),
    }

    def to_python(self, value):
        if not value:
            return []
        elif not isinstance(value, (list, tuple)):
            raise ValidationError(self.error_messages['invalid_list'])
        return [self.coerce_value(val) for val in value]

    def validate(self, value):
        if self.required and not value:
            raise ValidationError(self.error_messages['required'])
        # Validate that each value in the value list is in self.choices or
        # the big data (i.e. validate_value() returns True).
        for val in value:
            if not self.valid_value(val):
                raise ValidationError(self.error_messages['invalid_choice'] % {'value': val})


class HeavySelect2ChoiceField(HeavySelect2FieldBaseMixin, HeavyChoiceField):
    """Heavy Select2 Choice field."""
    widget = HeavySelect2Widget


class HeavySelect2MultipleChoiceField(HeavySelect2FieldBaseMixin, HeavyMultipleChoiceField):
    """Heavy Select2 Multiple Choice field."""
    widget = HeavySelect2MultipleWidget


class HeavySelect2TagField(HeavySelect2MultipleChoiceField):
    """
    Heavy Select2 field for tagging.

    .. warning:: :py:exc:`NotImplementedError` would be thrown if :py:meth:`create_new_value` is not implemented.
    """
    widget = HeavySelect2TagWidget

    def validate(self, value):
        if self.required and not value:
            raise ValidationError(self.error_messages['required'])
        # Check if each value in the value list is in self.choices or
        # the big data (i.e. validate_value() returns True).
        # If not then calls create_new_value() to create the new value.
        for i in range(0, len(value)):
            val = value[i]
            if not self.valid_value(val):
                value[i] = self.create_new_value(val)

    def create_new_value(self, value):
        """
        This is called when the input value is not valid. This
        allows you to add the value into the data-store. If that
        is not done then eventually the validation will fail.

        :param value: Invalid value entered by the user.
        :type value: As coerced by :py:meth:`HeavyChoiceField.coerce_value`.

        :return: The a new value, which could be the id (pk) of the created value.
        :rtype: Any
        """
        raise NotImplementedError


# ## Heavy field specialized for Models ##


class HeavyModelSelect2ChoiceField(HeavySelect2FieldBaseMixin, ModelChoiceField):
    """Heavy Select2 Choice field, specialized for Models."""
    widget = HeavySelect2Widget

    def __init__(self, *args, **kwargs):
        kwargs.pop('choices', None)
        super(HeavyModelSelect2ChoiceField, self).__init__(*args, **kwargs)


class HeavyModelSelect2MultipleChoiceField(HeavySelect2FieldBaseMixin, ModelMultipleChoiceField):
    """Heavy Select2 Multiple Choice field, specialized for Models."""
    widget = HeavySelect2MultipleWidget

    def __init__(self, *args, **kwargs):
        kwargs.pop('choices', None)
        super(HeavyModelSelect2MultipleChoiceField, self).__init__(*args, **kwargs)


class HeavyModelSelect2TagField(HeavySelect2FieldBaseMixin, ModelMultipleChoiceField):
    """
    Heavy Select2 field for tagging, specialized for Models.

    .. warning:: :py:exc:`NotImplementedError` would be thrown if :py:meth:`get_model_field_values` is not implemented.
    """
    widget = HeavySelect2TagWidget

    def __init__(self, *args, **kwargs):
        kwargs.pop('choices', None)
        super(HeavyModelSelect2TagField, self).__init__(*args, **kwargs)

    def to_python(self, value):
        if value in self.empty_values:
            return None
        try:
            key = self.to_field_name or 'pk'
            value = self.queryset.get(**{key: value})
        except ValueError:
            raise ValidationError(self.error_messages['invalid_choice'])
        except self.queryset.model.DoesNotExist:
            value = self.create_new_value(value)
        return value

    def clean(self, value):
        if self.required and not value:
            raise ValidationError(self.error_messages['required'])
        elif not self.required and not value:
            return []
        if not isinstance(value, (list, tuple)):
            raise ValidationError(self.error_messages['list'])
        new_values = []
        key = self.to_field_name or 'pk'
        for pk in list(value):
            try:
                self.queryset.filter(**{key: pk})
            except ValueError:
                value.remove(pk)
                new_values.append(pk)

        for val in new_values:
            value.append(self.create_new_value(force_text(val)))

        # Usually new_values will have list of new tags, but if the tag is
        # suppose of type int then that could be interpreted as valid pk
        # value and ValueError above won't be triggered.
        # Below we find such tags and create them, by check if the pk
        # actually exists.
        qs = self.queryset.filter(**{'%s__in' % key: value})
        pks = set([force_text(getattr(o, key)) for o in qs])
        for i in range(0, len(value)):
            val = force_text(value[i])
            if val not in pks:
                value[i] = self.create_new_value(val)
        # Since this overrides the inherited ModelChoiceField.clean
        # we run custom validators here
        self.run_validators(value)
        return qs

    def create_new_value(self, value):
        """
        This is called when the input value is not valid. This
        allows you to add the value into the data-store. If that
        is not done then eventually the validation will fail.

        :param value: Invalid value entered by the user.
        :type value: As coerced by :py:meth:`HeavyChoiceField.coerce_value`.

        :return: The a new value, which could be the id (pk) of the created value.
        :rtype: Any
        """
        obj = self.queryset.create(**self.get_model_field_values(value))
        return getattr(obj, self.to_field_name or 'pk')

    def get_model_field_values(self, value):
        """
        This is called when the input value is not valid and the field
        tries to create a new model instance.

        :param value: Invalid value entered by the user.
        :type value: unicode

        :return: Dict with attribute name - attribute value pair.
        :rtype: dict
        """
        raise NotImplementedError


# ## Heavy general field that uses central AutoView ##


class AutoSelect2Field(AutoViewFieldMixin, HeavySelect2ChoiceField):
    """
    Auto Heavy Select2 field.

    This needs to be subclassed. The first instance of a class (sub-class) is used to serve all incoming
    json query requests for that type (class).

    .. warning:: :py:exc:`NotImplementedError` would be thrown if :py:meth:`get_results` is not implemented.
    """

    widget = AutoHeavySelect2Widget


class AutoSelect2MultipleField(AutoViewFieldMixin, HeavySelect2MultipleChoiceField):
    """
    Auto Heavy Select2 field for multiple choices.

    This needs to be subclassed. The first instance of a class (sub-class) is used to serve all incoming
    json query requests for that type (class).

    .. warning:: :py:exc:`NotImplementedError` would be thrown if :py:meth:`get_results` is not implemented.
    """

    widget = AutoHeavySelect2MultipleWidget


class AutoSelect2TagField(AutoViewFieldMixin, HeavySelect2TagField):
    """
    Auto Heavy Select2 field for tagging.

    This needs to be subclassed. The first instance of a class (sub-class) is used to serve all incoming
    json query requests for that type (class).

    .. warning:: :py:exc:`NotImplementedError` would be thrown if :py:meth:`get_results` is not implemented.
    """

    widget = AutoHeavySelect2TagWidget


# ## Heavy field, specialized for Model, that uses central AutoView ##


class AutoModelSelect2Field(ModelResultJsonMixin, AutoViewFieldMixin,
                            HeavyModelSelect2ChoiceField):
    """
    Auto Heavy Select2 field, specialized for Models.

    This needs to be subclassed. The first instance of a class (sub-class) is used to serve all incoming
    json query requests for that type (class).
    """

    widget = AutoHeavySelect2Widget


class AutoModelSelect2MultipleField(ModelResultJsonMixin, AutoViewFieldMixin,
                                    HeavyModelSelect2MultipleChoiceField):
    """
    Auto Heavy Select2 field for multiple choices, specialized for Models.

    This needs to be subclassed. The first instance of a class (sub-class) is used to serve all incoming
    json query requests for that type (class).
    """

    widget = AutoHeavySelect2MultipleWidget


class AutoModelSelect2TagField(ModelResultJsonMixin, AutoViewFieldMixin,
                               HeavyModelSelect2TagField):
    """
    Auto Heavy Select2 field for tagging, specialized for Models.

    This needs to be subclassed. The first instance of a class (sub-class) is used to serve all incoming
    json query requests for that type (class).

    .. warning:: :py:exc:`NotImplementedError` would be thrown if :py:meth:`get_model_field_values` is not implemented.

    Example::

        class Tag(models.Model):
            tag = models.CharField(max_length=10, unique=True)
            def __str__(self):
                return text_type(self.tag)

        class TagField(AutoModelSelect2TagField):
            queryset = Tag.objects
            search_fields = ['tag__icontains', ]
            def get_model_field_values(self, value):
                return {'tag': value}

    """

    widget = AutoHeavySelect2TagWidget
