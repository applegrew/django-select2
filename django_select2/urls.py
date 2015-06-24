# -*- coding:utf-8 -*-
from __future__ import absolute_import, unicode_literals

from django.conf.urls import patterns, url

from .views import AutoResponseView

urlpatterns = patterns(
    "",
    url(r"^fields/auto.json$",
        AutoResponseView.as_view(), name="django_select2_central_json"),
)
