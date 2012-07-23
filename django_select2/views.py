
import json
from django.http import HttpResponse
from django.views.generic import View

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
        self.check_all_permissions(request, *args, **kwargs)
        return super(Select2View, self).dispatch(request, *args, **kwargs)

    def get(self, request, *args, **kwargs):
        if request.method == 'GET':
            term = request.GET.get('term', None)
            if term is None:
                return self.render_to_response(self._results_to_context(('missing term', False, [])))
            page = request.GET.get('page', None)
            context = request.GET.get('context', None)
        else:
            return self.render_to_response(self._results_to_context(('not a get request', False, [])))

        return self.render_to_response(
            self._results_to_context(
                self.get_results(request, term, page, context)
                )
            )

    def _results_to_context(self, output):
        err, has_more, results = output
        res = []
        if err == 'nil':
            for id_, text in results:
                res.append({'id': id_, 'text': text})
        return {
            'err': err,
            'more': has_more,
            'results': res
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
        raise NotImplemented
