# Configuration file for the Sphinx documentation builder.
#
# This file only contains a selection of the most common options. For a full
# list see the documentation:
# https://www.sphinx-doc.org/en/master/usage/configuration.html

# -- Path setup --------------------------------------------------------------

# If extensions (or modules to document with autodoc) are in another directory,
# add these directories to sys.path here. If the directory is relative to the
# documentation root, use os.path.abspath to make it absolute, like shown here.
#
import os
import sys
sys.path.insert(0, os.path.abspath('..'))


def get_version(filename='../geomodels/__init__.py', strip_extra=False):
    import re
    from distutils.version import LooseVersion

    data = open(filename).read()
    mobj = re.search(
        r'''^__version__\s*=\s*(?P<quote>['"])(?P<version>.*)(?P=quote)''',
        data, re.MULTILINE)
    version = LooseVersion(mobj.group('version'))

    if strip_extra:
        return '.'.join(map(str, version.version[:3]))
    else:
        return version.vstring


# -- Project information -----------------------------------------------------

project = 'GeoModels'
copyright = '2019-2020, Antonio Valentino'
author = 'Antonio Valentino'

# The short X.Y version.
version = get_version(strip_extra=True)

# The full version, including alpha/beta/rc tags
release = get_version(strip_extra=False)


# -- General configuration ---------------------------------------------------

# Add any Sphinx extension module names here, as strings. They can be
# extensions coming with Sphinx (named 'sphinx.ext.*') or your custom
# ones.
extensions = [
    'sphinx.ext.autodoc',
    'sphinx.ext.autosummary',
    'sphinx.ext.doctest',
    'sphinx.ext.intersphinx',
    'sphinx.ext.todo',
    'sphinx.ext.imgmath',
    'sphinx.ext.ifconfig',
    'sphinx.ext.viewcode',
    'sphinx.ext.extlinks',
]

# Add any paths that contain templates here, relative to this directory.
templates_path = ['_templates']

# The master toctree document.
master_doc = 'index'

# List of patterns, relative to source directory, that match files and
# directories to ignore when looking for source files.
# This pattern also affects html_static_path and html_extra_path.
exclude_patterns = ['_build', 'Thumbs.db', '.DS_Store']


# -- Options for HTML output -------------------------------------------------

# The theme to use for HTML and HTML Help pages.  See the documentation for
# a list of builtin themes.
#
html_theme = 'alabaster'

# Theme options are theme-specific and customize the look and feel of a theme
# further.  For a list of options available for each theme, see the
# documentation.
html_theme_options = {
    # Service links and badges¶
    # 'badge_branch': 'master',  # not supported by Sphinx v1.8.5
    # 'codecov_button': True,
    'github_user': 'avalentino',
    'github_repo': 'geomodels',
    'github_banner': True,
    'github_button': True,
    'github_type': 'watch',  # 'watch', 'fork', 'follow'
    'github_count': True,
    # 'travis_button': True,
    # Non-service sidebar control
    'extra_nav_links': {
        'GeoModels on PyPI': 'https://pypi.org/project/geomodels',
        'GeoGraphicLib': 'https://geographiclib.sourceforge.io/html',
    },
    # 'show_related': True,
    # 'sidebar_collapse': True,  # not supported by Sphinx v1.8.5
    # Header/footer options
    # 'show_powered_by': True,
    # 'show_relbars': True,  # not supported by Sphinx v1.8.5
}

# Add any paths that contain custom static files (such as style sheets) here,
# relative to this directory. They are copied after the builtin static files,
# so a file named "default.css" will overwrite the builtin "default.css".
html_static_path = ['_static']

# Custom sidebar templates, must be a dictionary that maps document names
# to template names.
#
# This is required for the alabaster theme
# refs: http://alabaster.readthedocs.io/en/latest/installation.html#sidebars
html_sidebars = {
    '**': [
        'about.html',
        'navigation.html',
        'relations.html',
        'searchbox.html',
    ],
}


# -- Options for LaTeX output ---------------------------------------------

latex_elements = {
    # The paper size ('letterpaper' or 'a4paper').
    'papersize': 'a4paper',
    # The font size ('10pt', '11pt' or '12pt').
    'pointsize': '12pt',
    # Additional stuff for the LaTeX preamble.
    # 'preamble': '',
    # Latex figure (float) alignment
    # 'figure_align': 'htbp',
}

# Grouping the document tree into LaTeX files. List of tuples
# (source start file, target name, title,
#  author, documentclass [howto, manual, or own class]).
latex_documents = [
    (master_doc, 'GeoModels.tex', 'GeoModels Documentation',
     author, 'manual'),
]

# If false, no module index is generated.
latex_domain_indices = False


# -- Extension configuration -------------------------------------------------

# -- Options for intersphinx extension ---------------------------------------

# Example configuration for intersphinx: refer to the Python standard library.
intersphinx_mapping = {
    'python': ('https://docs.python.org/3', None),
              # '/usr/share/doc/python3/html/objects.inv'),
    'numpy':  ('https://docs.scipy.org/doc/numpy', None),
              # '/usr/share/doc/python-numpy-doc/html/objects.inv'),
}


# -- Options for extlinks extension ------------------------------------------

# External links configuration
extlinks = {
    'issue': ('https://github.com/avalentino/geomodels/issues/%s', 'gh-'),
}
