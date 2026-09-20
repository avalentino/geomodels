"""Geographic data models."""

from ._ext import (  # noqa: F401
    GeoidModel,
    GravityModel,
    EHeightConvDir,
    MagneticFieldModel,
    lib_version_str,
    lib_version_info,
)
from .data import (  # noqa: F401
    EModelType,
    EGeoidModel,
    EModelGroup,
    EArchiveType,
    EGravityModel,
    EMagneticModel,
    install,
    get_model_url,
    get_default_data_path,
)
from .wmmf import WmmData, MetaData, SphCoeffSet, import_igrf_txt  # noqa: F401
from .error import GeographicError  # noqa: F401
from ._version import __version__  # noqa: F401
