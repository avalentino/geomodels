"""Geographic data models."""

from ._version import __version__  # noqa: F401
from ._ext import lib_version_info, lib_version_str  # noqa: F401
from ._ext import GeoidModel, EHeightConvDir  # noqa: F401
from ._ext import GravityModel  # noqa: F401
from ._ext import MagneticFieldModel  # noqa: F401
from .data import (  # noqa: F401
    EModelGroup,
    EModelType,
    EGeoidModel,
    EGravityModel,
    EMagneticModel,
    EArchiveType,
    get_default_data_path,
    get_model_url,
    install,  # TODO: as install_data
)
from .wmmf import MetaData, SphCoeffSet, WmmData, import_igrf_txt  # noqa: F401
from .error import GeographicErr  # noqa: F401
from .tests import test  # noqa: F401
