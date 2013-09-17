from django import template

register = template.Library()

from ..widgets import HeavySelect2Widget, Select2Widget

__proxy_widget = HeavySelect2Widget(data_view="xyz")
__proxy_light_widget = Select2Widget()


@register.simple_tag(name='import_django_select2_js')
def import_js(light=0):
	if light:
		return u'\n'.join(__proxy_light_widget.media.render_js())
	else:
	    return u'\n'.join(__proxy_widget.media.render_js())


@register.simple_tag(name='import_django_select2_css')
def import_css(light=0):
	if light:
		return u'\n'.join(__proxy_light_widget.media.render_css())
	else:
	    return u'\n'.join(__proxy_widget.media.render_css())


@register.simple_tag(name='import_django_select2_js_css')
def import_all(light=0):
	if light:
		return __proxy_light_widget.media.render()
	else:
	    return __proxy_widget.media.render()
