# -*- conding:utf-8 -*-
from __future__ import absolute_import, unicode_literals

from django.conf.urls import include, url

from .forms import (
    AlbumModelSelect2WidgetForm, HeavySelect2MultipleWidgetForm,
    HeavySelect2WidgetForm, ModelSelect2TagWidgetForm, Select2WidgetForm
)
from .views import TemplateFormView, heavy_data_1, heavy_data_2

urlpatterns = [
    url(r'^select2_widget/$',
        TemplateFormView.as_view(form_class=Select2WidgetForm), name='select2_widget'),
    url(r'^heavy_select2_widget/$',
        TemplateFormView.as_view(form_class=HeavySelect2WidgetForm), name='heavy_select2_widget'),
    url(r'^heavy_select2_multiple_widget/$',
        TemplateFormView.as_view(form_class=HeavySelect2MultipleWidgetForm, success_url='/'),
        name='heavy_select2_multiple_widget'),

    url(r'^model_select2_widget/$',
        TemplateFormView.as_view(form_class=AlbumModelSelect2WidgetForm),
        name='model_select2_widget'),

    url(r'^model_select2_tag_widget/$',
        TemplateFormView.as_view(form_class=ModelSelect2TagWidgetForm),
        name='model_select2_tag_widget'),

    url(r'^heavy_data_1/$', heavy_data_1, name='heavy_data_1'),
    url(r'^heavy_data_2/$', heavy_data_2, name='heavy_data_2'),

    url(r'^select2/', include('django_select2.urls')),
]
