# -*- coding: utf-8 -*-

import os
import sys
import locale
import platform
import unittest


def print_versions():
    """Print platform information and library version."""
    from .. import lib_version_str, __version__  # avoid circular imports

    print('geomodels version:     %s' % __version__)
    print('GeographicLib version: %s' % lib_version_str())

    print('Python version:        %s' % platform.python_version())
    print('Platform:              %s' % platform.platform())
    print('Byte-ordering:         %s' % sys.byteorder)
    print('Default encoding:      %s' % sys.getdefaultencoding())
    print('Default FS encoding:   %s' % sys.getfilesystemencoding())
    print('Default locale:        (%s, %s)' % locale.getdefaultlocale())

    print()

    sys.stdout.flush()


def suite():
    """Return the test suite for the geomodels package."""
    loader = unittest.TestLoader()
    return loader.discover(start_dir=os.path.dirname(__file__))


def test(verbosity: int = 1, failfast: bool = False):
    """Run the test suite for the geomodels package.

    :param int verbosity:
        verbosity level (higher is more verbose).
        Default: 1.
    :param bool failfast:
        stop the test run on the first error or failure.
        Default: False.
    """
    print_versions()
    runner = unittest.TextTestRunner(verbosity=verbosity, failfast=failfast)
    result = runner.run(suite())

    return os.EX_OK if result.wasSuccessful() else 1
