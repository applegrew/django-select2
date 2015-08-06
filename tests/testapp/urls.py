# -*- conding:utf-8 -*-
from __future__ import absolute_import, unicode_literals

from django.conf.urls import include, patterns, url

from .forms import (
    ArtistForm, HeavySelect2MultipleWidgetForm, HeavySelect2WidgetForm,
    Select2WidgetForm
)
from .views import TemplateFormView, heavy_data

urlpatterns = patterns(
    '',
    url(r'^select2_widget/$',
        TemplateFormView.as_view(form_class=Select2WidgetForm), name='select2_widget'),
    url(r'^heavy_select2_widget/$',
        TemplateFormView.as_view(form_class=HeavySelect2WidgetForm), name='heavy_select2_widget'),
    url(r'^heavy_select2_multiple_widget/$',
        TemplateFormView.as_view(form_class=HeavySelect2MultipleWidgetForm), name='heavy_select2_multiple_widget'),
    url(r'^single_value_model_field/$',
        TemplateFormView.as_view(form_class=ArtistForm), name='single_value_model_field'),
    url(r'^heavy_data/$',
        heavy_data, name='heavy_data'),

    url(r'^select2/', include('django_select2.urls')),
)
