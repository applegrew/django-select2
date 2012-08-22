import logging
from itertools import chain

from django import forms
from django.utils.encoding import force_unicode
from django.utils.safestring import mark_safe
from django.core.urlresolvers import reverse
from django.utils.datastructures import MultiValueDict, MergeDict

from .util import render_js_script, convert_to_js_string_arr, JSVar, JSFunction, JSFunctionInContext, \
    convert_dict_to_js_map, convert_to_js_arr

logger = logging.getLogger(__name__)

### Light mixin and widgets ###

class Select2Mixin(object):
    # For details on these options refer: http://ivaynberg.github.com/select2/#documentation
    options = {
        'minimumResultsForSearch': 6, # Only applicable for single value select.
        'placeholder': '', # Empty text label
        'allowClear': True, # Not allowed when field is multiple since there each value has a clear button.
        'multiple': False, # Not allowed when attached to <select>
        'closeOnSelect': False,
    }

    def __init__(self, **kwargs):
        self.options = dict(self.options) # Making an instance specific copy
        self.init_options()
        attrs = kwargs.pop('attrs', None)
        if attrs:
            for name in self.options:
                val = self.options[name]
                self.options[name] = attrs.pop(name, val)
            kwargs['attrs'] = attrs

        super(Select2Mixin, self).__init__(**kwargs)

    def init_options(self):
        pass

    def set_placeholder(self, val):
        self.options['placeholder'] = val

    def get_options(self):
        options = dict(self.options)
        if options.get('allowClear', None) is not None:
            options['allowClear'] = not self.is_required
        return options

    def render_select2_options_code(self, options, id_):
        return convert_dict_to_js_map(options, id_)

    def render_js_code(self, id_, *args):
        if id_:
            return render_js_script(self.render_inner_js_code(id_, *args))
        return u''

    def render_inner_js_code(self, id_, *args):
        options = dict(self.get_options())
        options = self.render_select2_options_code(options, id_)

        return u'$("#%s").select2(%s);' % (id_, options)

    def render(self, name, value, attrs=None, choices=()):
        args = [name, value, attrs]
        if choices: args.append(choices)

        s = unicode(super(Select2Mixin, self).render(*args)) # Thanks to @ouhouhsami Issue#1
        s += self.media.render()
        final_attrs = self.build_attrs(attrs)
        id_ = final_attrs.get('id', None)
        s += self.render_js_code(id_, name, value, attrs, choices)

        if logger.isEnabledFor(logging.DEBUG):
            logger.debug("Generated widget code:-\n%s", s)

        return mark_safe(s)

    class Media:
        js = ('js/select2.min.js', )
        css = {'screen': ('css/select2.css', 'css/extra.css', )}

class Select2Widget(Select2Mixin, forms.Select):
    def init_options(self):
        self.options.pop('multiple', None)

    def render_options(self, choices, selected_choices):
        if not self.is_required:
            choices = list(choices)
            choices.append(('', '', )) # Adding an empty choice
        return super(Select2Widget, self).render_options(choices, selected_choices)

class Select2MultipleWidget(Select2Mixin, forms.SelectMultiple):
    def init_options(self):
        self.options.pop('multiple', None)
        self.options.pop('allowClear', None)
        self.options.pop('minimumResultsForSearch', None)

### Specialized Multiple Hidden Input Widget ###
class MultipleSelect2HiddenInput(forms.TextInput):
    """
    This is a specialized multiple Hidden Input widget. This includes a special
    JS component which renders multiple Hidden Input boxes as there are values.
    So, if user suppose chooses values 1,4,9 then Select2 would would write them
    to the hidden input. The JS component of this widget will read that value and
    will render three more hidden input boxes each with values 1, 4 and 9 respectively.
    They will all share the name of this field, and the name of the primary source
    hidden input would be removed. This way, when submitted all the selected values
    would be available was would have been for a <select> multiple field.
    """
    input_type = 'hidden' # We want it hidden but should be treated as if is_hidden is False
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
        return s

    def value_from_datadict(self, data, files, name):
        if isinstance(data, (MultiValueDict, MergeDict)):
            return data.getlist(name)
        return data.get(name, None)

### Heavy mixins and widgets ###

class HeavySelect2Mixin(Select2Mixin):
    def __init__(self, **kwargs):
        self.options = dict(self.options) # Making an instance specific copy
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
        selected_choices = list(force_unicode(v) for v in selected_choices)
        txts = []
        all_choices = choices if choices else []
        for val, txt in chain(self.choices, all_choices):
            val = force_unicode(val)
            if val in selected_choices:
                txts.append(txt)
        if txts:
            return convert_to_js_string_arr(txts)

    def get_options(self):
        if self.url is None:
            self.url = reverse(self.view) # We lazy resolve the view. By this time Url conf would been loaded fully.
        if self.options['ajax'].get('url', None) is None:
            self.options['ajax']['url'] = self.url
        return super(HeavySelect2Mixin, self).get_options()

    def render_texts_for_value(self, id_, value, choices):
        if value is not None:
            values = [value] # Just like forms.Select.render() it assumes that value will be single valued.
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
        js = ('js/select2.min.js', 'js/heavy_data.js', )
        css = {'screen': ('css/select2.css', 'css/extra.css', )}

class HeavySelect2Widget(HeavySelect2Mixin, forms.TextInput):
    input_type = 'hidden' # We want it hidden but should be treated as if is_hidden is False
    def init_options(self):
        self.options['multiple'] = False

class HeavySelect2MultipleWidget(HeavySelect2Mixin, MultipleSelect2HiddenInput):
    def init_options(self):
        self.options['multiple'] = True
        self.options.pop('allowClear', None)
        self.options.pop('minimumResultsForSearch', None)
        self.options['separator'] = JSVar('django_select2.MULTISEPARATOR')

    def render_texts_for_value(self, id_, value, choices): # value is expected to be a list of values
        if value: # Just like forms.SelectMultiple.render() it assumes that value will be multi-valued (list).
            texts = self.render_texts(value, choices)
            if texts:
                return u"$('#%s').txt(%s);" % (id_, texts)

### Auto Heavy widgets ###

class AutoHeavySelect2Mixin(object):
    def render_inner_js_code(self, id_, *args):
        js = u"$('#%s').data('field_id', '%s');" % (id_, self.field_id)
        js += super(AutoHeavySelect2Mixin, self).render_inner_js_code(id_, *args)
        return js

class AutoHeavySelect2Widget(AutoHeavySelect2Mixin, HeavySelect2Widget):
    pass

class AutoHeavySelect2MultipleWidget(AutoHeavySelect2Mixin, HeavySelect2MultipleWidget):
    pass
