#!/usr/bin/env python
# -*- coding: utf-8 -*-
from __future__ import unicode_literals

import codecs
import os
import sys

from setuptools import Command, find_packages, setup


def read(file_name):
    file_path = os.path.join(os.path.dirname(__file__), file_name)
    return codecs.open(file_path, encoding='utf-8').read()


PACKAGE = "django_select2"
NAME = "Django-Select2"
DESCRIPTION = "Select2 option fields for Django"
AUTHOR = "Nirupam Biswas"
AUTHOR_EMAIL = "admin@applegrew.com"
URL = "https://github.com/applegrew/django-select2"
VERSION = __import__(PACKAGE).__version__


def getPkgPath():
    return __import__(PACKAGE).__path__[0] + '/'


def minify(files, outfile, ftype):
    import requests
    import io

    content = ''

    for filename in files:
        with io.open(getPkgPath() + filename, 'r', encoding='utf8') as f:
            content = content + '\n' + f.read()

    data = {
        'code': content,
        'type': ftype,
    }
    response = requests.post('http://api.applegrew.com/minify', data)
    response.raise_for_status()
    response = response.json()
    if response['success']:
        with io.open(getPkgPath() + outfile, 'w', encoding='utf8') as f:
            f.write(response['compiled_code'])
    else:
        raise Exception('%(error_code)s: "%(error)s"' % response)


if len(sys.argv) > 1 and 'sdist' == sys.argv[1]:
    minify(['static/django_select2/js/select2.js'], 'static/django_select2/js/select2.min.js', 'js')
    minify(['static/django_select2/js/heavy_data.js'], 'static/django_select2/js/heavy_data.min.js', 'js')
    minify(['static/django_select2/css/select2.css'], 'static/django_select2/css/select2.min.css', 'css')
    minify(['static/django_select2/css/select2.css', 'static/django_select2/css/extra.css'],
           'static/django_select2/css/all.min.css', 'css')
    minify(['static/django_select2/css/select2.css', 'static/django_select2/css/select2-bootstrap.css'],
           'static/django_select2/css/select2-bootstrapped.min.css', 'css')
    minify(
        [
            'static/django_select2/css/select2.css',
            'static/django_select2/css/extra.css',
            'static/django_select2/css/select2-bootstrap.css'
        ], 'static/django_select2/css/all-bootstrapped.min.css', 'css')


class PyTest(Command):
    user_options = []

    def initialize_options(self):
        pass

    def finalize_options(self):
        pass

    def run(self):
        import sys
        import subprocess

        errno = subprocess.call([sys.executable, 'runtests.py'])
        raise SystemExit(errno)


setup(
    name=NAME,
    version=VERSION,
    description=DESCRIPTION,
    long_description=read("README.md"),
    author=AUTHOR,
    author_email=AUTHOR_EMAIL,
    license="LICENSE.txt",
    url=URL,
    packages=find_packages(),
    include_package_data=True,
    classifiers=[
        "Development Status :: 5 - Production/Stable",
        "Environment :: Web Environment",
        "Intended Audience :: Developers",
        "License :: OSI Approved :: Apache Software License",
        "Operating System :: OS Independent",
        "Programming Language :: Python",
        "Framework :: Django",
    ],
    install_requires=[
        'django-appconf>=0.6.0',
    ],
    zip_safe=False,
    cmdclass={'test': PyTest},
)
