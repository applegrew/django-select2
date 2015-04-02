# -*- coding:utf-8 -*-
from __future__ import absolute_import, unicode_literals

from django import template

from django_select2.media import (get_select2_css_libs,
                                  get_select2_heavy_js_libs,
                                  get_select2_js_libs)

register = template.Library()


def link_tag(css_file):
    return '<link href="{file}" rel="stylesheet">'.format(file=css_file)


def script_tag(script_file):
    return '<script type="text/javascript" src="{file}"></script>'.format(file=script_file)


@register.simple_tag(name='import_django_select2_js')
def import_js(light=0):
    if light:
        js_files = get_select2_js_libs()
    else:
        js_files = get_select2_heavy_js_libs()
    return '\n'.join(script_tag(js_file) for js_file in js_files)


@register.simple_tag(name='import_django_select2_css')
def import_css(light=0):
    return '\n'.join(link_tag(css_file) for css_file in get_select2_css_libs(light=light))


@register.simple_tag(name='import_django_select2_js_css')
def import_all(light=0):
    return import_css(light=light) + import_js(light=light)
