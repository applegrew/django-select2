# -*- conding:utf-8 -*-
from __future__ import absolute_import, unicode_literals

from django.conf.urls import include, patterns, url

from .forms import ArtistForm
from .views import TemplateFormView

urlpatterns = patterns(
    '',
    url(r'single_value_model_field',
        TemplateFormView.as_view(form_class=ArtistForm), name='single_value_model_field'),

    url(r'^select2/', include('django_select2.urls')),
)
