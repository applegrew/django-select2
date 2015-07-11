# -*- coding:utf-8 -*-
from __future__ import absolute_import, unicode_literals

from django.core import signing
from django.core.signing import BadSignature
from django.http import Http404, JsonResponse
from django.utils.encoding import smart_text
from django.views.generic.list import BaseListView

from django_select2.cache import cache

from .conf import settings

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
        if not field_id:
            raise Http404('No "field_id" provided.')
        try:
            key = signing.loads(field_id)
        except BadSignature:
            raise Http404('Invalid "field_id".')
        else:
            cache_key = '%s%s' % (settings.SELECT2_CACHE_PREFIX, key)
            field = cache.get(cache_key)
            if field is None:
                raise Http404('field_id not found')
        return field
