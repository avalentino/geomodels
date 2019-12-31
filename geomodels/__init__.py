# -*- coding: utf-8 -*-

"""Geographic data models."""

from ._ext import lib_version_info, lib_version_str  # noqa
from ._ext import GeoidModel, EHeightConvDir         # noqa
from ._ext import GravityModel                       # noqa
from ._ext import MagneticFieldModel                 # noqa
from .data import *                                  # noqa
from .wmmf import *                                  # noqa
from .error import GeographicErr                     # noqa
from .tests import test                              # noqa


__version__ = '1.0.0b4'
