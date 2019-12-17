# -*- coding: utf-8 -*-
# cython: language_level=3
# distutils: language=c++

from typing import Tuple
from collections import namedtuple

from .common cimport (
    GEOGRAPHICLIB_VERSION_MAJOR,
    GEOGRAPHICLIB_VERSION_MINOR,
    GEOGRAPHICLIB_VERSION_PATCH,
    GEOGRAPHICLIB_VERSION_STRING,
)


__all__ = ['lib_version_info', 'lib_version_str']


VersionInfo = namedtuple('VersionInfo', ['major', 'minor', 'micro'])


def lib_version_info() -> Tuple[int, int, int]:
    """Return the (major, minor, patch) version of GeographicLib.

    .. note::

       the returned information refers to the version of the
       GeographicLib library used at build time.
       The version of the shared library actually used at runtime could
       be different.
    """
    return VersionInfo(
        GEOGRAPHICLIB_VERSION_MAJOR,
        GEOGRAPHICLIB_VERSION_MINOR,
        GEOGRAPHICLIB_VERSION_PATCH,
    )


def lib_version_str() -> str:
    """Return the version string of GeographicLib.

    .. note::

       the returned information refers to the version of the
       GeographicLib library used at build time.
       The version of the shared library actually used at runtime could
       be different.
    """
    return GEOGRAPHICLIB_VERSION_STRING.decode('utf-8')
