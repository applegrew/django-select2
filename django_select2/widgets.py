import types

from django import forms
from django.utils.safestring import mark_safe
from django.core.urlresolvers import reverse

class JSFunction(str):
    """
    Flags that the string is the name of a JS function. Used by Select2Mixin.render_options()
    to make sure that this string is not quoted like other strings.
    """
    pass

class JSFunctionInContext(str):
    """
    Like JSFunction, this too flags the string as JS function, but with a special requirement.
    The JS function needs to be invoked in the context of the current Select2 Html DOM,
    such that 'this' inside the function refers to the source Select2 DOM.
    """
    pass

class Select2Mixin(object):
    # For details on these options refer: http://ivaynberg.github.com/select2/#documentation
    options = {
        'minimumResultsForSearch': 6, # Only applicable for single value select.
        'placeholder': '',
        'allowClear': True, # Not allowed when field is multiple since there each value has a clear button.
        'multiple': False, # Not allowed when attached to <select>
        'closeOnSelect': False
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

    def get_options(self):
        options = dict(self.options)
        if options.get('allowClear', None) is not None:
            options['allowClear'] = not self.is_required
        return options

    def render_options_code(self, options, id_):
        out = '{'
        is_first = True
        for name in options:
            if not is_first:
                out += ", "
            else:
                is_first = False

            out += "'%s': " % name
            val = options[name]
            if type(val) == types.BooleanType:
                out += 'true' if val else 'false'
            elif type(val) in [types.IntType, types.LongType, types.FloatType]:
                out += str(val)
            elif isinstance(val, JSFunctionInContext):
                out += """function () {
                        var args = Array.prototype.slice.call(arguments);
                        return %s.apply($('#%s').get(0), args);
                    }""" % (val, id_)
            elif isinstance(val, JSFunction):
                out += val # No quotes here
            elif isinstance(val, dict):
                out += self.render_options_code(val, id_)
            else:
                out += "'%s'" % val

        return out + '}'

    def render_js_code(self, id_):
        if id_:
            return u"""
            <script>
                $(function () {
                    %s
                });
            </script>""" % self.render_inner_js_code(id_);
        return u''

    def render_inner_js_code(self, id_):
        options = dict(self.get_options())
        options = self.render_options_code(options, id_)

        return '$("#%s").select2(%s);' % (id_, options)

    def render(self, name, value, attrs=None):
        s = str(super(Select2Mixin, self).render(name, value, attrs))
        s += self.media.render()
        final_attrs = self.build_attrs(attrs)
        id_ = final_attrs.get('id', None)
        s += self.render_js_code(id_)
        return mark_safe(s)

    class Media:
        js = ('js/select2.min.js', )
        css = {'screen': ('css/select2.css', 'css/extra.css', )}

class HeavySelect2Mixin(Select2Mixin):
    def __init__(self, **kwargs):
        self.options = dict(self.options) # Making an instance specific copy
        self.view = kwargs.pop('data_view', None)
        self.url = kwargs.pop('data_url', None)
        if not self.view and not self.url:
            raise ValueError('data_view or data_url is required')
        self.url = None
        self.options['ajax'] = {
            'dataType': 'json',
            'quietMillis': 100,
            'data': JSFunctionInContext('django_select2.get_url_params'),
            'results': JSFunctionInContext('django_select2.process_results'),
        }
        self.options['minimumInputLength'] = 2
        self.options['initSelection'] = JSFunction('django_select2.onInit')
        super(HeavySelect2Mixin, self).__init__(**kwargs)

    def get_options(self):
        if self.url is None:
            self.url = reverse(self.view) # We lazy resolve the view. By this time Url conf would been loaded fully.
        if self.options['ajax'].get('url', None) is None:
            self.options['ajax']['url'] = self.url
        return super(HeavySelect2Mixin, self).get_options()

    def render_inner_js_code(self, id_):
        js = super(HeavySelect2Mixin, self).render_inner_js_code(id_)
        js += "$('#%s').change(django_select2.onValChange);" % id_
        return js

    class Media:
        js = ('js/select2.min.js', 'js/heavy_data.js', )
        css = {'screen': ('css/select2.css', 'css/extra.css', )}

class AutoHeavySelect2Mixin(HeavySelect2Mixin):
    def render_inner_js_code(self, id_):
        js = super(AutoHeavySelect2Mixin, self).render_inner_js_code(id_)
        js += "$('#%s').data('field_id', '%s');" % (id_, self.field_id)
        return js

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

class HeavySelect2Widget(HeavySelect2Mixin, forms.TextInput):
    input_type = 'hidden' # We want it hidden but should be treated as if is_hidden is False
    def init_options(self):
        self.options['multiple'] = False

class HeavySelect2MultipleWidget(HeavySelect2Mixin, forms.TextInput):
    input_type = 'hidden' # We want it hidden but should be treated as if is_hidden is False
    def init_options(self):
        self.options['multiple'] = True
        self.options.pop('allowClear', None)
        self.options.pop('minimumResultsForSearch', None)

class AutoHeavySelect2Widget(AutoHeavySelect2Mixin, HeavySelect2Widget):
    pass
