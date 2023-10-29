"""Geographic data models."""

from ._ext import (  # noqa: F401
    lib_version_info,
    lib_version_str,
    GeoidModel,
    GravityModel,
    EHeightConvDir,
    MagneticFieldModel,
)
from .data import (  # noqa: F401
    EModelGroup,
    EModelType,
    EGeoidModel,
    EGravityModel,
    EMagneticModel,
    EArchiveType,
    get_default_data_path,
    get_model_url,
    install,
)
from .wmmf import MetaData, SphCoeffSet, WmmData, import_igrf_txt  # noqa: F401
from .error import GeographicErr  # noqa: F401
from .tests import test  # noqa: F401
from ._version import __version__  # noqa: F401
