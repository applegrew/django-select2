import datetime
import os
import sys

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

extensions = [
    'sphinx.ext.autodoc',
    'sphinx.ext.napoleon',
    'sphinx.ext.inheritance_diagram',
    'sphinx.ext.intersphinx',
    'sphinx.ext.viewcode',
    'sphinxcontrib.spelling',
]

intersphinx_mapping = {
    'python': ('http://docs.python.org/3', None),
    'django': ('https://docs.djangoproject.com/en/stable/',
               'https://docs.djangoproject.com/en/stable/_objects/'),
}

# spell check
spelling_word_list_filename = 'spelling_wordlist.txt'
spelling_show_suggestions = True

master_doc = 'index'

# General information about the project.
project = 'django-select2'
year = datetime.datetime.now().strftime("%Y")
copyright = '%s, Johannes Hoppe' % year

autodoc_default_flags = ['members', 'show-inheritance']
autodoc_member_order = 'bysource'

inheritance_graph_attrs = dict(rankdir='TB')

inheritance_node_attrs = dict(shape='rect', fontsize=14, fillcolor='gray90',
                              color='gray30', style='filled')

inheritance_edge_attrs = dict(penwidth=0.75)

html_theme = 'sphinx_rtd_theme'
