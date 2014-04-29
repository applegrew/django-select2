# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.conf.urls import patterns, url


urlpatterns = patterns('django_select2.views',
    url(r"^fields/auto.json$",
        'auto_response_view',
        name="django_select2_central_json"),
)
