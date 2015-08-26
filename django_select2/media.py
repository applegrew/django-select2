from django.conf import settings
from django.contrib.staticfiles.templatetags.staticfiles import static

from . import __BOOTSTRAP as BOOTSTRAP

# Local version of DEBUG
DEBUG = settings.configured and settings.DEBUG


def django_select2_static(file):
    return static('django_select2/' + file)


def get_select2_js_libs():
    if DEBUG:
        js_file = 'js/select2.js'
    else:
        js_file = 'js/select2.min.js'
    return (django_select2_static(js_file), )


def get_select2_heavy_js_libs():
    libs = get_select2_js_libs()

    if DEBUG:
        js_file = 'js/heavy_data.js'
    else:
        js_file = 'js/heavy_data.min.js'
    return libs + (django_select2_static(js_file), )


def get_select2_css_libs(light=False):
    css_files = []
    if BOOTSTRAP:
        if DEBUG:
            if light:
                css_files = ('css/select2.css', 'css/select2-bootstrap.css', )
            else:
                css_files = ('css/select2.css', 'css/extra.css', 'css/select2-bootstrap.css')
        else:
            if light:
                css_files = ('css/select2-bootstrapped.min.css',)
            else:
                css_files = ('css/all-bootstrapped.min.css',)
    else:
        if settings.configured and settings.DEBUG:
            if light:
                css_files = ('css/select2.css',)
            else:
                css_files = ('css/select2.css', 'css/extra.css')
        else:
            if light:
                css_files = ('css/select2.min.css',)
            else:
                css_files = ('css/all.min.css',)
    return [django_select2_static(f) for f in css_files]
