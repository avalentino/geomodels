"""Unit tests for the geomodels package."""

import os
import sys
import locale
import platform
import unittest


def print_versions():
    """Print platform information and library version."""
    from .. import lib_version_str, __version__  # avoid circular imports

    geographiclib_data = os.environ.get("GEOGRAPHICLIB_DATA", "not specified")

    print(f"geomodels version:     {__version__}")
    print(f"GeographicLib version: {lib_version_str()}")
    print(f"GEOGRAPHICLIB_DATA:    {geographiclib_data}")

    print(f"Python version:        {platform.python_version()}")
    print(f"Platform:              {platform.platform()}")
    print(f"Byte-ordering:         {sys.byteorder}")
    print(f"Default encoding:      {sys.getdefaultencoding()}")
    print(f"Default FS encoding:   {sys.getfilesystemencoding()}")
    print(f"Locale:                {locale.getlocale()}")

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
