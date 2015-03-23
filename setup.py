import codecs
import os
import sys

from distutils.util import convert_path
from fnmatch import fnmatchcase
from setuptools import setup, find_packages


def read(fname):
    return codecs.open(os.path.join(os.path.dirname(__file__), fname), 'rb').read()


# Provided as an attribute, so you can append to these instead
# of replicating them:
standard_exclude = ["*.py", "*.pyc", "*$py.class", "*~", ".*", "*.bak"]
standard_exclude_directories = [
    ".*", "CVS", "_darcs", "./build", "./dist", "EGG-INFO", "*.egg-info"
]


# (c) 2005 Ian Bicking and contributors; written for Paste (http://pythonpaste.org)
# Licensed under the MIT license: http://www.opensource.org/licenses/mit-license.php
# Note: you may want to copy this into your setup.py file verbatim, as
# you can't import this from another package, when you don't know if
# that package is installed yet.
def find_package_data(
    where=".",
    package="",
    exclude=standard_exclude,
    exclude_directories=standard_exclude_directories,
    only_in_packages=True,
    show_ignored=False):
    """
    Return a dictionary suitable for use in ``package_data``
    in a distutils ``setup.py`` file.

    The dictionary looks like::

        {"package": [files]}

    Where ``files`` is a list of all the files in that package that
    don"t match anything in ``exclude``.

    If ``only_in_packages`` is true, then top-level directories that
    are not packages won"t be included (but directories under packages
    will).

    Directories matching any pattern in ``exclude_directories`` will
    be ignored; by default directories with leading ``.``, ``CVS``,
    and ``_darcs`` will be ignored.

    If ``show_ignored`` is true, then all the files that aren"t
    included in package data are shown on stderr (for debugging
    purposes).

    Note patterns use wildcards, or can be exact paths (including
    leading ``./``), and all searching is case-insensitive.
    """
    out = {}
    stack = [(convert_path(where), "", package, only_in_packages)]
    while stack:
        where, prefix, package, only_in_packages = stack.pop(0)
        for name in os.listdir(where):
            fn = os.path.join(where, name)
            if os.path.isdir(fn):
                bad_name = False
                for pattern in exclude_directories:
                    if (fnmatchcase(name, pattern)
                        or fn.lower() == pattern.lower()):
                        bad_name = True
                        if show_ignored:
                            print((
                                "Directory %s ignored by pattern %s"
                                % (fn, pattern)), file=sys.stderr)
                        break
                if bad_name:
                    continue
                if (os.path.isfile(os.path.join(fn, "__init__.py"))
                    and not prefix):
                    if not package:
                        new_package = name
                    else:
                        new_package = package + "." + name
                    stack.append((fn, "", new_package, False))
                else:
                    stack.append((fn, prefix + name + "/", package, only_in_packages))
            elif package or not only_in_packages:
                # is a file
                bad_name = False
                for pattern in exclude:
                    if (fnmatchcase(name, pattern)
                        or fn.lower() == pattern.lower()):
                        bad_name = True
                        if show_ignored:
                            print((
                                "File %s ignored by pattern %s"
                                % (fn, pattern)), file=sys.stderr)
                        break
                if bad_name:
                    continue
                out.setdefault(package, []).append(prefix+name)
    return out

PACKAGE = "django_select2"
NAME = "Django-Select2-Py3"
DESCRIPTION = "Select2 option fields for Django for Python3"
AUTHOR = "Nirupam Biswas, Nicolas Pantel"
AUTHOR_EMAIL = "admin@applegrew.com"
URL = "https://github.com/applegrew/django-select2"
VERSION = __import__(PACKAGE).__version__

def getPkgPath():
    return __import__(PACKAGE).__path__[0] + '/'

def minify(files, outfile, ftype):
    import urllib.request, urllib.parse, urllib.error, json

    content = ''
    for filename in files:
        with open(getPkgPath() + filename) as f:
            for line in f:
                content = content + line

    data = urllib.parse.urlencode([
        ('code', content.encode('utf-8')),
        ('type', ftype),
      ])

    f = urllib.request.urlopen('http://api.applegrew.com/minify', bytes(data, encoding='utf-8'))
    data = ''
    while 1:
        line = f.readline()
        if line:
            if isinstance(line, bytes):
                line = line.decode('utf-8')
            data = data + line
        else:
            break
    f.close()

    data = json.loads(data)
    for key in data:
        value = data[key]
        #if isinstance(value, str):
        #    value = value.decode('utf-8')

    if data['success']:
        with open(getPkgPath() + outfile, 'w') as f:
            f.write(data['compiled_code'])
    else:
        print(data['error_code'])
        print(data['error'])
        raise Exception('Could not minify.')

if len(sys.argv) > 1 and 'sdist' == sys.argv[1]:
    minify(['static/js/select2.js'], 'static/js/select2.min.js', 'js')
    minify(['static/js/heavy_data.js'], 'static/js/heavy_data.min.js', 'js')
    minify(['static/css/select2.css'], 'static/css/select2.min.css', 'css')
    minify(['static/css/select2.css', 'static/css/extra.css'], 'static/css/all.min.css', 'css')

setup(
    name=NAME,
    version=VERSION,
    description=DESCRIPTION,
    long_description=read("README.md").decode('utf-8'),
    author=AUTHOR,
    author_email=AUTHOR_EMAIL,
    license="LICENSE.txt",
    url=URL,
    packages=[PACKAGE, PACKAGE + '.templatetags'],
    package_data=find_package_data(),
    exclude_package_data={ '': standard_exclude },
    include_package_data=True,
    classifiers=[
        "Development Status :: 4 - Beta",
        "Environment :: Web Environment",
        "Intended Audience :: Developers",
        "License :: OSI Approved :: Apache Software License",
        "Operating System :: OS Independent",
        "Programming Language :: Python",
        "Framework :: Django",
    ],
    install_requires=[
        "Django>=1.5",
    ],
)
