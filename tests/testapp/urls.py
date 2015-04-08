# -*- conding:utf-8 -*-
from __future__ import absolute_import, unicode_literals

from django.conf.urls import include, patterns, url

from .forms import ArtistForm, Select2WidgetForm
from .views import TemplateFormView

urlpatterns = patterns(
    '',
    url(r'select2_widget',
        TemplateFormView.as_view(form_class=Select2WidgetForm), name='select2_widget'),
    url(r'single_value_model_field',
        TemplateFormView.as_view(form_class=ArtistForm), name='single_value_model_field'),

    url(r'^select2/', include('django_select2.urls')),
)
