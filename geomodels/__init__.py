# -*- coding: utf-8 -*-

"""Geographic data models."""

from ._common import lib_version_info, lib_version_str  # noqa
from ._geoid import Geoid                               # noqa
from ._magnetic import MagneticFieldModel               # noqa
from .data import *                                     # noqa
from .error import GeographicErr                        # noqa


__version__ = '0.1.0.dev0'
