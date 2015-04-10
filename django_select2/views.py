# -*- coding:utf-8 -*-
from __future__ import absolute_import, unicode_literals

import json

from django.core.exceptions import PermissionDenied
from django.http import Http404, HttpResponse
from django.utils.six import binary_type
from django.views.generic import View

from .util import get_field, is_valid_id

NO_ERR_RESP = 'nil'
"""
Equals to 'nil' constant.

Use this in :py:meth:`.Select2View.get_results` to mean no error, instead of hardcoding 'nil' value.
"""


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
        """Convert the context dictionary into a JSON object"""
        return json.dumps(context)


class Select2View(JSONResponseMixin, View):
    """
    Base view which is designed to respond with JSON to Ajax queries from heavy widgets/fields.

    Although the widgets won't enforce the type of data_view it gets, but it is recommended to
    sub-class this view instead of creating a Django view from scratch.

    .. note:: Only `GET <http://www.w3.org/Protocols/rfc2616/rfc2616-sec9.html#sec9.3>`_ Http requests are supported.
    """

    def dispatch(self, request, *args, **kwargs):
        try:
            self.check_all_permissions(request, *args, **kwargs)
        except Exception as e:
            return self.respond_with_exception(e)
        return super(Select2View, self).dispatch(request, *args, **kwargs)

    def get(self, request, *args, **kwargs):
        term = request.GET.get('term', None)
        if term is None:
            return self.render_to_response(self._results_to_context(('missing term', False, [], )))

        try:
            page = int(request.GET.get('page', None))
            if page <= 0:
                page = -1
        except ValueError:
            page = -1
        if page == -1:
            return self.render_to_response(self._results_to_context(('bad page no.', False, [], )))
        context = request.GET.get('context', None)

        return self.render_to_response(
            self._results_to_context(
                self.get_results(request, term, page, context)
                )
            )

    def respond_with_exception(self, e):
        """
        :param e: Exception object.
        :type e: Exception
        :return: Response with status code of 404 if e is ``Http404`` object,
            else 400.
        :rtype: HttpResponse
        """
        if isinstance(e, Http404):
            status = 404
        else:
            status = getattr(e, 'status_code', 400)
        return self.render_to_response(
            self._results_to_context((binary_type(e), False, [],)),
            status=status
            )

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

    def check_all_permissions(self, request, *args, **kwargs):
        """
        Sub-classes can use this to raise exception on permission check failures,
        or these checks can be placed in ``urls.py``, e.g. ``login_required(SelectClass.as_view())``.

        :param request: The Ajax request object.
        :type request: :py:class:`django.http.HttpRequest`

        :param args: The ``*args`` passed to :py:meth:`django.views.generic.View.dispatch`.
        :param kwargs: The ``**kwargs`` passed to :py:meth:`django.views.generic.View.dispatch`.

        .. warning:: Sub-classes should override this. You really do not want random people making
            Http requests to your server, be able to get access to sensitive information.
        """
        pass

    def get_results(self, request, term, page, context):
        """
        Returns the result for the given search ``term``.

        :param request: The Ajax request object.
        :type request: :py:class:`django.http.HttpRequest`

        :param term: The search term.
        :type term: :py:obj:`str`

        :param page: The page number. If in your last response you had signalled that there are more results,
            then when user scrolls more a new Ajax request would be sent for the same term but with next page
            number. (Page number starts at 1)
        :type page: :py:obj:`int`

        :param context: Can be anything which persists across the lifecycle of queries for the same search term.
            It is reset to ``None`` when the term changes.

            .. note:: Currently this is not used by ``heavy_data.js``.
        :type context: :py:obj:`str` or None

        Expected output is of the form::

            (err, has_more, [results])

        Where ``results = [(id1, text1), (id2, text2), ...]``

        For example::

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
    """
    A central view meant to respond to Ajax queries for all Heavy widgets/fields.
    Although it is not mandatory to use, but is immensely helpful.

    .. tip:: Fields which want to use this view must sub-class :py:class:`~.widgets.AutoViewFieldMixin`.
    """
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
