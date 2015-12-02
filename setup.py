#!/usr/bin/env python
# -*- coding: utf-8 -*-
from __future__ import unicode_literals

import codecs
import os

from setuptools import Command, find_packages, setup


def read(file_name):
    file_path = os.path.join(os.path.dirname(__file__), file_name)
    return codecs.open(file_path, encoding='utf-8').read()


PACKAGE = "django_select2"
NAME = "Django-Select2"
DESCRIPTION = "Select2 option fields for Django"
AUTHOR = "Nirupam Biswas, Johannes Hoppe"
AUTHOR_EMAIL = "admin@applegrew.com"
URL = "https://github.com/applegrew/django-select2"
VERSION = __import__(PACKAGE).__version__


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
        "Programming Language :: Python :: 2",
        "Programming Language :: Python :: 3",
        "Framework :: Django",
        "Framework :: Django :: 1.8",
        "Framework :: Django :: 1.9",
    ],
    install_requires=[
        'django-appconf>=0.6.0',
    ],
    zip_safe=False,
)
