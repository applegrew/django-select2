import logging

logger = logging.getLogger(__name__)

class AutoViewFieldMixin(object):
    """Registers itself with AutoResponseView."""
    def __init__(self, *args, **kwargs):
        name = kwargs.pop('auto_id', u"%s.%s" % (self.__module__, self.__class__.__name__))
        if logger.isEnabledFor(logging.INFO):
            logger.info("Registering auto field: %s", name)

        from . import util
        id_ = util.register_field(name, self)
        self.field_id = id_
        super(AutoViewFieldMixin, self).__init__(*args, **kwargs)

    def security_check(self, request, *args, **kwargs):
        return True

    def get_results(self, request, term, page, context):
        raise NotImplementedError

import copy

from django import forms
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
    widget = Select2Widget

class Select2MultipleChoiceField(forms.MultipleChoiceField):
    widget = Select2MultipleWidget

### Model fields related mixins ###

class ModelResultJsonMixin(object):

    def __init__(self, *args, **kwargs):
        if self.queryset is None and not kwargs.has_key('queryset'):
            raise ValueError('queryset is required.')

        if not self.search_fields:
            raise ValueError('search_fields is required.')

        self.max_results = getattr(self, 'max_results', None)
        self.to_field_name = getattr(self, 'to_field_name', 'pk')

        super(ModelResultJsonMixin, self).__init__(*args, **kwargs)

    def label_from_instance(self, obj):
        return smart_unicode(obj)

    def prepare_qs_params(self, request, search_term, search_fields):        
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
    def _get_choices(self):
        if hasattr(self, '_choices'):
            return self._choices

    def _set_choices(self, value):
        # Setting choices also sets the choices on the widget.
        # choices can be any iterable, but we call list() on it because
        # it will be consumed more than once.
        self._choices = self.widget.choices = list(value)

    choices = property(_get_choices, _set_choices)

class QuerysetChoiceMixin(ChoiceMixin):
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
    "Light Model Select2 field"
    widget = Select2Widget

class ModelSelect2MultipleField(ModelMultipleChoiceField) :
    "Light multiple-value Model Select2 field"
    widget = Select2MultipleWidget

### Heavy fields ###

class HeavySelect2FieldBase(ChoiceMixin, forms.Field):
    def __init__(self, *args, **kwargs):
        data_view = kwargs.pop('data_view', None)
        self.choices = kwargs.pop('choices', [])

        kargs = {}
        if data_view is not None:
            kargs['widget'] = self.widget(data_view=data_view)
        elif kwargs.get('widget', None) is None:
            raise ValueError('data_view is required else you need to provide your own widget instance.')

        kargs.update(kwargs)
        super(HeavySelect2FieldBase, self).__init__(*args, **kargs)
        # This piece of code is needed here since (God knows) why Django's Field class does not call
        # super(); because of that __init__() of classes would get called after Field.__init__().
        # If did had super() call there then we could have simply moved AutoViewFieldMixin at the
        # end of the MRO list. This way it would have got widget instance instead of class and it
        # could have directly set field_id on it.
        if hasattr(self, 'field_id'):
            self.widget.field_id = self.field_id

class HeavySelect2ChoiceField(HeavySelect2FieldBase):
    widget = HeavySelect2Widget

class HeavySelect2MultipleChoiceField(HeavySelect2FieldBase):
    widget = HeavySelect2MultipleWidget

### Heavy field specialized for Models ###

class HeavyModelSelect2ChoiceField(QuerysetChoiceMixin, HeavySelect2ChoiceField, ModelChoiceField):
    def __init__(self, *args, **kwargs):
        kwargs.pop('choices', None)
        super(HeavyModelSelect2ChoiceField, self).__init__(*args, **kwargs)

class HeavyModelSelect2MultipleChoiceField(QuerysetChoiceMixin, HeavySelect2MultipleChoiceField, ModelMultipleChoiceField):
    def __init__(self, *args, **kwargs):
        kwargs.pop('choices', None)
        super(HeavyModelSelect2MultipleChoiceField, self).__init__(*args, **kwargs)

### Heavy general field that uses central AutoView ###

class AutoSelect2Field(AutoViewFieldMixin, HeavySelect2ChoiceField):
    """
    This needs to be subclassed. The first instance of a class (sub-class) is used to serve all incoming
    json query requests for that type (class).
    """

    widget = AutoHeavySelect2Widget

    def __init__(self, *args, **kwargs):
        self.data_view = "django_select2_central_json"
        kwargs['data_view'] = self.data_view
        super(AutoSelect2Field, self).__init__(*args, **kwargs)

class AutoSelect2MultipleField(AutoViewFieldMixin, HeavySelect2MultipleChoiceField):
    """
    This needs to be subclassed. The first instance of a class (sub-class) is used to serve all incoming
    json query requests for that type (class).
    """

    widget = AutoHeavySelect2MultipleWidget

    def __init__(self, *args, **kwargs):
        self.data_view = "django_select2_central_json"
        kwargs['data_view'] = self.data_view
        super(AutoSelect2MultipleField, self).__init__(*args, **kwargs)

### Heavy field, specialized for Model, that uses central AutoView ###

class AutoModelSelect2Field(ModelResultJsonMixin, AutoViewFieldMixin, HeavyModelSelect2ChoiceField):
    """
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


