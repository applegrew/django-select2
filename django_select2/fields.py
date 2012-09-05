"""
Contains all the Django fields for Select2.
"""

import logging

logger = logging.getLogger(__name__)

class AutoViewFieldMixin(object):
    """
    Registers itself with AutoResponseView.

    All Auto fields must sub-class this mixin, so that they are registered.

    .. warning:: Do not forget to include ``'django_select2.urls'`` in your url conf, else,
        central view used to serve Auto fields won't be available.
    """
    def __init__(self, *args, **kwargs):
        """
        Class constructor.

        :param auto_id: The key to use while registering this field. If it is not provided then
            an auto generated key is used.

            .. tip::
                This mixin uses full class name of the field to register itself. This is
                used like key in a :py:obj:`dict` by :py:func:`.util.register_field`.

                If that key already exists then the instance is not registered again. So, eventually
                all instances of an Auto field share one instance to respond to the Ajax queries for
                its fields.

                If for some reason any instance needs to be isolated then ``auto_id`` can be used to
                provide a unique key which has never occured before.

        :type auto_id: :py:obj:`unicode`

        """
        name = kwargs.pop('auto_id', u"%s.%s" % (self.__module__, self.__class__.__name__))
        if logger.isEnabledFor(logging.INFO):
            logger.info("Registering auto field: %s", name)

        from . import util
        id_ = util.register_field(name, self)
        self.field_id = id_
        super(AutoViewFieldMixin, self).__init__(*args, **kwargs)

    def security_check(self, request, *args, **kwargs):
        """
        Returns ``False`` if security check fails.

        :param request: The Ajax request object.
        :type request: :py:class:`django.http.HttpRequest`

        :param args: The ``*args`` passed to :py:meth:`django.views.generic.base.View.dispatch`.
        :param kwargs: The ``**kwargs`` passed to :py:meth:`django.views.generic.base.View.dispatch`.

        :return: A boolean value, signalling if check passed or failed.
        :rtype: :py:obj:`bool`

        .. warning:: Sub-classes should override this. You really do not want random people making
            Http reqeusts to your server, be able to get access to sensitive information.
        """
        return True

    def get_results(self, request, term, page, context):
        "See :py:meth:`.views.Select2View.get_results`."
        raise NotImplementedError


import copy

from django import forms
from django.core import validators
from django.core.exceptions import ValidationError
from django.forms.models import ModelChoiceIterator
from django.db.models import Q
from django.utils.translation import ugettext_lazy as _
from django.utils.encoding import smart_unicode
from django.core.validators import EMPTY_VALUES

from .widgets import Select2Widget, Select2MultipleWidget,\
    HeavySelect2Widget, HeavySelect2MultipleWidget, AutoHeavySelect2Widget, \
    AutoHeavySelect2MultipleWidget
from .views import NO_ERR_RESP
from .util import extract_some_key_val

### Light general fields ###

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


### Model fields related mixins ###

class ModelResultJsonMixin(object):
    """
    Makes ``heavy_data.js`` parsable JSON response for queries on its model.

    On query it uses :py:meth:`.prepare_qs_params` to prepare query attributes
    which it then passes to ``self.queryset.filter()`` to get the results.

    It is expected that sub-classes will defined a class field variable
    ``search_fields``, which should be a list of field names to search for.
    """

    def __init__(self, *args, **kwargs):
        """
        Class constructor.

        :param queryset: This can be passed as kwarg here or defined as field variabel,
            like ``search_fields``.
        :type queryset: :py:class:`django.db.models.query.QuerySet` or None

        :param max_results: Maximum number to results to return per Ajax query.
        :type max_results: :py:obj:`int`

        :param to_field_name: Which field's value should be returned as result tuple's
            value. (Default is ``pk``, i.e. the id field of the model)
        :type to_field_name: :py:obj:`str`
        """
        if self.queryset is None and not kwargs.has_key('queryset'):
            raise ValueError('queryset is required.')

        if not self.search_fields:
            raise ValueError('search_fields is required.')

        self.max_results = getattr(self, 'max_results', None)
        self.to_field_name = getattr(self, 'to_field_name', 'pk')

        super(ModelResultJsonMixin, self).__init__(*args, **kwargs)

    def label_from_instance(self, obj):
        """
        Sub-classes should override this to generate custom label texts for values.

        :param obj: The model object.
        :type obj: :py:class:`django.model.Model`

        :return: The label string.
        :rtype: :py:obj:`unicode`
        """
        return smart_unicode(obj)

    def prepare_qs_params(self, request, search_term, search_fields):
        """
        Prepares queryset parameter to use for searching.

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
        q = None
        for field in search_fields:
            kwargs = {}
            kwargs[field] = search_term
            if q is None:
                q = Q(**kwargs)
            else:
                q = q | Q(**kwargs)
        return {'or': [q], 'and': {},}

    def get_results(self, request, term, page, context):
        """
        See :py:meth:`.views.Select2View.get_results`.

        This implementation takes care of detecting if more results are available.
        """
        qs = copy.deepcopy(self.queryset)
        params = self.prepare_qs_params(request, term, self.search_fields)

        if self.max_results:
            min_ = (page - 1) * self.max_results
            max_ = min_ + self.max_results + 1 # fetching one extra row to check if it has more rows.
            res = list(qs.filter(*params['or'], **params['and'])[min_:max_])
            has_more = len(res) == (max_ - min_)
            if has_more:
                res = res[:-1]
        else:
            res = list(qs.filter(*params['or'], **params['and']))
            has_more = False

        res = [ (getattr(obj, self.to_field_name), self.label_from_instance(obj), ) for obj in res ]
        return (NO_ERR_RESP, has_more, res, )


class UnhideableQuerysetType(type):
    """
    This does some pretty nasty hacky stuff, to make sure users can
    also define ``queryset`` as class-level field variable, instead of
    passing it to constructor.
    """

    # TODO check for alternatives. Maybe this hack is not necessary.

    def __new__(cls, name, bases, dct):
        _q = dct.get('queryset', None)
        if _q is not None and not isinstance(_q, property):
            # This hack is needed since users are allowed to
            # provide queryset in sub-classes by declaring
            # class variable named - queryset, which will
            # effectively hide the queryset declared in this
            # mixin.
            dct.pop('queryset') # Throwing away the sub-class queryset
            dct['_subclass_queryset'] = _q

        return type.__new__(cls, name, bases, dct)

    def __call__(cls, *args, **kwargs):
        queryset = kwargs.get('queryset', None)
        if not queryset and hasattr(cls, '_subclass_queryset'):
            kwargs['queryset'] = getattr(cls, '_subclass_queryset')
        return type.__call__(cls, *args, **kwargs)


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
        result._choices = copy.deepcopy(self._choices, memo)
        return result


class QuerysetChoiceMixin(ChoiceMixin):
    """
    Overrides ``choices``' getter to return instance of :py:class:`.ModelChoiceIterator`
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
        return ModelChoiceIterator(self)

    choices = property(_get_choices, ChoiceMixin._set_choices)


class ModelChoiceFieldMixin(object):

    def __init__(self, *args, **kwargs):
        queryset = kwargs.pop('queryset', None)
        kargs = extract_some_key_val(kwargs, [
            'empty_label', 'cache_choices', 'required', 'label', 'initial', 'help_text',
            ])
        kargs['widget'] = kwargs.pop('widget', getattr(self, 'widget', None))
        kargs['to_field_name'] = kwargs.pop('to_field_name', 'pk')        

        if hasattr(self, '_choices'): # If it exists then probably it is set by HeavySelect2FieldBase.
                                      # We are not gonna use that anyway.
            del self._choices

        super(ModelChoiceFieldMixin, self).__init__(queryset, **kargs)

        if hasattr(self, 'set_placeholder'):
            self.widget.set_placeholder(self.empty_label)

    def _get_queryset(self):
        if hasattr(self, '_queryset'):
            return self._queryset


### Slightly altered versions of the Django counterparts with the same name in forms module. ###

class ModelChoiceField(ModelChoiceFieldMixin, forms.ModelChoiceField):
    queryset = property(ModelChoiceFieldMixin._get_queryset, forms.ModelChoiceField._set_queryset)


class ModelMultipleChoiceField(ModelChoiceFieldMixin, forms.ModelMultipleChoiceField):
    queryset = property(ModelChoiceFieldMixin._get_queryset, forms.ModelMultipleChoiceField._set_queryset)


### Light Fileds specialized for Models ###

class ModelSelect2Field(ModelChoiceField) :
    """
    Light Select2 field, specialized for Models.

    Select2 replacement for :py:class:`forms.ModelChoiceField`.
    """
    widget = Select2Widget


class ModelSelect2MultipleField(ModelMultipleChoiceField) :
    """
    Light multiple-value Select2 field, specialized for Models.

    Select2 replacement for :py:class:`forms.ModelMultipleChoiceField`.
    """
    widget = Select2MultipleWidget


### Heavy fields ###

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

        kargs = {}
        if data_view is not None:
            kargs['widget'] = self.widget(data_view=data_view)
        elif kwargs.get('widget', None) is None:
            raise ValueError('data_view is required else you need to provide your own widget instance.')

        kargs.update(kwargs)
        super(HeavySelect2FieldBaseMixin, self).__init__(*args, **kargs)

        # By this time self.widget would have been instantiated.

        # This piece of code is needed here since (God knows why) Django's Field class does not call
        # super(); because of that __init__() of classes would get called after Field.__init__().
        # If did had super() call there then we could have simply moved AutoViewFieldMixin at the
        # end of the MRO list. This way it would have got widget instance instead of class and it
        # could have directly set field_id on it.
        if hasattr(self, 'field_id'):
            self.widget.field_id = self.field_id

        if not choices and hasattr(self, 'choices'): # ModelChoiceField will set this to ModelChoiceIterator
            choices = self.choices
        self.choices = choices


class HeavyChoiceField(ChoiceMixin, forms.Field):
    """
    Reimplements :py:class:`django.forms.TypedChoiceField` in a way which suites the use of big data.

    .. note:: Although this field accepts ``choices`` parameter like all Django choice fields, but these
        fields are backed by big data sources, so ``choices`` cannot possibly have all the values. It is meant
        to be a subset of all possible choices.
    """
    default_error_messages = {
        'invalid_choice': _(u'Select a valid choice. %(value)s is not one of the available choices.'),
    }
    empty_value = u''
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
        uvalue = smart_unicode(value)
        for k, v in self.choices:
            if uvalue == smart_unicode(k):
                return True
        return self.validate_value(value)

    def coerce_value(self, value):
        """
        Coerces ``value`` to a Python data type.

        Sub-classes should override this if they do not want unicode values.
        """
        return smart_unicode(value)

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
        except Exception, e:
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
        'invalid_choice': _(u'Select a valid choice. %(value)s is not one of the available choices.'),
        'invalid_list': _(u'Enter a list of values.'),
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
    "Heavy Select2 Choice field."
    widget = HeavySelect2Widget


class HeavySelect2MultipleChoiceField(HeavySelect2FieldBaseMixin, HeavyMultipleChoiceField):
    "Heavy Select2 Multiple Choice field."
    widget = HeavySelect2MultipleWidget


### Heavy field specialized for Models ###

class HeavyModelSelect2ChoiceField(HeavySelect2FieldBaseMixin, ModelChoiceField):
    "Heavy Select2 Choice field, specialized for Models."
    widget = HeavySelect2Widget

    def __init__(self, *args, **kwargs):
        kwargs.pop('choices', None)
        super(HeavyModelSelect2ChoiceField, self).__init__(*args, **kwargs)


class HeavyModelSelect2MultipleChoiceField(HeavySelect2FieldBaseMixin, ModelMultipleChoiceField):
    "Heavy Select2 Multiple Choice field, specialized for Models."
    widget = HeavySelect2MultipleWidget

    def __init__(self, *args, **kwargs):
        kwargs.pop('choices', None)
        super(HeavyModelSelect2MultipleChoiceField, self).__init__(*args, **kwargs)


### Heavy general field that uses central AutoView ###

class AutoSelect2Field(AutoViewFieldMixin, HeavySelect2ChoiceField):
    """
    Auto Heavy Select2 field.

    This needs to be subclassed. The first instance of a class (sub-class) is used to serve all incoming
    json query requests for that type (class).

    .. warning:: :py:exc:`NotImplementedError` would be thrown if :py:meth:`get_results` is not implemented.
    """

    widget = AutoHeavySelect2Widget

    def __init__(self, *args, **kwargs):
        self.data_view = "django_select2_central_json"
        kwargs['data_view'] = self.data_view
        super(AutoSelect2Field, self).__init__(*args, **kwargs)


class AutoSelect2MultipleField(AutoViewFieldMixin, HeavySelect2MultipleChoiceField):
    """
    Auto Heavy Select2 field for multiple choices.

    This needs to be subclassed. The first instance of a class (sub-class) is used to serve all incoming
    json query requests for that type (class).

    .. warning:: :py:exc:`NotImplementedError` would be thrown if :py:meth:`get_results` is not implemented.
    """

    widget = AutoHeavySelect2MultipleWidget

    def __init__(self, *args, **kwargs):
        self.data_view = "django_select2_central_json"
        kwargs['data_view'] = self.data_view
        super(AutoSelect2MultipleField, self).__init__(*args, **kwargs)


### Heavy field, specialized for Model, that uses central AutoView ###

class AutoModelSelect2Field(ModelResultJsonMixin, AutoViewFieldMixin, HeavyModelSelect2ChoiceField):
    """
    Auto Heavy Select2 field, specialized for Models.

    This needs to be subclassed. The first instance of a class (sub-class) is used to serve all incoming
    json query requests for that type (class).
    """
    __metaclass__ = UnhideableQuerysetType # Makes sure that user defined queryset class variable is replaced by
                                           # queryset property (as it is needed by super classes).

    widget = AutoHeavySelect2Widget

    def __init__(self, *args, **kwargs):
        self.data_view = "django_select2_central_json"
        kwargs['data_view'] = self.data_view
        super(AutoModelSelect2Field, self).__init__(*args, **kwargs)


class AutoModelSelect2MultipleField(ModelResultJsonMixin, AutoViewFieldMixin, HeavyModelSelect2MultipleChoiceField):
    """
    Auto Heavy Select2 field for multiple choices, specialized for Models.

    This needs to be subclassed. The first instance of a class (sub-class) is used to serve all incoming
    json query requests for that type (class).
    """
    __metaclass__ = UnhideableQuerysetType # Makes sure that user defined queryset class variable is replaced by
                                           # queryset property (as it is needed by super classes).

    widget = AutoHeavySelect2MultipleWidget

    def __init__(self, *args, **kwargs):
        self.data_view = "django_select2_central_json"
        kwargs['data_view'] = self.data_view
        super(AutoModelSelect2MultipleField, self).__init__(*args, **kwargs)


