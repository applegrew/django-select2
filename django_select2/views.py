# -*- coding: utf-8 -*-
from __future__ import absolute_import, unicode_literals

from django.core import signing
from django.core.signing import BadSignature
from django.http import Http404, JsonResponse
from django.utils.encoding import smart_text
from django.views.generic.list import BaseListView

from .cache import cache
from .conf import settings
from .types import NO_ERR_RESP


class AutoResponseView(BaseListView):

    def get(self, request, *args, **kwargs):
        self.widget = self.get_widget_or_404()
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
        return self.widget.filter_queryset(self.term)

    def get_paginate_by(self, queryset):
        return self.widget.max_results

    def get_widget_or_404(self):
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
