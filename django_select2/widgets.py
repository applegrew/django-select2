"""
Contains all the Django widgets for Select2.
"""

import logging
from itertools import chain
import util

from django import forms
from django.utils.encoding import force_unicode
from django.utils.safestring import mark_safe
from django.core.urlresolvers import reverse
from django.utils.datastructures import MultiValueDict, MergeDict

from .util import render_js_script, convert_to_js_string_arr, JSVar, JSFunction, JSFunctionInContext, \
    convert_dict_to_js_map, convert_to_js_arr

from . import __RENDER_SELECT2_STATICS as RENDER_SELECT2_STATICS

logger = logging.getLogger(__name__)


def get_select2_js_libs():
    from django.conf import settings
    if settings.configured and settings.DEBUG:
        return ('js/select2.js', )
    else:
        return ('js/select2.min.js', )

def get_select2_heavy_js_libs():
    libs = get_select2_js_libs()

    from django.conf import settings
    if settings.configured and settings.DEBUG:
        return libs + ('js/heavy_data.js', )
    else:
        return libs + ('js/heavy_data.min.js', )

def get_select2_css_libs(light=False):
    from django.conf import settings
    if settings.configured and settings.DEBUG:
        if light:
            return ('css/select2.css',)
        else:
            return ('css/select2.css', 'css/extra.css', )
    else:
        if light:
            return ('css/select2.min.css',)
        else:
            return ('css/all.min.css', )

### Light mixin and widgets ###

class Select2Mixin(object):
    """
    The base mixin of all Select2 widgets.

    This mixin is responsible for rendering the necessary Javascript and CSS codes which turns normal ``<select>``
    markups into Select2 choice list.

    The following Select2 otions are added by this mixin:-

        * minimumResultsForSearch: ``6``
        * placeholder: ``''``
        * allowClear: ``True``
        * multiple: ``False``
        * closeOnSelect: ``False``

    .. note:: Many of them would be removed by sub-classes depending on requirements.
    """

    # For details on these options refer: http://ivaynberg.github.com/select2/#documentation
    options = {
        'minimumResultsForSearch': 6,  # Only applicable for single value select.
        'placeholder': '',  # Empty text label
        'allowClear': True,  # Not allowed when field is multiple since there each value has a clear button.
        'multiple': False,  # Not allowed when attached to <select>
        'closeOnSelect': False,
    }
    """
    The options listed here are rendered as JS map and passed to Select2 JS code.
    Complete description of theses options are available in Select2_ JS' site.

    .. _Select2: http://ivaynberg.github.com/select2/#documentation.
    """

    def __init__(self, **kwargs):
        """
        Constructor of the class.

        The following additional kwarg is allowed:-

        :param select2_options: This is similar to standard Django way to pass extra attributes to widgets.
            This is meant to override values of existing :py:attr:`.options`.

            Example::

                class MyForm(ModelForm):
                    class Meta:
                        model = MyModel
                        widgets = {
                            'name': Select2WidgetName(select2_options={
                                'minimumResultsForSearch': 10,
                                'closeOnSelect': True,
                                })
                        }

            .. tip:: You cannot introduce new options using this. For that you should sub-class and overried
                :py:meth:`.init_options`. The reason for this is, few options are not compatible with each other
                or are not applicable in some scenarios. For example, when Select2 is attached to ``<select>`` tag,
                it can get if it is multiple or single valued from that tag itself. In this case if you specify
                ``multiple`` option then not only it is useless but an error in Select2 JS' point of view.

                There are other such intricacies, based on which some options are removed. By enforcing this
                restriction we make sure to not break the code by passing some wrong concotion of options.

        :type select2_options: :py:obj:`dict` or None

        """
        # Making an instance specific copy
        self.options = dict(self.options)
        select2_options = kwargs.pop('select2_options', None)
        if select2_options:
            for name, value in select2_options.items():
                self.options[name] = value
        self.init_options()

        super(Select2Mixin, self).__init__(**kwargs)

    def init_options(self):
        """
        Sub-classes can use this to suppress or override options passed to Select2 JS library.

        Example::

            def init_options(self):
                self.options['createSearchChoice'] = JSFunction('Your_js_function')

        In the above example we are setting ``Your_js_function`` as Select2's ``createSearchChoice``
        function.

        .. tip:: If you want to run ``Your_js_function`` in the context of the Select2 DOM element,
            i.e. ``this`` inside your JS function should point to the component instead of ``window``, then
            use :py:class:`~.util.JSFunctionInContext` instead of :py:class:`~.util.JSFunction`.
        """
        pass

    def set_placeholder(self, val):
        """
        Placeholder is a value which Select2 JS library shows when nothing is selected. This should be string.

        :return: None
        """
        self.options['placeholder'] = val

    def get_options(self):
        """
        :return: Dictionary of options to be passed to Select2 JS.

        :rtype: :py:obj:`dict`
        """
        options = dict(self.options)
        if options.get('allowClear', None) is not None:
            options['allowClear'] = not self.is_required
        return options

    def render_select2_options_code(self, options, id_):
        """
        Renders options for Select2 JS.

        :return: The rendered JS code.
        :rtype: :py:obj:`unicode`
        """
        return convert_dict_to_js_map(options, id_)

    def render_js_code(self, id_, *args):
        """
        Renders the ``<script>`` block which contains the JS code for this widget.

        :return: The rendered JS code enclosed inside ``<script>`` block.
        :rtype: :py:obj:`unicode`
        """
        if id_:
            return render_js_script(self.render_inner_js_code(id_, *args))
        return u''

    def render_inner_js_code(self, id_, *args):
        """
        Renders all the JS code required for this widget.

        :return: The rendered JS code which will be later enclosed inside ``<script>`` block.
        :rtype: :py:obj:`unicode`
        """
        options = dict(self.get_options())
        options = self.render_select2_options_code(options, id_)

        return u'$("#%s").select2(%s);' % (id_, options)

    def render(self, name, value, attrs=None, choices=()):
        """
        Renders this widget. Html and JS code blocks all are rendered by this.

        :return: The rendered markup.
        :rtype: :py:obj:`unicode`
        """
        if logger.isEnabledFor(logging.DEBUG):
            t1 = util.timer_start('Select2Mixin.render')

        args = [name, value, attrs]
        if choices:
            args.append(choices)

        s = unicode(super(Select2Mixin, self).render(*args))  # Thanks to @ouhouhsami Issue#1
        if RENDER_SELECT2_STATICS:
            s += self.media.render()
        final_attrs = self.build_attrs(attrs)
        id_ = final_attrs.get('id', None)
        s += self.render_js_code(id_, name, value, attrs, choices)

        if logger.isEnabledFor(logging.DEBUG):
            util.timer_end(t1)
            logger.debug("Generated widget code:-\n%s", s)

        return mark_safe(s)

    class Media:
        js = get_select2_js_libs()
        css = {'screen': get_select2_css_libs(light=True)}


class Select2Widget(Select2Mixin, forms.Select):
    """
    Drop-in Select2 replacement for :py:class:`forms.Select`.

    Following Select2 option from :py:attr:`.Select2Mixin.options` is removed:-

        * multiple

    """

    def init_options(self):
        self.options.pop('multiple', None)

    def render_options(self, choices, selected_choices):
        all_choices = chain(self.choices, choices)
        if not self.is_required and \
            len([value for value, txt in all_choices if value == '']) == 0: # Checking if list already has empty choice
                                                                            # as in the case of Model based Light fields.

            choices = list(choices)
            choices.append(('', '', ))  # Adding an empty choice
        return super(Select2Widget, self).render_options(choices, selected_choices)


class Select2MultipleWidget(Select2Mixin, forms.SelectMultiple):
    """
    Drop-in Select2 replacement for :py:class:`forms.SelectMultiple`.

    Following Select2 options from :py:attr:`.Select2Mixin.options` are removed:-

        * multiple
        * allowClear
        * minimumResultsForSearch

    """

    def init_options(self):
        self.options.pop('multiple', None)
        self.options.pop('allowClear', None)
        self.options.pop('minimumResultsForSearch', None)


### Specialized Multiple Hidden Input Widget ###
class MultipleSelect2HiddenInput(forms.TextInput):
    """
    Multiple hidden input for Select2.

    This is a specialized multiple Hidden Input widget. This includes a special
    JS component which renders multiple Hidden Input boxes as there are values.
    So, if user suppose chooses values 1, 4 and 9 then Select2 would would write them
    to the primary hidden input. The JS component of this widget will read that value and
    will render three more hidden input boxes each with values 1, 4 and 9 respectively.
    They will all share the name of this field, and the name of the primary source
    hidden input would be removed. This way, when submitted all the selected values
    would be available as list.
    """
    # We want it hidden but should be treated as if is_hidden is False
    input_type = 'hidden'

    def render(self, name, value, attrs=None, choices=()):
        attrs = self.build_attrs(attrs, multiple='multiple')
        s = unicode(super(MultipleSelect2HiddenInput, self).render(name, u"", attrs))
        id_ = attrs.get('id', None)
        if id_:
            jscode = u''
            if value:
                jscode = u"$('#%s').val(django_select2.convertArrToStr(%s));" \
                    % (id_, convert_to_js_arr(value, id_))
            jscode += u"django_select2.initMultipleHidden($('#%s'));" % id_
            s += render_js_script(jscode)
        return mark_safe(s)

    def value_from_datadict(self, data, files, name):
        if isinstance(data, (MultiValueDict, MergeDict)):
            return data.getlist(name)
        return data.get(name, None)

    def _has_changed(self, initial, data):
        if initial is None:
            initial = []
        if data is None:
            data = []
        if len(initial) != len(data):
            return True
        initial_set = set([force_unicode(value) for value in initial])
        data_set = set([force_unicode(value) for value in data])
        return data_set != initial_set

### Heavy mixins and widgets ###

class HeavySelect2Mixin(Select2Mixin):
    """
    The base mixin of all Heavy Select2 widgets. It sub-classes :py:class:`Select2Mixin`.

    This mixin adds more Select2 options to :py:attr:`.Select2Mixin.options`. These are:-

        * minimumInputLength: ``2``
        * initSelection: ``JSFunction('django_select2.onInit')``
        * ajax:
            * dataType: ``'json'``
            * quietMillis: ``100``
            * data: ``JSFunctionInContext('django_select2.get_url_params')``
            * results: ``JSFunctionInContext('django_select2.process_results')``

    .. tip:: You can override these options by passing ``select2_options`` kwarg to :py:meth:`.__init__`.
    """

    def __init__(self, **kwargs):
        """
        Constructor of the class.

        The following kwargs are allowed:-

        :param data_view: A :py:class:`~.views.Select2View` sub-class which can respond to this widget's Ajax queries.
        :type data_view: :py:class:`django.views.generic.base.View` or None

        :param data_url: Url which will respond to Ajax queries with JSON object.
        :type data_url: :py:obj:`str` or None

        .. tip:: When ``data_view`` is provided then it is converted into Url using
            :py:func:`~django.core.urlresolvers.reverse`.

        .. warning:: Either of ``data_view`` or ``data_url`` must be specified, else :py:exc:`ValueError` would
            be raised.

        :param choices: The list of available choices. If not provided then empty list is used instead. It
            should be of the form -- ``[(val1, 'Label1'), (val2, 'Label2'), ...]``.
        :type choices: :py:obj:`list` or :py:obj:`tuple`

        :param userGetValTextFuncName: The name of the custom JS function which you want to use to convert
            value to label.

            In ``heavy_data.js``, ``django_select2.getValText()`` employs the following logic to convert value
            to label :-

                1. First check if the Select2 input field has ``txt`` attribute set along with ``value``. If found
                then use it.

                2. Otherwise, check if user has provided any custom method for this. Then use that. If it returns a
                label then use it.

                3. Otherwise, check the cached results. When the user searches in the fields then all the returned
                responses from server, which has the value and label mapping, are cached by ``heavy_data.js``.

        :type userGetValTextFuncName: :py:obj:`str`

        .. tip:: Since version 3.2.0, cookies or localStorage are no longer checked or used. All
            :py:class:`~.field.HeavyChoiceField` must override :py:meth:`~.fields.HeavyChoiceField.get_val_txt`.
            If you are only using heavy widgets in your own fields then you should override :py:meth:`.render_texts`.
        """
        self.field = None
        self.options = dict(self.options)  # Making an instance specific copy
        self.view = kwargs.pop('data_view', None)
        self.url = kwargs.pop('data_url', None)
        self.userGetValTextFuncName = kwargs.pop('userGetValTextFuncName', u'null')
        self.choices = kwargs.pop('choices', [])

        if not self.view and not self.url:
            raise ValueError('data_view or data_url is required')

        self.options['ajax'] = {
            'dataType': 'json',
            'quietMillis': 100,
            'data': JSFunctionInContext('django_select2.get_url_params'),
            'results': JSFunctionInContext('django_select2.process_results'),
        }
        self.options['minimumInputLength'] = 2
        self.options['initSelection'] = JSFunction('django_select2.onInit')
        super(HeavySelect2Mixin, self).__init__(**kwargs)

    def render_texts(self, selected_choices, choices):
        """
        Renders a JS array with labels for the ``selected_choices``.

        :param selected_choices: List of selected choices' values.
        :type selected_choices: :py:obj:`list` or :py:obj:`tuple`

        :param choices: Extra choices, if any. This is a list of tuples. In each tuple, the first
            item is the choice value and the second item is choice label.
        :type choices: :py:obj:`list` or :py:obj:`tuple`

        :return: The rendered JS array code.
        :rtype: :py:obj:`unicode`
        """
        selected_choices = list(force_unicode(v) for v in selected_choices)
        txts = []
        all_choices = choices if choices else []
        choices_dict = dict()
        self_choices = self.choices

        import fields
        if isinstance(self_choices, fields.FilterableModelChoiceIterator):
            self_choices.set_extra_filter(**{'%s__in' % self.field.get_pk_field_name(): selected_choices})

        for val, txt in chain(self_choices, all_choices):
            val = force_unicode(val)
            choices_dict[val] = txt

        for val in selected_choices:
            try:
                txts.append(choices_dict[val])
            except KeyError:
                logger.error("Value '%s' is not a valid choice.", val)

        if hasattr(self.field, '_get_val_txt') and selected_choices:
            for val in selected_choices:
                txt = self.field._get_val_txt(val)
                if txt is not None:
                    txts.append(txt)
        if txts:
            return convert_to_js_string_arr(txts)

    def get_options(self):
        if self.url is None:
            # We lazy resolve the view. By this time Url conf would been loaded fully.
            self.url = reverse(self.view)

        if self.options['ajax'].get('url', None) is None:
            self.options['ajax']['url'] = self.url

        return super(HeavySelect2Mixin, self).get_options()

    def render_texts_for_value(self, id_, value, choices):
        """
        Renders the JS code which sets the ``txt`` attribute on the field. It gets the array
        of lables from :py:meth:`.render_texts`.

        :param id_: Id of the field. This can be used to get reference of this field's DOM in JS.
        :type id_: :py:obj:`str`

        :param value: Currently set value on the field.
        :type value: Any

        :param choices: Extra choices, if any. This is a list of tuples. In each tuple, the first
            item is the choice value and the second item is choice label.
        :type choices: :py:obj:`list` or :py:obj:`tuple`

        :return: JS code which sets the ``txt`` attribute.
        :rtype: :py:obj:`unicode`
        """
        if value is not None:
            # Just like forms.Select.render() it assumes that value will be single valued.
            values = [value]
            texts = self.render_texts(values, choices)
            if texts:
                return u"$('#%s').txt(%s);" % (id_, texts)

    def render_inner_js_code(self, id_, name, value, attrs=None, choices=(), *args):
        js = u"$('#%s').change(django_select2.onValChange).data('userGetValText', %s);" \
            % (id_, self.userGetValTextFuncName)
        texts = self.render_texts_for_value(id_, value, choices)
        if texts:
            js += texts
        js += super(HeavySelect2Mixin, self).render_inner_js_code(id_, name, value, attrs, choices, *args)
        return js

    class Media:
        js = get_select2_heavy_js_libs()
        css = {'screen': get_select2_css_libs()}


class HeavySelect2Widget(HeavySelect2Mixin, forms.TextInput):
    """
    Single selection heavy widget.

    Following Select2 option from :py:attr:`.Select2Mixin.options` is added or set:-

        * multiple: ``False``

    """
    # We want it hidden but should be treated as if is_hidden is False
    input_type = 'hidden'

    def init_options(self):
        self.options['multiple'] = False


class HeavySelect2MultipleWidget(HeavySelect2Mixin, MultipleSelect2HiddenInput):
    """
    Multiple selection heavy widget.

    Following Select2 options from :py:attr:`.Select2Mixin.options` are removed:-

        * allowClear
        * minimumResultsForSearch

    Following Select2 options from :py:attr:`.Select2Mixin.options` are added or set:-

        * multiple: ``True``
        * separator: ``JSVar('django_select2.MULTISEPARATOR')``

    """

    def init_options(self):
        self.options['multiple'] = True
        self.options.pop('allowClear', None)
        self.options.pop('minimumResultsForSearch', None)
        self.options['separator'] = JSVar('django_select2.MULTISEPARATOR')

    def render_texts_for_value(self, id_, value, choices):
        """
        Renders the JS code which sets the ``txt`` attribute on the field. It gets the array
        of lables from :py:meth:`.render_texts`.

        :param id_: Id of the field. This can be used to get reference of this field's DOM in JS.
        :type id_: :py:obj:`str`

        :param value: **List** of currently set value on the field.
        :type value: :py:obj:`list`

        :param choices: Extra choices, if any. This is a list of tuples. In each tuple, the first
            item is the choice value and the second item is choice label.
        :type choices: :py:obj:`list` or :py:obj:`tuple`

        :return: JS code which sets the ``txt`` attribute.
        :rtype: :py:obj:`unicode`
        """
        # Just like forms.SelectMultiple.render() it assumes that value will be multi-valued (list).
        if value:
            texts = self.render_texts(value, choices)
            if texts:
                return u"$('#%s').txt(%s);" % (id_, texts)

class HeavySelect2TagWidget(HeavySelect2MultipleWidget):
    """
    Heavy widget with tagging support. Based on :py:class:`HeavySelect2MultipleWidget`,
    unlike other widgets this allows users to create new options (tags).

    Following Select2 options from :py:attr:`.Select2Mixin.options` are removed:-

        * allowClear
        * minimumResultsForSearch
        * closeOnSelect

    Following Select2 options from :py:attr:`.Select2Mixin.options` are added or set:-

        * multiple: ``True``
        * separator: ``JSVar('django_select2.MULTISEPARATOR')``
        * tags: ``True``
        * tokenSeparators: ``,`` and `` ``
        * createSearchChoice: ``JSFunctionInContext('django_select2.createSearchChoice')``
        * minimumInputLength: ``1``

    """
    def init_options(self):
        super(HeavySelect2TagWidget, self).init_options()
        self.options.pop('closeOnSelect', None)
        self.options['minimumInputLength'] = 1
        self.options['tags'] = True
        self.options['tokenSeparators'] = [",", " "]
        self.options['createSearchChoice'] = JSFunctionInContext('django_select2.createSearchChoice')

### Auto Heavy widgets ###

class AutoHeavySelect2Mixin(object):
    """
    This mixin is needed for Auto heavy fields.

    This mxin adds extra JS code to notify the field's DOM object of the generated id. The generated id
    is not the same as the ``id`` attribute of the field's Html markup. This id is generated by
    :py:func:`~.util.register_field` when the Auto field is registered. The client side (DOM) sends this
    id along with the Ajax request, so that the central view can identify which field should be used to
    serve the request.
    """

    def __init__(self, *args, **kwargs):
        kwargs['data_view'] = "django_select2_central_json"
        super(AutoHeavySelect2Mixin, self).__init__(*args, **kwargs)

    def render_inner_js_code(self, id_, *args):
        js = u"$('#%s').data('field_id', '%s');" % (id_, self.field_id)
        js += super(AutoHeavySelect2Mixin, self).render_inner_js_code(id_, *args)
        return js


class AutoHeavySelect2Widget(AutoHeavySelect2Mixin, HeavySelect2Widget):
    "Auto version of :py:class:`.HeavySelect2Widget`"
    pass


class AutoHeavySelect2MultipleWidget(AutoHeavySelect2Mixin, HeavySelect2MultipleWidget):
    "Auto version of :py:class:`.HeavySelect2MultipleWidget`"
    pass

class AutoHeavySelect2TagWidget(AutoHeavySelect2Mixin, HeavySelect2TagWidget):
    "Auto version of :py:class:`.HeavySelect2TagWidget`"
    pass
