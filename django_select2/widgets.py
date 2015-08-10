# -*- coding:utf-8 -*-
"""
Contains all the Django widgets for Select2.
"""
from __future__ import absolute_import, unicode_literals

import json
import logging
import re
from itertools import chain

from django import forms
from django.core.urlresolvers import reverse
from django.core.validators import EMPTY_VALUES
from django.utils.datastructures import MergeDict, MultiValueDict
from django.utils.encoding import force_text
from django.utils.safestring import mark_safe
from django.utils.six import text_type

from django_select2.media import (get_select2_css_libs,
                                  get_select2_heavy_js_libs,
                                  get_select2_js_libs)

from . import __RENDER_SELECT2_STATICS as RENDER_SELECT2_STATICS

logger = logging.getLogger(__name__)


# ## Light mixin and widgets ##


class Select2Mixin(object):
    """
    The base mixin of all Select2 widgets.

    This mixin is responsible for rendering the necessary JavaScript and CSS codes which turns normal ``<select>``
    markups into Select2 choice list.

    The following Select2 options are added by this mixin:-

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
    Complete description of these options are available in Select2_ JS' site.

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

            .. tip:: You cannot introduce new options using this. For that you should sub-class and override
                :py:meth:`.init_options`. The reason for this is, few options are not compatible with each other
                or are not applicable in some scenarios. For example, when Select2 is attached to a ``<select>`` tag,
                it can detect if it is being used with a single or multiple values from that tag itself. If you specified the
                ``multiple`` option in this case, it would not only be useless but an error from Select2 JS' point of view.

                There are other such intricacies, based on which some options are removed. By enforcing this
                restriction we make sure to not break the code by passing some wrong concoction of options.

            .. tip:: According to the select2 documentation, in order to get the ``placeholder`` and ``allowClear``
                settings working, you have to specify an empty ``<option></option>`` as the first entry in your
                ``<select>`` list. Otherwise the field will be rendered without a placeholder and the clear feature
                will stay disabled.


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
                self.options['createSearchChoice'] = 'Your_js_function'

        In the above example we are setting ``Your_js_function`` as Select2's ``createSearchChoice``
        function.
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
        if options.get('placeholder'):
            options['placeholder'] = force_text(options['placeholder'])
        return options

    def render_js_code(self, id_, *args):
        """
        Renders the ``<script>`` block which contains the JS code for this widget.

        :return: The rendered JS code enclosed inside ``<script>`` block.
        :rtype: :py:obj:`unicode`
        """
        if id_:
            return self.render_js_script(self.render_inner_js_code(id_, *args))
        return ''

    def render_js_script(self, inner_code):
        """
        This wraps ``inner_code`` string inside the following code block::

            <script type="text/javascript">
                jQuery(function ($) {
                    // inner_code here
                });
            </script>

        :rtype: :py:obj:`unicode`
        """
        return """
                <script type="text/javascript">
                    jQuery(function ($) {
                        %s
                    });
                </script>
                """ % inner_code

    def render_inner_js_code(self, id_, *args):
        """
        Renders all the JS code required for this widget.

        :return: The rendered JS code which will be later enclosed inside ``<script>`` block.
        :rtype: :py:obj:`unicode`
        """
        options = json.dumps(self.get_options())
        options = options.replace('"*START*', '').replace('*END*"', '')
        js = 'var hashedSelector = "#" + "%s";' % id_
        js += '$(hashedSelector).select2(%s);' % (options)
        return js

    def render(self, name, value, attrs=None, choices=()):
        """
        Renders this widget. HTML and JS code blocks all are rendered by this.

        :return: The rendered markup.
        :rtype: :py:obj:`unicode`
        """

        args = [name, value, attrs]
        if choices:
            args.append(choices)

        s = text_type(super(Select2Mixin, self).render(*args))  # Thanks to @ouhouhsami Issue#1
        s += self.media.render()
        final_attrs = self.build_attrs(attrs)
        id_ = final_attrs.get('id', None)
        s += self.render_js_code(id_, name, value, attrs, choices)

        return mark_safe(s)

    def _get_media(self):
        """
        Construct Media as a dynamic property

        This is essential because we need to check RENDER_SELECT2_STATICS
        before returning our assets.

        for more information:
        https://docs.djangoproject.com/en/1.8/topics/forms/media/#media-as-a-dynamic-property
        """
        if RENDER_SELECT2_STATICS:
            return forms.Media(
                js=get_select2_js_libs(),
                css={'screen': get_select2_css_libs(light=True)}
            )
        return forms.Media()
    media = property(_get_media)


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
        if not self.is_required \
                and len([value for value, txt in all_choices if value == '']) == 0:
            # Checking if list already has empty choice
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


# ## Specialized Multiple Hidden Input Widget ##


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

    def render(self, name, value, attrs=None, choices=()):
        attrs = self.build_attrs(attrs, multiple='multiple')
        s = text_type(super(MultipleSelect2HiddenInput, self).render(name, "", attrs))
        id_ = attrs.get('id', None)
        if id_:
            jscode = ''
            if value:
                jscode = '$("#%s").val(django_select2.convertArrToStr(%s));' % (id_, json.dumps(value))
            jscode += "django_select2.initMultipleHidden($('#%s'));" % id_
            s += self.render_js_script(jscode)
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
        initial_set = set([force_text(value) for value in initial])
        data_set = set([force_text(value) for value in data])
        return data_set != initial_set

    @property
    def is_hidden(self):
        # we return false because even if input_type is 'hidden'
        # , the final field will be displayed by javascript
        # and we want label and other layout elements.
        return False


# ## Heavy mixins and widgets ###

class HeavySelect2Mixin(Select2Mixin):
    """
    The base mixin of all Heavy Select2 widgets. It sub-classes :py:class:`Select2Mixin`.

    This mixin adds more Select2 options to :py:attr:`.Select2Mixin.options`. These are:-

        * minimumInputLength: ``2``
        * initSelection: ``'django_select2.onInit'``
        * ajax:
            * dataType: ``'json'``
            * quietMillis: ``100``
            * data: ``'django_select2.get_url_params'``
            * results: ``'django_select2.process_results'``

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

        .. tip:: When ``data_view`` is provided then it is converted into an URL using
            :py:func:`~django.core.urlresolvers.reverse`.

        .. warning:: Either of ``data_view`` or ``data_url`` must be specified, otherwise :py:exc:`ValueError` will
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
        self.userGetValTextFuncName = kwargs.pop('userGetValTextFuncName', 'null')
        self.choices = kwargs.pop('choices', [])

        if not self.view and not self.url:
            raise ValueError('data_view or data_url is required')

        self.options['ajax'] = {
            'dataType': 'json',
            'quietMillis': 100,
            'data': '*START*django_select2.runInContextHelper(django_select2.get_url_params, selector)*END*',
            'results': '*START*django_select2.runInContextHelper(django_select2.process_results, selector)*END*',
        }
        self.options['minimumInputLength'] = 2
        self.options['initSelection'] = '*START*django_select2.onInit*END*'
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
        selected_choices = list(force_text(v) for v in selected_choices)
        txts = []
        all_choices = choices if choices else []
        choices_dict = dict()
        self_choices = self.choices

        from . import fields
        if isinstance(self_choices, fields.FilterableModelChoiceIterator):
            self_choices.set_extra_filter(**{'%s__in' % self.field.get_pk_field_name(): selected_choices})

        for val, txt in chain(self_choices, all_choices):
            val = force_text(val)
            choices_dict[val] = force_text(txt)

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
            return json.dumps(txts)

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
        empty_values = getattr(self.field, 'empty_values', EMPTY_VALUES)
        if value is not None and (self.field is None or value not in empty_values):
            # Just like forms.Select.render() it assumes that value will be single valued.
            values = [value]
            texts = self.render_texts(values, choices)
            if texts:
                return "$('#%s').txt(%s);" % (id_, texts)

    def render_inner_js_code(self, id_, name, value, attrs=None, choices=(), *args):
        js = '$(hashedSelector).change(django_select2.onValChange).data("userGetValText", null);'
        texts = self.render_texts_for_value(id_, value, choices)
        if texts:
            js += texts
        js += super(HeavySelect2Mixin, self).render_inner_js_code(id_, name, value, attrs, choices, *args)
        return js

    def _get_media(self):
        """
        Construct Media as a dynamic property

        This is essential because we need to check RENDER_SELECT2_STATICS
        before returning our assets.

        for more information:
        https://docs.djangoproject.com/en/1.8/topics/forms/media/#media-as-a-dynamic-property
        """
        if RENDER_SELECT2_STATICS:
            return forms.Media(
                js=get_select2_heavy_js_libs(),
                css={'screen': get_select2_css_libs()}
            )
        return forms.Media()
    media = property(_get_media)


class HeavySelect2Widget(HeavySelect2Mixin, forms.TextInput):
    """
    Single selection heavy widget.

    Following Select2 option from :py:attr:`.Select2Mixin.options` is added or set:-

        * multiple: ``False``

    """

    def init_options(self):
        self.options['multiple'] = False

    @property
    def is_hidden(self):
        # we return false because even if input_type is 'hidden'
        # , the final field will be displayed by javascript
        # and we want label and other layout elements.
        return False

    def render_inner_js_code(self, id_, *args):
        field_id = self.field_id if hasattr(self, 'field_id') else id_
        fieldset_id = re.sub(r'-\d+-', '_', id_).replace('-', '_')
        if '__prefix__' in id_:
            return ''
        else:
            js = '''
                  window.django_select2.%s = function (selector, fieldID) {
                    var hashedSelector = "#" + selector;
                    $(hashedSelector).data("field_id", fieldID);
                  ''' % (fieldset_id)
            js += super(HeavySelect2Widget, self).render_inner_js_code(id_, *args)
            js += '};'
            js += 'django_select2.%s("%s", "%s");' % (fieldset_id, id_, field_id)
            return js


class HeavySelect2MultipleWidget(HeavySelect2Mixin, MultipleSelect2HiddenInput):
    """
    Multiple selection heavy widget.

    Following Select2 options from :py:attr:`.Select2Mixin.options` are removed:-

        * allowClear
        * minimumResultsForSearch

    Following Select2 options from :py:attr:`.Select2Mixin.options` are added or set:-

        * multiple: ``True``
        * separator: ``django_select2.MULTISEPARATOR``

    """

    def init_options(self):
        self.options['multiple'] = True
        self.options.pop('allowClear', None)
        self.options.pop('minimumResultsForSearch', None)
        self.options['separator'] = '*START*django_select2.MULTISEPARATOR*END*'

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
                return '$("#%s").txt(%s);' % (id_, texts)

    def render_inner_js_code(self, id_, *args):
        field_id = self.field_id if hasattr(self, 'field_id') else id_
        fieldset_id = re.sub(r'-\d+-', '_', id_).replace('-', '_')
        if '__prefix__' in id_:
            return ''
        else:
            js = '''
                  window.django_select2.%s = function (selector, fieldID) {
                    var hashedSelector = "#" + selector;
                    $(hashedSelector).data("field_id", fieldID);
                  ''' % (fieldset_id)
            js += super(HeavySelect2MultipleWidget, self).render_inner_js_code(id_, *args)
            js += '};'
            js += 'django_select2.%s("%s", "%s");' % (fieldset_id, id_, field_id)
            return js


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
        * separator: ``django_select2.MULTISEPARATOR``
        * tags: ``True``
        * tokenSeparators: ``,`` and `` ``
        * createSearchChoice: ``django_select2.createSearchChoice``
        * minimumInputLength: ``1``

    """
    def init_options(self):
        super(HeavySelect2TagWidget, self).init_options()
        self.options.pop('closeOnSelect', None)
        self.options['minimumInputLength'] = 1
        self.options['tags'] = True
        self.options['tokenSeparators'] = [",", " "]
        self.options['createSearchChoice'] = '*START*django_select2.createSearchChoice*END*'

    def render_inner_js_code(self, id_, *args):
        field_id = self.field_id if hasattr(self, 'field_id') else id_
        fieldset_id = re.sub(r'-\d+-', '_', id_).replace('-', '_')
        if '__prefix__' in id_:
            return ''
        else:
            js = '''
                  window.django_select2.%s = function (selector, fieldID) {
                    var hashedSelector = "#" + selector;
                    $(hashedSelector).data("field_id", fieldID);
                  ''' % (fieldset_id)
            js += super(HeavySelect2TagWidget, self).render_inner_js_code(id_, *args)
            js += '};'
            js += 'django_select2.%s("%s", "%s");' % (fieldset_id, id_, field_id)
            return js


# ## Auto Heavy widgets ##


class AutoHeavySelect2Mixin(object):
    """
    This mixin is needed for Auto heavy fields.

    This mixin adds extra JS code to notify the field's DOM object of the generated id. The generated id
    is not the same as the ``id`` attribute of the field's HTML markup. This id is generated by
    :py:func:`~.util.register_field` when the Auto field is registered. The client side (DOM) sends this
    id along with the Ajax request, so that the central view can identify which field should be used to
    serve the request.

    The js call to dynamically add the `django_select2` is as follows::

        django_select2.id_cities('id_cities', django_select2.id_cities_field_id);

    For an inline formset::

        django_select2.id_musician_set_name(
            'id_musician_set-0-name', django_select2.id_musician_set_name_field_id);
    """

    def __init__(self, *args, **kwargs):
        kwargs['data_view'] = "django_select2_central_json"
        super(AutoHeavySelect2Mixin, self).__init__(*args, **kwargs)

    def render_inner_js_code(self, id_, *args):
        fieldset_id = re.sub(r'-\d+-', '_', id_).replace('-', '_')
        if '__prefix__' in id_:
            return ''
        else:
            js = '''
                  window.django_select2.%s = function (selector, fieldID) {
                    var hashedSelector = "#" + selector;
                    $(hashedSelector).data("field_id", fieldID);
                  ''' % (fieldset_id)
            js += super(AutoHeavySelect2Mixin, self).render_inner_js_code(id_, *args)
            js += '};'
            js += 'django_select2.%s("%s", "%s");' % (fieldset_id, id_, self.field_id)
            return js


class AutoHeavySelect2Widget(AutoHeavySelect2Mixin, HeavySelect2Widget):
    """Auto version of :py:class:`.HeavySelect2Widget`"""
    pass


class AutoHeavySelect2MultipleWidget(AutoHeavySelect2Mixin, HeavySelect2MultipleWidget):
    """Auto version of :py:class:`.HeavySelect2MultipleWidget`"""
    pass


class AutoHeavySelect2TagWidget(AutoHeavySelect2Mixin, HeavySelect2TagWidget):
    """Auto version of :py:class:`.HeavySelect2TagWidget`"""
    pass
