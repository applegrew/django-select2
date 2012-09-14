from django import template
from django.conf import settings

register = template.Library()

from ..widgets import HeavySelect2Widget

__proxy_widget = HeavySelect2Widget(data_view="xyz")

@register.simple_tag(name='import_django_select2_js')
def import_js():
    return u'\n'.join(__proxy_widget.media.render_js())

@register.simple_tag(name='import_django_select2_css')
def import_css():
    return u'\n'.join(__proxy_widget.media.render_css())

@register.simple_tag(name='import_django_select2_js_css')
def import_all():
    return __proxy_widget.media.render()
