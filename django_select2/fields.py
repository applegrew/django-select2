class AutoViewFieldMixin(object):
    """Registers itself with AutoResponseView."""
    def __init__(self, *args, **kwargs):
        name = self.__class__.__name__
        from .util import register_field
        if name not in ['AutoViewFieldMixin', 'AutoModelSelect2Field']:
            id_ = register_field("%s.%s" % (self.__module__, name), self)
            self.widget.field_id = id_
        super(AutoViewFieldMixin, self).__init__(*args, **kwargs)

    def security_check(self, request, *args, **kwargs):
        return True

    def get_results(self, request, term, page, context):
        raise NotImplemented

import copy

from django import forms
from django.utils.translation import ugettext_lazy as _
from django.utils.encoding import smart_unicode
from django.db.models import Q
from django.core.validators import EMPTY_VALUES

from .widgets import Select2Widget, Select2MultipleWidget,\
    HeavySelect2Widget, HeavySelect2MultipleWidget, AutoHeavySelect2Widget
from .views import NO_ERR_RESP

class ModelResultJsonMixin(object):

    def __init__(self, **kwargs):
        if self.queryset is None:
            raise ValueError('queryset is required.')

        if not self.search_fields:
            raise ValueError('search_fields is required.')

        self.max_results = getattr(self, 'max_results', None)
        self.to_field_name = getattr(self, 'to_field_name', 'pk')

        super(ModelResultJsonMixin, self).__init__(**kwargs)

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

class ModelValueMixin(object):
    default_error_messages = {
        'invalid_choice': _(u'Select a valid choice. That choice is not one of'
                            u' the available choices.'),
    }

    def __init__(self, **kwargs):
        if self.queryset is None:
            raise ValueError('queryset is required.')

        self.to_field_name = getattr(self, 'to_field_name', 'pk')

        super(ModelValueMixin, self).__init__(**kwargs)

    def to_python(self, value):
        if value in EMPTY_VALUES:
            return None
        try:
            key = self.to_field_name
            value = self.queryset.get(**{key: value})
        except (ValueError, self.queryset.model.DoesNotExist):
            raise ValidationError(self.error_messages['invalid_choice'])
        return value

class Select2ChoiceField(forms.ChoiceField):
    widget = Select2Widget

class Select2MultipleChoiceField(forms.ChoiceField):
    widget = Select2MultipleWidget

class HeavySelect2FieldBase(forms.Field):
    def __init__(self, **kwargs):
        data_view = kwargs.pop('data_view', None)
        kargs = {}

        if data_view is not None:
            kargs['widget'] = self.widget(data_view=data_view)
        elif kwargs.get('widget', None) is None:
            raise ValueError('data_view is required else you need to provide your own widget instance.')

        kargs.update(kwargs)
        super(HeavySelect2FieldBase, self).__init__(**kargs)

class HeavySelect2ChoiceField(HeavySelect2FieldBase):
    widget = HeavySelect2Widget

class HeavySelect2MultipleChoiceField(HeavySelect2FieldBase):
    widget = HeavySelect2MultipleWidget

class AutoSelect2Field(ModelResultJsonMixin, AutoViewFieldMixin, HeavySelect2ChoiceField):
    """
    This needs to be subclassed. The first instance of a class (sub-class) is used to serve all incoming
    json query requests for that type (class).
    """

    widget = AutoHeavySelect2Widget

    def __init__(self, **kwargs):
        self.data_view = "django_select2_central_json"
        kwargs['data_view'] = self.data_view
        super(AutoSelect2Field, self).__init__(**kwargs)

class AutoModelSelect2Field(ModelResultJsonMixin, AutoViewFieldMixin, ModelValueMixin, HeavySelect2ChoiceField):
    """
    This needs to be subclassed. The first instance of a class (sub-class) is used to serve all incoming
    json query requests for that type (class).
    """

    widget = AutoHeavySelect2Widget

    def __init__(self, **kwargs):
        self.data_view = "django_select2_central_json"
        kwargs['data_view'] = self.data_view
        super(AutoModelSelect2Field, self).__init__(**kwargs)

class ModelSelect2Field(ModelValueMixin, Select2ChoiceField):
    def __init__(self, **kwargs):
        self.queryset = kwargs.pop('queryset', None)
        self.to_field_name = kwargs.pop('to_field_name', 'pk')
        
        choices = kwargs.pop('choices', None)
        if choices is None:
            choices = []
            for obj in self.queryset.all():
                choices.append((getattr(obj, self.to_field_name), smart_unicode(obj), ))

        kwargs['choices'] = choices

        super(ModelSelect2Field, self).__init__(**kwargs)

    def valid_value(self, value):
        val = getattr(value, self.to_field_name)
        for k, v in self.choices:
            if k == val:
                return True
        return False


    
