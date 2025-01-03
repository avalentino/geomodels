"""Tools for geographic models data download and installation."""

import os
import enum
import shutil
import logging
import pathlib
import tempfile
import contextlib
from typing import Union
from urllib.parse import urlsplit
from urllib.request import urlretrieve
from collections.abc import Callable, Iterable

from ._typing import PathType

__all__ = [
    "EModelGroup",
    "EModelType",
    "EGeoidModel",
    "EGravityModel",
    "EMagneticModel",
    "EArchiveType",
    "get_default_data_path",
    "get_model_url",
    "install",
]


class EModelGroup(enum.Enum):
    """Model groups."""

    ALL = "all"
    MINIMAL = "minimal"
    RECOMMENDED = "recommended"


class EModelType(enum.Enum):
    """Enumerate geographic model types."""

    GEOID = "geoids"
    GRAVITY = "gravity"
    MAGNETIC = "magnetic"


class EGeoidModel(enum.Enum):
    """Enumerate geoid models."""

    EGM84_30 = "egm84-30"
    EGM84_15 = "egm84-15"
    EGM96_15 = "egm96-15"
    EGM96_5 = "egm96-5"
    EGM2008_5 = "egm2008-5"
    EGM2008_2_5 = "egm2008-2_5"
    EGM2008_1 = "egm2008-1"

    @staticmethod
    def get_model_type() -> EModelType:
        """Return the model type corresponding to the enumeration."""
        return EModelType.GEOID


class EGravityModel(enum.Enum):
    """Enumerate gravity models."""

    EGM84 = "egm84"
    EGM96 = "egm96"
    EGM2008 = "egm2008"
    GRS80 = "grs80"
    WGS84 = "wgs84"

    @staticmethod
    def get_model_type() -> EModelType:
        """Return the model type corresponding to the enumeration."""
        return EModelType.GRAVITY


class EMagneticModel(enum.Enum):
    """Enumerate magnetic field models."""

    WMM2010 = "wmm2010"
    WMM2015 = "wmm2015"
    WMM2015V2 = "wmm2015v2"
    WMM2020 = "wmm2020"
    WMM2025 = "wmm2025"
    WMMHR2025 = "wmmhr2025"
    IGRF11 = "igrf11"
    IGRF12 = "igrf12"
    IGRF13 = "igrf13"
    IGRF14 = "igrf14"
    EMM2010 = "emm2010"
    EMM2015 = "emm2015"
    EMM2017 = "emm2017"

    @staticmethod
    def get_model_type() -> EModelType:
        """Return the model type corresponding to the enumeration."""
        return EModelType.MAGNETIC


class EArchiveType(enum.Enum):
    """Enumerate the archive type."""

    ZIP = ".zip"
    BZ2 = ".tar.bz2"


GenericModelType = Union[EGeoidModel, EGravityModel, EMagneticModel]
ReportHookType = Callable[[int, int, int], None]


def get_default_data_path() -> str:
    """Return the default data path.

    The `GEOGRAPHICLIB_DATA` environment variable is used if available
    to locate the location where the geographic model data are installed.

    If `GEOGRAPHICLIB_DATA` is not set, then then it is returned the
    path configured at build time.
    """
    path = os.environ.get("GEOGRAPHICLIB_DATA")
    if path is None:
        from . import MagneticFieldModel

        path = os.path.dirname(MagneticFieldModel.default_magnetic_path())
    return path


_BASE_URL = "https://downloads.sourceforge.net/project/geographiclib/"
_URL_PATH_TEMPLATE = "{basepath}/{modeltype}-distrib/{filename}{ext}"
_URL_QUERY = "use_mirror=autoselect"
_URL_FRAGMENT = ""


def get_base_url() -> str:
    """Return the base URL for data download."""
    return _BASE_URL


def get_model_url(
    model: GenericModelType,
    base_url: str | None = None,
    archive_type: EArchiveType = EArchiveType.BZ2,
) -> str:
    """Return the download URL for the specified geographic model.

    :param model:
        the enumeration corresponding to the desired geographic model.
        It can be one of the enumerates defined in :class:`EGeoidModel`,
        :class:`EGravityModel` or :class:`EMagneticModel`.
    :param str base_url:
        (optional) base URL for data download.
        The full URL is build from this function starting from base_url
        and model information.
    :param EArchiveType archive_type:
        specifies the archive type that should be downloaded.
        Default: `data:`EArchiveType.BZ2`.
    """
    if not base_url:
        base_url = get_base_url()
        query = _URL_QUERY
        fragment = _URL_FRAGMENT
    else:
        query = ""
        fragment = ""

    url = urlsplit(base_url)
    urlpath = _URL_PATH_TEMPLATE.format(
        basepath=url.path.rstrip("/"),
        modeltype=model.get_model_type().value,
        filename=model.value,
        ext=archive_type.value,
    )
    url = url._replace(path=urlpath, query=query, fragment=fragment)
    return url.geturl()


InstallableModelType = Union[EModelGroup, EModelType, GenericModelType]


_MODELTYPE_MAP: dict[EModelType, type[GenericModelType]] = {
    EModelType.GEOID: EGeoidModel,
    EModelType.GRAVITY: EGravityModel,
    EModelType.MAGNETIC: EMagneticModel,
}


def _get_url_map_from_group(
    model: EModelGroup,
    base_url: str | None = None,
    archive_type: EArchiveType = EArchiveType.BZ2,
) -> dict[GenericModelType, str]:
    urls: dict[GenericModelType, str] = {}
    match model:
        case EModelGroup.ALL:
            for modeltype in EModelType:
                urls.update(_get_url_map(modeltype, base_url, archive_type))
        case EModelGroup.MINIMAL:
            from . import GeoidModel, GravityModel, MagneticFieldModel

            models: list[GenericModelType] = [
                EGeoidModel(GeoidModel.default_geoid_name()),
                EGravityModel(GravityModel.default_gravity_name()),
                EMagneticModel(MagneticFieldModel.default_magnetic_name()),
            ]
            for model_ in models:
                urls[model_] = get_model_url(model_, base_url, archive_type)
        case EModelGroup.RECOMMENDED:
            urls.update(_get_url_map(EModelGroup.MINIMAL))
            extra_models: list[GenericModelType] = [
                EGeoidModel.EGM96_5,
                EGravityModel.EGM96,
                EMagneticModel.IGRF12,
                EMagneticModel.WMM2015,
            ]
            for model_ in extra_models:
                urls[model_] = get_model_url(model_, base_url, archive_type)
        case _:
            raise ValueError(f"unexpected value: {model!r}")

    return urls


def _get_url_map(
    model: InstallableModelType,
    base_url: str | None = None,
    archive_type: EArchiveType = EArchiveType.BZ2,
) -> dict[GenericModelType, str]:
    urls: dict[GenericModelType, str]
    match model:
        case EModelGroup() as group:
            urls = _get_url_map_from_group(group)
        case EModelType() as modeltype:
            models: Iterable[GenericModelType] = _MODELTYPE_MAP[modeltype]
            urls = {
                model_: get_model_url(model_, base_url, archive_type)
                for model_ in models
            }
        case EGeoidModel() | EGravityModel() | EMagneticModel() as mod:
            urls = {mod: get_model_url(mod, base_url, archive_type)}
        case _:
            raise ValueError(f"unexpected model: {model!r}")

    return urls


have_tqdm: bool
try:
    import tqdm

    have_tqdm = True

    class TqdmReportHook(tqdm.tqdm):
        """Tqdm based report hook for urllib.request.urlretrieve."""

        def __init__(self, **kwargs):
            if "iterable" in kwargs:
                raise TypeError(
                    "{!r} argument is not allowed by TqdmReportHook."
                )

            # set defaults
            kargs = {
                "unit": "B",
                "unit_scale": True,
                "unit_divisor": 1024,
                "miniters": 1,
            }
            kargs.update(kwargs)

            super().__init__(**kargs)  # type: ignore[call-overload]

        def __call__(
            self,
            count: int = 1,
            block_size: int = 1,
            total_size: int | None = None,
        ):
            if total_size not in (None, -1):
                self.total = total_size

            # will also set: self.n = cont * block_size
            self.update(count * block_size - self.n)

        def __bool__(self):
            # needed by urllib.request.urlretrieve
            return True

except ImportError:
    have_tqdm = False


def _get_report_hook(
    progress: bool | ReportHookType, description: str
) -> ReportHookType | None:
    if progress is True and have_tqdm:
        try:
            base_width = 50
            ncols = os.get_terminal_size().columns
            ncols = ncols - base_width if ncols >= base_width else 0
        except OSError:
            ncols = 0
        return TqdmReportHook(desc=description[-ncols:], leave=False)
    elif callable(progress):
        return progress
    else:
        return None


def download(
    url: str,
    path: PathType = ".",
    progress: bool | ReportHookType = True,
    force: bool = False,
) -> str:
    """Download the specified URL.

    :param str url:
        the url of the file to be downloaded (simple file names are also OK)
    :param str path:
        (optional) target download location (filename or directory).
        Default: ".".
    :param progress:
        boolean to enable/disable the display of progress information
        (default: True).
        Please note that default progress reporting uses the 'tqdm'
        library, if it is not available progress display is switched off.
        It `progress` is set to a callable it is used ar reporthook to show
        progress information.
        Please refer to the :func:`urllib.request.urlretrieve` for
        details about the reporthook function.
    :param bool force:
        overwrite existing files (default: False)
    :returns:
        pathname of the downloaded file
    """
    urlobj = urlsplit(url)
    if not urlobj.scheme:
        urlobj = urlobj._replace(scheme="file")

    path = pathlib.Path(path)
    if path.is_dir():
        path /= pathlib.Path(urlobj.path).name

    if path.exists() and not force:
        raise RuntimeError(f'download target path already exists: "{path}"')

    desc = urlsplit(url)._replace(query="", fragment="").geturl()
    report_hook = _get_report_hook(progress=progress, description=desc)

    if isinstance(report_hook, contextlib.AbstractContextManager):
        with report_hook:
            outpath, _ = urlretrieve(urlobj.geturl(), path, report_hook)
    else:
        outpath, _ = urlretrieve(urlobj.geturl(), path, report_hook)

    return outpath


def install(
    model: InstallableModelType = EModelGroup.MINIMAL,
    datadir: PathType | None = None,
    base_url: str | None = None,
    archive_type: EArchiveType = EArchiveType.BZ2,
    progress: bool = True,
):
    """Install the specified geographic model data.

    :param model:
        the enumeration corresponding to the desired geographic model.
        It can be one of the enumerates defined in :class:`EGeoidModel`,
        :class:`EGravityModel`, :class:`EMagneticModel`, or one of the
        enumerates defined in :class:`EModelType` to indicate that all
        geographic models of the specified type shall be installed,
        or one of the enumerates defined in :class:`EModelGroup` to
        indicate that a specific group of model data shall be installed:
        :data:`EModelGroup.ALL` (all available models of any kind),
        :data:`EModelGroup.MINIMAL` (only the default model for each type)
        or :data:`EModelGroup.RECOMMENDED`.
    :param PathType datadir:
        (optional) specify the target location where geographic model
        data shall be installed. If not specified that the path returned
        by :func:`get_default_data_path` is assumed.
    :param str base_url:
        (optional) base URL for data download.
        The full URL is built from this function starting from base_url
        and model information.
    :param EArchiveType archive_type:
        specifies the archive type that should be downloaded.
        Default: :data:`EArchiveType.BZ2`.
    :param bool progress:
        enable/disable progress information display (default: True)
    """
    urls = _get_url_map(model, base_url, archive_type)

    if not datadir:
        datadir = get_default_data_path()
        if datadir is None:
            raise RuntimeError("no default data location found")

        datadir = pathlib.Path(datadir)
        if not datadir.is_dir():
            raise NotADirectoryError(f'"{datadir}" is not a directory')

    datadir = pathlib.Path(datadir)
    datadir.mkdir(parents=True, exist_ok=True)

    with tempfile.TemporaryDirectory() as tempdir:
        urliterator: Iterable[tuple[GenericModelType, str]]
        if progress and have_tqdm and len(urls) > 1:
            urliterator = tqdm.tqdm(urls.items(), unit="file", desc="download")
        else:
            urliterator = urls.items()

        for model, url in urliterator:
            target = datadir / model.get_model_type().value / model.value
            matches = list(target.parent.glob(f"{target.name}*"))
            if matches:
                logging.debug('"%s" already exists: skip download', target)
                continue
            filename = download(url, tempdir, progress=progress)
            # @CMPATIBILITY: shutil.unpack_archive accepts pathlib.Path
            #                parameters since Python 3.7
            shutil.unpack_archive(str(filename), extract_dir=str(datadir))
