import json

from django.http import HttpResponse
from django.views.generic import View
from django.core.exceptions import PermissionDenied
from django.http import Http404

from .util import get_field, is_valid_id

NO_ERR_RESP = 'nil'

class JSONResponseMixin(object):
    """
    A mixin that can be used to render a JSON response.
    """
    response_class = HttpResponse

    def render_to_response(self, context, **response_kwargs):
        """
        Returns a JSON response, transforming 'context' to make the payload.
        """
        response_kwargs['content_type'] = 'application/json'
        return self.response_class(
            self.convert_context_to_json(context),
            **response_kwargs
        )

    def convert_context_to_json(self, context):
        "Convert the context dictionary into a JSON object"
        return json.dumps(context)

class Select2View(JSONResponseMixin, View):

    def dispatch(self, request, *args, **kwargs):
        try:
            self.check_all_permissions(request, *args, **kwargs)
        except Exception, e:
            return self.respond_with_exception(e)
        return super(Select2View, self).dispatch(request, *args, **kwargs)

    def get(self, request, *args, **kwargs):
        if request.method == 'GET':
            term = request.GET.get('term', None)
            if term is None:
                return self.render_to_response(self._results_to_context(('missing term', False, [], )))
            if not term:
                return self.render_to_response(self._results_to_context((NO_ERR_RESP, False, [], )))

            try:
                page = int(request.GET.get('page', None))
                if page <= 0:
                    page = -1
            except ValueError:
                page = -1
            if page == -1:
                return self.render_to_response(self._results_to_context(('bade page no.', False, [], )))
            context = request.GET.get('context', None)
        else:
            return self.render_to_response(self._results_to_context(('not a get request', False, [], )))

        return self.render_to_response(
            self._results_to_context(
                self.get_results(request, term, page, context)
                )
            )

    def respond_with_exception(self, e):
        if isinstance(e, Http404):
            status = 404
        else:
            status = getattr(e, 'status_code', 400)
        return self.render_to_response(
            self._results_to_context((str(e), False, [],)),
            status=status
            )

    def _results_to_context(self, output):
        err, has_more, results = output
        res = []
        if err == NO_ERR_RESP:
            for id_, text in results:
                res.append({'id': id_, 'text': text})
        return {
            'err': err,
            'more': has_more,
            'results': res,
        }

    def check_all_permissions(self, request, *args, **kwargs):
        """Sub-classes can use this to raise exception on permission check failures,
        or these checks can be placed in urls.py, e.g. login_required(SelectClass.as_view())."""
        pass

    def get_results(self, request, term, page, context):
        """
        Expected output is of the form:-
        (err, has_more, [results]), where results = [(id1, text1), (id2, text2),...]
        e.g.
        ('nil', False,
            [
            (1, 'Value label1'),
            (20, 'Value label2'),
            ])
        When everything is fine then the `err` must be 'nil'.
        `has_more` should be true if there are more rows.
        """
        raise NotImplementedError


class AutoResponseView(Select2View):
    """A central view meant to respond to Ajax queries for all Heavy fields. Although it is not mandatory to use. This is just a helper."""
    def check_all_permissions(self, request, *args, **kwargs):
        id_ = request.GET.get('field_id', None)
        if id_ is None or not is_valid_id(id_):
            raise Http404('field_id not found or is invalid')
        field = get_field(id_)
        if field is None:
            raise Http404('field_id not found')

        if not field.security_check(request, *args, **kwargs):
            raise PermissionDenied('permission denied')

        request.__django_select2_local = field

    def get_results(self, request, term, page, context):
        field = request.__django_select2_local
        del request.__django_select2_local
        return field.get_results(request, term, page, context)


