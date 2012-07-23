from django import forms

from .widgets import Select2Widget, Select2MultipleWidget, HeavySelect2Widget, HeavySelect2MultipleWidget

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

class ModelSelect2Field(HeavySelect2ChoiceField):
    def __init__(self, **kwargs):
        self.queryset = kwargs.pop('queryset', None)
        if self.queryset is None:
            raise ValueError('queryset is required.')
        self.max_results = kwargs.pop('max_results', None)
        self.search_fields = kwargs.pop('search_fields', None)
        if not self.search_fields:
            raise ValueError('search_fields is required.')
        kargs = {}
        kargs['data_view'] = "django_select2_central_json"
        kargs.update(kwargs)
        super(ModelSelect2Field, self).__init__(**kargs)

    def security_check(self, request):
        raise NotImplemented


