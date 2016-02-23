# -*- coding: utf-8 -*-
from __future__ import unicode_literals

import json

from django.http import HttpResponse
from django.views.generic import FormView


class TemplateFormView(FormView):
    template_name = 'form.html'


def heavy_data_1(request):
    term = request.GET.get("term", "")
    numbers = ['Zero', 'One', 'Two', 'Three', 'Four', 'Five']
    numbers = filter(lambda num: term.lower() in num.lower(), numbers)
    results = [{'id': index, 'text': value} for (index, value) in enumerate(numbers)]
    return HttpResponse(json.dumps({'err': 'nil', 'results': results}), content_type='application/json')


def heavy_data_2(request):
    term = request.GET.get("term", "")
    numbers = ['Six', 'Seven', 'Eight', 'Nine', 'Ten', 'Fortytwo']
    numbers = filter(lambda num: term.lower() in num.lower(), numbers)
    results = [{'id': index, 'text': value} for (index, value) in enumerate(numbers)]
    return HttpResponse(json.dumps({'err': 'nil', 'results': results}), content_type='application/json')
