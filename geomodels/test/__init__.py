# -*- coding: utf-8 -*-

import os
import sys
import locale
import platform
import unittest

from .. import lib_version_str, __version__


def print_versions():
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
    loader = unittest.TestLoader()
    return loader.discover(start_dir=os.path.dirname(__file__))


def test(verbosity=1, failfast=False):
    print_versions()
    runner = unittest.TextTestRunner(verbosity=verbosity, failfast=failfast)
    result = runner.run(suite())

    return os.EX_OK if result.wasSuccessful() else 1
