from django import template
from django.conf import settings

register = template.Library()

class ToolbarBtn(object):
    text = ''
    _btn_type = 'normal'
    btn_type = property(lambda s: s._btn_type)
    @btn_type.setter
    def btn_type(self, val):
        if val not in ['normal', 'warn', 'info', 'success', 'primary', 'inverse', 'danger']:
            raise ValueError('Invalid btn_type %s' % str(val))
        self._btn_type = val

    action = ''
    is_js_function_name = False # if True the action is JS function name,
                                # which will be registered as click handler of the button,
                                # else action is a url to invoke.

    def __init__(self, text, action, is_js_function_name=False, btn_type='normal'):
        self.text = text
        self.action = action
        self.is_js_function_name = is_js_function_name
        self.btn_type = btn_type

    def get_css_classes(self):
        if self.btn_type == 'warn':
            return 'btn-warning'
        elif self.btn_type == 'info':
            return 'btn-info'
        elif self.btn_type == 'success':
            return 'btn-success'
        elif self.btn_type == 'primary':
            return 'btn-primary'
        elif self.btn_type == 'inverse':
            return 'btn-inverse'
        elif self.btn_type == 'danger':
            return 'btn-danger'
        return ''

    def additional_attrs(self):
        return 'js_click="%s"' % self.action if self.is_js_function_name else ''

    def get_href(self):
        return '#' if self.is_js_function_name else self.action

    def get_text(self):
        return self.text

    def as_html(self):
        return "<a class='btn %s' href='%s' %s>%s</a>" % (self.get_css_classes(), self.get_href(),
            self.additional_attrs(), self.get_text())

class ToolbarDropdownBtn(ToolbarBtn):
    action = '#' # Should always be #
    texts_actions = []

    def __init__(self, text, texts_actions, is_js_function_name=False, btn_type='normal'):
        self.text = text
        self.action = "#"
        self.is_js_function_name = is_js_function_name
        self.btn_type = btn_type
        self.texts_actions = texts_actions

    def get_css_classes(self):
        return super(ToolbarDropdownBtn, self).get_css_classes() + ' dropdown-toggle'

    def additional_attrs(self):
        return 'data-toggle="dropdown"'

    def get_text(self):
        return self.text + '<span class="caret"></span>'

    def as_html(self):
        html = ("""
            <div class="btn-group">
                %s
                <ul class="dropdown-menu">
            """
            %
            super(ToolbarDropdownBtn, self).as_html())

        for text, action in self.texts_actions:
            html += "<li><a href='%s' %s>%s</a></li>" % ('#' if self.is_js_function_name else action,
                'js_click="%s"' % action if self.is_js_function_name else '', text)

        html += """
                </ul>
            </div>"""

        return html


class ToolbarNode(template.Node):
    def get_list_html(self, val):
        html = ''
        for e in val:
            if isinstance(e, ToolbarBtn):
                html += e.as_html()
            elif isinstance(e, list):
                html += '<div class="btn-group">%s</div>' % self.get_list_html(e)
            else:
                ValueError('Invalid item %s in the list.' % str(e))

        return html

    def __init__(self, valName):
        self.valName = valName

    def render(self, context):
        val = context[self.valName]
        if val:
            return '<div class="btn-group">%s</div>' % self.get_list_html(val)
        else:
            return ''

@register.tag(name="render_toolbar_btns")
def do_render_toolbar_btns(parser, token):
    try:
        # split_contents() knows not to split quoted strings.
        tag_name, valName = token.split_contents()
    except ValueError:
        raise template.TemplateSyntaxError("%r tag requires a single argument" % token.contents.split()[0])

    return ToolbarNode(valName)
