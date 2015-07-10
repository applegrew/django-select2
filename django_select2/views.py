# -*- coding:utf-8 -*-
from __future__ import absolute_import, unicode_literals

from django.http import Http404, JsonResponse, HttpResponseForbidden
from django.utils.encoding import smart_text
from django.views.generic.list import BaseListView

from .util import get_field, is_valid_id


NO_ERR_RESP = 'nil'
"""
Equals to 'nil' constant.

Use this in :py:meth:`.Select2View.get_results` to mean no error, instead of hardcoding 'nil' value.
"""


class AutoResponseView(BaseListView):
    """
    A central view meant to respond to Ajax queries for all Heavy widgets/fields.

    Although it is not mandatory to use, but is immensely helpful.

    .. tip:: Fields which want to use this view must sub-class :py:class:`~.widgets.AutoViewFieldMixin`.
    """

    def get(self, request, *args, **kwargs):
        self.field = self.get_field_or_404()
        self.term = kwargs.get('term', request.GET.get('term', ''))

        if not self.field.security_check(request, *args, **kwargs):
            return HttpResponseForbidden('Permission denied.')

        self.object_list = self.get_queryset()
        context = self.get_context_data()
        return JsonResponse({
            'results': [
                {
                    'text': smart_text(obj),
                    'id': obj.pk,
                }
                for obj in context['object_list']
                ],
            'err': NO_ERR_RESP,
            'more': context['is_paginated']
        })

    def get_queryset(self):
        return self.field.get_results(self.request, self.term)

    def get_paginate_by(self, queryset):
        return self.field.max_results

    def get_field_or_404(self):
        field_id = self.kwargs.get('field_id', self.request.GET.get('field_id', None))
        if field_id is None or not is_valid_id(field_id):
            raise Http404
        field = get_field(field_id)
        if field is None:
            raise Http404
        return field
