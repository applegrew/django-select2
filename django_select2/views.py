"""JSONResponse views for model widgets."""
from django.core import signing
from django.core.signing import BadSignature
from django.http import Http404, JsonResponse
from django.views.generic.list import BaseListView

from .cache import cache
from .conf import settings


class AutoResponseView(BaseListView):
    """
    View that handles requests from heavy model widgets.

    The view only supports HTTP's GET method.
    """

    def get(self, request, *args, **kwargs):
        """
        Return a :class:`.django.http.JsonResponse`.

        Example::

            {
                'results': [
                    {
                        'text': "foo",
                        'id': 123
                    }
                ],
                'more': true
            }

        """
        self.widget = self.get_widget_or_404()
        self.term = kwargs.get("term", request.GET.get("term", ""))
        self.object_list = self.get_queryset()
        context = self.get_context_data()
        return JsonResponse(
            {
                "results": [
                    {"text": self.widget.label_from_instance(obj), "id": obj.pk}
                    for obj in context["object_list"]
                ],
                "more": context["page_obj"].has_next(),
            }
        )

    def get_queryset(self):
        """Get QuerySet from cached widget."""
        kwargs = {
            model_field_name: self.request.GET.get(form_field_name)
            for form_field_name, model_field_name in self.widget.dependent_fields.items()
            if form_field_name in self.request.GET
            and self.request.GET.get(form_field_name, "") != ""
        }
        return self.widget.filter_queryset(
            self.request, self.term, self.queryset, **kwargs
        )

    def get_paginate_by(self, queryset):
        """Paginate response by size of widget's `max_results` parameter."""
        return self.widget.max_results

    def get_widget_or_404(self):
        """
        Get and return widget from cache.

        Raises:
            Http404: If if the widget can not be found or no id is provided.

        Returns:
            ModelSelect2Mixin: Widget from cache.

        """
        field_id = self.kwargs.get("field_id", self.request.GET.get("field_id", None))
        if not field_id:
            raise Http404('No "field_id" provided.')
        try:
            key = signing.loads(field_id)
        except BadSignature:
            raise Http404('Invalid "field_id".')
        else:
            cache_key = "%s%s" % (settings.SELECT2_CACHE_PREFIX, key)
            widget_dict = cache.get(cache_key)
            if widget_dict is None:
                raise Http404("field_id not found")
            if widget_dict.pop("url") != self.request.path:
                raise Http404("field_id was issued for the view.")
        qs, qs.query = widget_dict.pop("queryset")
        self.queryset = qs.all()
        widget_dict["queryset"] = self.queryset
        widget_cls = widget_dict.pop("cls")
        return widget_cls(**widget_dict)
