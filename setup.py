#!/usr/bin/env python
# -*- coding: utf-8 -*-
from __future__ import unicode_literals

import codecs
import os
import sys

from setuptools import setup, find_packages, Command


def read(fname):
    f = codecs.open(os.path.join(os.path.dirname(__file__), fname), 'rb')
    return f.read()


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
    import urllib
    import json

    content = u''
    for filename in files:
        with open(getPkgPath() + filename) as f:
            for line in f.xreadlines():
                if isinstance(line, str):
                    line = line.decode('utf-8')
                content = content + line

    data = urllib.urlencode([
        ('code', content.encode('utf-8')),
        ('type', ftype),
    ])

    f = urllib.urlopen('http://api.applegrew.com/minify', data)
    data = u''
    while 1:
        line = f.readline()
        if line:
            if isinstance(line, str):
                line = line.decode('utf-8')
            data = data + line
        else:
            break
    f.close()

    data = json.loads(data)
    if data['success']:
        with open(getPkgPath() + outfile, 'w') as f:
            f.write(data['compiled_code'].encode('utf8'))
    else:
        print data['error_code']
        print data['error']
        raise Exception('Could not minify.')


if len(sys.argv) > 1 and 'sdist' == sys.argv[1]:
    minify(['static/js/select2.js'], 'static/js/select2.min.js', 'js')
    minify(['static/js/heavy_data.js'], 'static/js/heavy_data.min.js', 'js')
    minify(['static/css/select2.css'], 'static/css/select2.min.css', 'css')
    minify(['static/css/select2.css', 'static/css/extra.css'],
           'static/css/all.min.css', 'css')
    minify(['static/css/select2.css', 'static/css/select2-bootstrap.css'],
           'static/css/select2-bootstrapped.min.css', 'css')
    minify(
        [
            'static/css/select2.css',
            'static/css/extra.css',
            'static/css/select2-bootstrap.css'
        ], 'static/css/all-bootstrapped.min.css', 'css')


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
    packages=find_packages(exclude=['tests']),
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
        "Django>=1.4",
    ],
    zip_safe=False,
    cmdclass={'test': PyTest},
)
