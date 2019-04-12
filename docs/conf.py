import os
import sys

from pkg_resources import get_distribution

# This is needed since django_select2 requires django model modules
# and those modules assume that django settings is configured and
# have proper DB settings.
# Using this we give a proper environment with working django settings.
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "tests.testapp.settings")

# If extensions (or modules to document with autodoc) are in another directory,
# add these directories to sys.path here. If the directory is relative to the
# documentation root, use os.path.abspath to make it absolute, like shown here.
sys.path.insert(0, os.path.abspath('../tests.testapp'))
sys.path.insert(0, os.path.abspath('..'))


project = "Django-Select2"
author = "Johannes Hoppe"
copyright = "2017, Johannes Hoppe"
release = get_distribution('django_select2').version
version = '.'.join(release.split('.')[:2])


master_doc = 'index'  # default in Sphinx v2


extensions = [
    'sphinx.ext.autodoc',
    'sphinx.ext.napoleon',
    'sphinx.ext.inheritance_diagram',
    'sphinx.ext.intersphinx',
    'sphinx.ext.viewcode',
    'sphinx.ext.doctest',
]

intersphinx_mapping = {
    'python': ('http://docs.python.org/3', None),
    'django': ('https://docs.djangoproject.com/en/stable/',
               'https://docs.djangoproject.com/en/stable/_objects/'),
}

autodoc_default_flags = ['members', 'show-inheritance']
autodoc_member_order = 'bysource'

inheritance_graph_attrs = dict(rankdir='TB')

inheritance_node_attrs = dict(shape='rect', fontsize=14, fillcolor='gray90',
                              color='gray30', style='filled')

inheritance_edge_attrs = dict(penwidth=0.75)
