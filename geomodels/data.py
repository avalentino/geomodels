# -*- coding: utf-8 -*-

"""Tools for geographic models data download."""

import os
import enum
import shutil
import logging
import pathlib
import tempfile
import contextlib

from urllib.parse import urlsplit
from urllib.request import urlretrieve
from typing import Dict, Union, Optional, Callable


__all__ = [
    'EModelType', 'EGeoidModel', 'EGravityModel', 'EMagneticModel',
    'EArchiveType', 'get_default_data_path', 'get_model_url', 'install',
]


class EModelType(enum.Enum):
    """Enumerate geographic model types."""

    GEOID = 'geoids'
    GRAVITY = 'gravity'
    MAGNETIC = 'magnetic'


class EGeoidModel(enum.Enum):
    """Enumerate geoid models."""

    EGM84_30 = 'egm84-30'
    EGM84_15 = 'egm84-15'
    EGM96_15 = 'egm96-15'
    EGM96_5 = 'egm96-5'
    EGM2008_5 = 'egm2008-5'
    EGM2008_2_5 = 'egm2008-2_5'
    EGM2008_1 = 'egm2008-1'

    @staticmethod
    def get_model_type() -> EModelType:
        """Return the model type corresponding to the enumeration."""
        return EModelType.GEOID


class EGravityModel(enum.Enum):
    """Enumerate gravity models."""

    EGM84 = 'egm84'
    EGM96 = 'egm96'
    EGM2008 = 'egm2008'
    # GRS80 = 'grs80'
    WGS84 = 'wgs84'

    @staticmethod
    def get_model_type() -> EModelType:
        """Return the model type corresponding to the enumeration."""
        return EModelType.GRAVITY


class EMagneticModel(enum.Enum):
    """Enumerate magnetic field models."""

    WMM2010 = 'wmm2010'
    WMM2015 = 'wmm2015'
    WMM2020 = 'wmm2020'  # new in GeographicLib v1.50.1
    IGRF11 = 'igrf11'
    IGRF12 = 'igrf12'
    EMM2010 = 'emm2010'
    EMM2015 = 'emm2015'
    EMM2017 = 'emm2017'

    @staticmethod
    def get_model_type() -> EModelType:
        """Return the model type corresponding to the enumeration."""
        return EModelType.MAGNETIC


class EArchiveType(enum.Enum):
    """Enumerate the archive type."""

    ZIP = '.zip'
    BZ2 = '.tar.bz2'


GenericModelType = Union[EGeoidModel, EGravityModel, EMagneticModel]
PathType = Union[str, os.PathLike]  # os.PathLike is new in Python v3.6
ReportHookType = Callable[[int, int, int], None]


def get_default_data_path() -> str:
    """Return the default data path.

    The `GEOGRAPHICLIB_DATA` environment variable is used if available
    to locate the location where the geographic model data are installed.

    If `GEOGRAPHICLIB_DATA` is not set, then then it is returned the
    path configured at build time.
    """
    path = os.environ.get('GEOGRAPHICLIB_DATA')
    if path is None:
        from . import MagneticFieldModel
        path = os.path.dirname(MagneticFieldModel.default_magnetic_path())
    return path


_BASE_URL = 'https://downloads.sourceforge.net/project/geographiclib/'
_URL_PATH_TEMPLATE = '{basepath}/{modeltype}-distrib/{filename}{ext}'
_URL_QUERY = 'use_mirror=autoselect'
_URL_FRAGMENT = ''


def get_base_url():
    """Return the base URL for data download."""
    return _BASE_URL


def get_model_url(model: GenericModelType, base_url: Optional[str] = None,
                  archive_type: EArchiveType = EArchiveType.BZ2) -> str:
    """Return the download URL for the specified geographic model.

    :param model:
        the enumeration corresponding to the desired geographic model.
        It can be one of the enumerates defined in :class:`EGeoidModel`,
        :class:`EGravityModel` or :class:`EMagneticModel`.
    :param str base_url:
        (optional) base URL for data download.
        The full URL is build from this function starting form base_url
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
        query = ''
        fragment = ''

    url = urlsplit(base_url)
    urlpath = _URL_PATH_TEMPLATE.format(
        basepath=url.path.rstrip('/'),
        modeltype=model.get_model_type().value,
        filename=model.value,
        ext=archive_type.value,
    )
    url = url._replace(path=urlpath, query=query, fragment=fragment)
    return url.geturl()


def _get_url_map(modeltype: Optional[EModelType],
                 base_url: Optional[str] = None,
                 archive_type: EArchiveType = EArchiveType.BZ2
                 ) -> Dict[GenericModelType, str]:
    urls = {}
    if not modeltype:
        for modeltype in EModelType:
            urls.update(_get_url_map(modeltype, base_url, archive_type))
    else:
        modeltype_map = {
            EModelType.GEOID: EGeoidModel,
            EModelType.GRAVITY: EGravityModel,
            EModelType.MAGNETIC: EMagneticModel,
        }
        modelenum = modeltype_map[modeltype]
        urls = {
            item: get_model_url(item, base_url, archive_type)
            for item in modelenum
        }

    return urls


try:
    import tqdm

    class TqdmReportHook(tqdm.tqdm):
        """Tqdm based report hook for urllib.request.urlretrieve."""

        def __init__(self, **kwargs):
            if 'iterable' in kwargs:
                raise TypeError(
                    '{!r} argument is not allowed by TqdmReportHook.')

            # set defaults
            kargs = dict(
                unit='B',
                unit_scale=True,
                unit_divisor=1024,
                miniters=1
            )
            kargs.update(kwargs)

            super(TqdmReportHook, self).__init__(**kargs)

        def __call__(self, count=1, block_size=1, total_size=None):
            if total_size not in (None, -1):
                self.total = total_size

            # will also set: self.n = cont * block_size
            self.update(count * block_size - self.n)

        def __bool__(self):
            # needed by urllib.request.urlretrieve
            return True

except ImportError:
    tqdm = None


def download(url: str, path: PathType = '.',
             progress: Union[bool, ReportHookType] = True,
             force: bool = False) -> str:
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
        urlobj = urlobj._replace(scheme='file')

    path = pathlib.Path(path)
    if path.is_dir():
        path /= pathlib.Path(urlobj.path).name

    if path.exists() and not force:
        raise RuntimeError(
            'download target path already exists: "{}"'.format(path))

    if progress is True and tqdm:
        try:
            base_width = 50
            ncols = os.get_terminal_size().columns
            ncols = ncols - base_width if ncols >= base_width else 0
        except OSError:
            ncols = 0
        desc = urlsplit(url)._replace(query='', fragment='').geturl()
        reporthook = TqdmReportHook(desc=desc[-ncols:], leave=False)
    elif progress is False:
        reporthook = None       # type: ignore
    else:
        reporthook = progress

    if isinstance(reporthook, contextlib.AbstractContextManager):
        with reporthook:
            outpath, _ = urlretrieve(urlobj.geturl(), path, reporthook)
    else:
        outpath, _ = urlretrieve(urlobj.geturl(), path, reporthook)

    return outpath


def install(model: Optional[Union[EModelType, GenericModelType]],
            datadir: Optional[PathType] = None, base_url: str = None,
            archive_type: EArchiveType = EArchiveType.BZ2,
            progress: bool = True):
    """Install the specified geographic model data.

    :param model:
        the enumeration corresponding to the desired geographic model.
        It can be one of the enumerates defined in :class:`EGeoidModel`,
        :class:`EGravityModel`, :class:`EMagneticModel`, or one of the
        enumerates defined in :class:`EModelType` to indicate that all
        geographic models of the specified type shall be installed.
        Finally if model is set to None, then all models are installed.
    :param PathType datadir:
        (optional) specify the target location where geographic model
        data shall be installed. If not specified that the path returned
        by :func:`get_default_data_path` is assumed.
    :param str base_url:
        (optional) base URL for data download.
        The full URL is built from this function starting form base_url
        and model information.
    :param EArchiveType archive_type:
        specifies the archive type that should be downloaded.
        Default: :data:`EArchiveType.BZ2`.
    :param bool progress:
        enable/disable progress information display (default: True)
    """
    urls = {}
    if model is None or model in EModelType:
        urls.update(_get_url_map(model, base_url, archive_type))
    else:
        urls[model] = get_model_url(model, base_url, archive_type)

    if not datadir:
        datadir = get_default_data_path()
        if datadir is None:
            raise RuntimeError('no default data location found')

        datadir = pathlib.Path(datadir)
        if not datadir.is_dir():
            raise NotADirectoryError(
                '"{}" is not a directory'.format(datadir))

    datadir = pathlib.Path(datadir)
    datadir.mkdir(parents=True, exist_ok=True)

    with tempfile.TemporaryDirectory() as tempdir:
        if progress and tqdm and len(urls) > 1:
            urliterator = tqdm.tqdm(urls.items(), unit='file', desc='download')
        else:
            urliterator = urls.items()

        for model, url in urliterator:
            target = datadir / model.get_model_type().value / model.value
            matches = list(target.parent.glob(f'{target.name}*'))
            if matches:
                logging.debug('"%s" already exists: skip download', target)
                continue
            filename = download(url, tempdir, progress=progress)
            # NOTE: shutil.unpack_archive accepts pathlib.Path for
            #       extract_dir since Python 3.7
            shutil.unpack_archive(filename, extract_dir=str(datadir))
