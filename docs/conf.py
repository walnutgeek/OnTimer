import os
import sys
sys.path.insert(0, os.path.abspath(".."))
import ontimer

master_doc = "index"

project = "OnTimer"

author = "WalnutGeek.org"
copyright = "2014, " + author

version = release = ontimer.__version__

extensions = [
    "sphinx.ext.autodoc",
    "sphinx.ext.coverage",
    "sphinx.ext.extlinks",
    "sphinx.ext.intersphinx",
    "sphinx.ext.viewcode",
    ]

primary_domain = 'py'
default_role = 'py:obj'

autodoc_member_order = "bysource"
autoclass_content = "both"

# Without this line sphinx includes a copy of object.__init__'s docstring
# on any class that doesn't define __init__.
# https://bitbucket.org/birkenfeld/sphinx/issue/1337/autoclass_content-both-uses-object__init__
autodoc_docstring_signature = False

coverage_skip_undoc_in_source = True
coverage_ignore_modules = [
]

# I wish this could go in a per-module file...
coverage_ignore_classes = [
]

coverage_ignore_functions = [
    "doctests",
    "main",
]

#html_favicon = 'favicon.ico'

latex_documents = [
    ('documentation', project + '.tex',  project +' Documentation', author, 'manual', False),
    ]

# HACK: sphinx has limited support for substitutions with the |version|
# variable, but there doesn't appear to be any way to use this in a link
# target.
# http://stackoverflow.com/questions/1227037/substitutions-inside-links-in-rest-sphinx
# The extlink extension can be used to do link substitutions, but it requires a
# portion of the url to be literally contained in the document.  Therefore,
# this link must be referenced as :current_tarball:`z`
extlinks = {
    'current_tarball': ( 'https://pypi.python.org/packages/source/t/{0}/{0}-{1}.tar.g%s'
                                .format( project.lower(), version ),
        '{0}-{1}.tar.g'.format( project.lower(), version) ),
    }

intersphinx_mapping = {
     'python': ('http://python.readthedocs.org/en/latest/', None),
    }

on_rtd = os.environ.get('READTHEDOCS', None) == 'True'

# On RTD we can't import sphinx_rtd_theme, but it will be applied by
# default anyway.  This block will use the same theme when building locally
# as on RTD.
if not on_rtd:
    import sphinx_rtd_theme
    html_theme = 'sphinx_rtd_theme'
    html_theme_path = [sphinx_rtd_theme.get_html_theme_path()]
