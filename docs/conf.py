# Configuration file for the Sphinx documentation builder.
#
# For the full list of built-in configuration values, see the documentation:
# https://www.sphinx-doc.org/en/master/usage/configuration.html

# -- Path setup --------------------------------------------------------------

import os
import sys

try:
    import geomodels  # noqa: F401
except ImportError:
    sys.path.insert(0, os.path.abspath(".."))


# -- Version utils -----------------------------------------------------------


def get_version(filename="../geomodels/_version.py", strip_extra=False):
    import re

    import packaging.version

    with open(filename) as fd:
        data = fd.read()

    mobj = re.search(
        r"""^__version__\s*=\s*(?P<quote>['"])(?P<version>.*)(?P=quote)""",
        data,
        re.MULTILINE,
    )

    version = packaging.version.parse(mobj.group("version"))

    if strip_extra:
        return version.base_version
    return str(version)


# -- Project information -----------------------------------------------------
# https://www.sphinx-doc.org/en/master/usage/configuration.html#project-information

project = "GeoModels"
copyright = "2019-2026, Antonio Valentino"
author = "Antonio Valentino"

# The short X.Y version.
version = get_version(strip_extra=True)

# The full version, including alpha/beta/rc tags
release = get_version(strip_extra=False)

master_doc = "index"


# -- General configuration ---------------------------------------------------
# https://www.sphinx-doc.org/en/master/usage/configuration.html#general-configuration

extensions = [
    "sphinx.ext.autodoc",
    # "sphinx.ext.autosectionlabel",
    "sphinx.ext.autosummary",
    # "sphinx.ext.coverage",
    "sphinx.ext.doctest",
    # "sphinx.ext.duration",
    "sphinx.ext.extlinks",
    # "sphinx.ext.githubpages",
    # "sphinx.ext.graphviz",
    "sphinx.ext.ifconfig",
    # "sphinx.ext.imgconverter",
    # "sphinx.ext.inheritance_diagram",
    "sphinx.ext.intersphinx",
    # "sphinx.ext.linkcode",  # needs_sphinx = "1.2"
    # "sphinx.ext.napoleon",
    "sphinx.ext.todo",
    "sphinx.ext.viewcode",
    # "sphinx.ext.imgmath",
    # "sphinx.ext.jsmath",
    "sphinx.ext.mathjax",
]

try:
    import sphinxcontrib.spelling  # noqa: F401,I900
except ImportError:
    pass
else:
    extensions.append("sphinxcontrib.spelling")

templates_path = ["_templates"]
exclude_patterns = ["_build", "Thumbs.db", ".DS_Store"]


# -- Options for HTML output -------------------------------------------------
# https://www.sphinx-doc.org/en/master/usage/configuration.html#options-for-html-output

html_theme = "alabaster"
html_static_path = ["_static"]
html_theme_options = {
    # Service links and badges¶
    # 'badge_branch': 'master',  # not supported by Sphinx v1.8.5
    # 'codecov_button': True,
    "github_user": "avalentino",
    "github_repo": "geomodels",
    "github_banner": True,
    "github_button": True,
    "github_type": "watch",  # 'watch', 'fork', 'follow'
    "github_count": True,
    # 'travis_button': True,
    # Non-service sidebar control
    "extra_nav_links": {
        "GeoModels on PyPI": "https://pypi.org/project/geomodels",
        "GeoGraphicLib": "https://github.com/geographiclib/geographiclib",
    },
    # 'show_related': True,
    # 'sidebar_collapse': True,  # not supported by Sphinx v1.8.5
    # Header/footer options
    # 'show_powered_by': True,
    # 'show_relbars': True,  # not supported by Sphinx v1.8.5
}

# Custom sidebar templates, must be a dictionary that maps document names
# to template names.
#
# This is required for the alabaster theme
# refs: http://alabaster.readthedocs.io/en/latest/installation.html#sidebars
html_sidebars = {
    "**": [
        "about.html",
        "navigation.html",
        "relations.html",
        "searchbox.html",
    ],
}


# -- Options for LaTeX output ------------------------------------------------
latex_documents = [
    (
        master_doc,
        project + ".tex",
        f"{project} Documentation",
        author,
        "manual",
        False,
    ),
]

latex_domain_indices = False

latex_elements = {
    "papersize": "a4paper",
    "pointsize": "12pt",
}


# -- Extension configuration -------------------------------------------------

# -- Options for intersphinx extension ---------------------------------------
# https://www.sphinx-doc.org/en/master/usage/extensions/intersphinx.html#configuration

intersphinx_mapping = {
    "python": ("https://docs.python.org/3/", None),
    # '/usr/share/doc/python3/html/objects.inv'),
    "numpy": ("https://numpy.org/doc/stable/", None),
    # '/usr/share/doc/python-numpy-doc/html/objects.inv'),
}


# -- Options for extlinks extension ------------------------------------------

extlinks = {
    "issue": ("https://github.com/avalentino/geomodels/issues/%s", "gh-%s"),
}


# -- Options for todo extension ----------------------------------------------
# https://www.sphinx-doc.org/en/master/usage/extensions/todo.html#configuration

todo_include_todos = True
