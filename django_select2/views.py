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
    """
    A central view meant to respond to Ajax queries for all Heavy widgets/fields.

    Although it is not mandatory to use, but is immensely helpful.

    .. tip:: Fields which want to use this view must sub-class :py:class:`~.widgets.AutoViewFieldMixin`.
    """

    def get(self, request, *args, **kwargs):
        self.widget = self.get_widget_or_404()
        self.term = kwargs.get('term', request.GET.get('term', ''))

        try:
            self.object_list = self.get_queryset()
        except NotImplementedError:
            self.object_list = []
            context = self.get_context_data()
            results = self.widget.field.get_results(
                self.request,
                self.term,
                int(self.request.GET.get('page', 1)),
                context
            )
            return JsonResponse(self._results_to_context(results))
        else:
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

    def _results_to_context(self, output):
        err, has_more, results = output
        res = []
        if err == NO_ERR_RESP:
            for result in results:
                id_, text = result[:2]
                if len(result) > 2:
                    extra_data = result[2]
                else:
                    extra_data = {}
                res.append(dict(id=id_, text=text, **extra_data))
        return {
            'err': err,
            'more': has_more,
            'results': res,
        }
