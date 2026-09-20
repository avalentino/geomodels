"""Unit tests for the geomodels package."""

import os
import unittest

from geomodels.cli import print_versions


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
