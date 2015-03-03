# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.views.generic import FormView


class TemplateFormView(FormView):
    template_name = 'form.html'
