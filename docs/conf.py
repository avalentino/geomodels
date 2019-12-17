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
copyright = '2019, Antonio Valentino'
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
    # 'sphinx.ext.doctest',
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

# Add any paths that contain custom static files (such as style sheets) here,
# relative to this directory. They are copied after the builtin static files,
# so a file named "default.css" will overwrite the builtin "default.css".
html_static_path = ['_static']


# -- Extension configuration -------------------------------------------------

# -- Options for intersphinx extension ---------------------------------------

# Example configuration for intersphinx: refer to the Python standard library.
intersphinx_mapping = {
    'python': ('https://docs.python.org/3',
               '/usr/share/doc/python3/html/objects.inv'),
    'numpy':  ('https://docs.scipy.org/doc/numpy',
               '/usr/share/doc/python-numpy-doc/html/objects.inv'),
}


# -- Options for extlinks extension ------------------------------------------

# External links configuration
extlinks = {
    'issue': ('https://github.com/avalentino/geomodels/issues/%s', 'gh-'),
}
