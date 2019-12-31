# -*- coding: utf-8 -*-

"""Command Line Interface (CLI) for the geomodels package."""

import os
import enum
import glob
import logging
import pathlib
import argparse

from typing import Optional

from . import __version__
from . import tests
from .data import get_default_data_path, get_base_url, install
from .data import (
    EModelGroup, EModelType, EGeoidModel, EGravityModel, EMagneticModel,
)
from .wmmf import import_igrf_txt
from .tests import print_versions
from ._typing import PathType

try:
    import argcomplete
except ImportError:
    argcomplete = False


EX_FAILURE = 1
EX_INTERRUPT = 130


PROG = __package__ + '-cli'
LOGFMT = '%(levelname)s: %(message)s'


class EInfoMode(enum.Enum):
    INFO = 'info'
    DATA = 'data'
    ALL = 'all'


def _format_data_info(datadir=None):
    if datadir is None:
        datadir = get_default_data_path()

    lines = [f'data directory: {datadir!r}']
    for modelenum in (EGeoidModel, EGravityModel, EMagneticModel):
        modeltype = modelenum.get_model_type().value
        modeltype_dir = os.path.join(datadir, modeltype)
        lines.append(f'* model: {modeltype} ({modeltype_dir!r})')
        for item in modelenum:
            pattern = os.path.join(modeltype_dir, item.value + '*')
            installed = bool(glob.glob(pattern))
            installed = 'INSTALLED ' if installed else 'NOT INSTALLED'
            lines.append(f'  {item.name:12s} - {installed}')

    return '\n'.join(lines)


def info(mode=EInfoMode.ALL, datadir=None):
    """Provide information about the platform, library versions and
    installed data."""

    if mode in (EInfoMode.INFO, EInfoMode.ALL):
        print_versions()
    if mode in (EInfoMode.DATA, EInfoMode.ALL):
        print(_format_data_info(datadir))


def install_data(model, datadir=None, base_url=None, no_progress=False):
    """Download and install the data necessary for models computation.

    GeoModels uses external data to perform geoid, gravity and magnetic
    field computations.

    It is possible to install different subsets of data:

    :minimal:
        only data for the default model of each kind (geoid,
        gravity and magnetic field) are installed,
    :recommended:
        install the `minimal` set of data (see above) plus few
        additional and commonly used data (it is guaranteed that
        the `recommended` subset always includes all data that
        are necessary to run the test suite),
    :all:
        install all available data (about 670MB of disk space
        required),
    :geoids:
        install data for all supported geoids,
    :gravity:
        install data for all supported gravity models,
    :magnetic:
        install data for all supported magnetic field models.

    Additionally the it is possible to install data for a single model.
    """
    if datadir is None:
        datadir = get_default_data_path()
    if base_url is None:
        base_url = get_base_url()

    enums = (
        EModelGroup,
        EModelType,
        EGeoidModel,
        EGravityModel,
        EMagneticModel,
    )
    for enumtype in enums:
        try:
            model = enumtype(model)
        except ValueError:
            pass
        else:
            break
    else:
        raise RuntimeError(f'unexpected model: {model!r}')

    progress = not no_progress
    install(model, datadir, base_url, progress=progress)


def import_igrf(path: PathType, outpath: Optional[PathType] = None,
                force: bool = False):
    """Import magnetic field data from IGRF text format.

    Import Spherical Harmonics coefficients for the IGRF magnetic field
    model from text file in IGRF standard format.

    See: https://www.ngdc.noaa.gov/IAGA/vmod/igrf.html.
    """
    wmmdata = import_igrf_txt(path)

    if outpath is None:
        outpath = pathlib.Path(get_default_data_path()) / 'magnetic'

    wmmdata.save(outpath, force)


def test(datadir: Optional[PathType] = None,
         verbosity: int = 1, failfast: bool = False):
    """Run the test suite for the geomodels package."""
    old_geographiclib_data = os.environ.get('GEOGRAPHICLIB_DATA')
    try:
        if datadir is not None:
            os.environ['GEOGRAPHICLIB_DATA'] = str(datadir)
        return tests.test(verbosity, failfast)
    finally:
        if old_geographiclib_data is None:
            del os.environ['GEOGRAPHICLIB_DATA']
        else:
            os.environ['GEOGRAPHICLIB_DATA'] = old_geographiclib_data


def _set_logging_control_args(parser, default_loglevel='WARNING'):
    """Setup command line options for logging control."""

    loglevels = [logging.getLevelName(level) for level in range(10, 60, 10)]

    parser.add_argument(
        '--loglevel', default=default_loglevel, choices=loglevels,
        help='logging level (default: %(default)s)')
    parser.add_argument(
        '-q', '--quiet', dest='loglevel', action='store_const',
        const='ERROR',
        help='suppress standard output messages, only errors are printed '
             'to screen (set "loglevel" to "ERROR")')
    parser.add_argument(
        '-v', '--verbose', dest='loglevel', action='store_const', const='INFO',
        help='print verbose output messages (set "loglevel" to "INFO")')
    parser.add_argument(
        '--debug', dest='loglevel', action='store_const', const='DEBUG',
        help='print debug messages (set "loglevel" to "DEBUG")')

    return parser


def get_info_parser(parser=None):
    name = 'info'
    synopsis = info.__doc__.splitlines()[0].lower()
    doc = info.__doc__

    if parser is None:
        parser = argparse.ArgumentParser(prog=name, description=doc)
    else:
        parser = parser.add_parser(name, description=doc, help=synopsis)

    parser.set_defaults(func=info)

    # command line options
    parser.add_argument(
        '-d', '--datadir', default=get_default_data_path(),
        help='specifies where the model data are stored '
             '(default: %(default)r).')
    parser.add_argument(
        '-a', '--all', dest='mode', action='store_const', const=EInfoMode.ALL,
        default=EInfoMode.INFO,
        help='show both versions and platform info and also information '
             'about installed data')
    parser.add_argument(
        '--data', dest='mode', action='store_const', const=EInfoMode.DATA,
        help='show info about installed data')

    # positional arguments
    # ...

    return parser


def get_install_data_parser(parser=None):
    name = 'install-data'
    synopsis = install_data.__doc__.splitlines()[0].lower()
    doc = install_data.__doc__

    if parser is None:
        parser = argparse.ArgumentParser(
            prog=name, description=doc,
            formatter_class=argparse.RawDescriptionHelpFormatter)
    else:
        parser = parser.add_parser(
            name, description=doc, help=synopsis,
            formatter_class=argparse.RawDescriptionHelpFormatter)

    parser.set_defaults(func=install_data)

    # command line options
    parser.add_argument(
        '-b', '--base-url', default=get_base_url(),
        help='specifies the base URL for the download (default: %(default)r).')
    parser.add_argument(
        '-d', '--datadir', default=get_default_data_path(),
        help='specifies where the datasets should be stored '
             '(default: %(default)r).')
    parser.add_argument(
        '--no-progress', action='store_true', default=False,
        help='suppress progress bar display')

    # positional arguments
    choices = [model.value for model in EModelGroup]
    choices.extend(model.value for model in EModelType)
    choices.extend(model.value for model in EGeoidModel)
    choices.extend(model.value for model in EGravityModel)
    choices.extend(model.value for model in EMagneticModel)
    parser.add_argument(
        'model', choices=choices, help='model(s) to be installed')

    return parser


def get_import_igrf_parser(parser=None):
    name = 'import-igrf'
    doc = import_igrf.__doc__.splitlines()[0]
    synopsis = doc.lower()

    if parser is None:
        parser = argparse.ArgumentParser(prog=name, description=doc)
    else:
        parser = parser.add_parser(name, description=doc, help=synopsis)

    parser.set_defaults(func=import_igrf)

    # command line options
    parser.add_argument(
        '-o', '--outpath',
        default=pathlib.Path(get_default_data_path()) / 'magnetic',
        help='specifies the output data path (default: "%(default)s").')
    parser.add_argument(
        '--force', action='store_true', default=False,
        help='overwrite existing files (default: %(default)s).')

    # positional arguments
    parser.add_argument(
        'path',
        help='path or URL of the IGRF text file')

    return parser


def get_test_parser(parser=None):
    name = 'test'
    doc = test.__doc__.splitlines()[0]
    synopsis = doc.lower()

    if parser is None:
        parser = argparse.ArgumentParser(prog=name, description=doc)
    else:
        parser = parser.add_parser(name, description=doc, help=synopsis)

    parser.set_defaults(func=test)

    # command line options
    parser.add_argument(
        '-d', '--datadir', default=get_default_data_path(),
        help='specifies where the model data are stored '
             '(default: %(default)r).')
    parser.add_argument(
        '--verbosity', type=int, default=1,
        help='verbosity level for the unittest runner (default: %(default)s).')
    parser.add_argument(
        '--failfast', action='store_true', default=False,
        help='stop the test run on the first error or failure '
             '(default: %(default)s).')

    # positional arguments
    # ...

    return parser


def get_parser():
    """Instantiate the command line argument parser."""
    parser = argparse.ArgumentParser(description=__doc__, prog=PROG)
    parser.add_argument(
        '--version', action='version', version='%(prog)s v' + __version__)

    # Command line options
    _set_logging_control_args(parser)

    # Positional arguments
    # ...

    # Sub-command management
    subparsers = parser.add_subparsers(title='sub-commands')  # dest='func'
    get_info_parser(subparsers)
    get_install_data_parser(subparsers)
    get_import_igrf_parser(subparsers)
    get_test_parser(subparsers)

    if argcomplete:
        argcomplete.autocomplete(parser)

    return parser


def parse_args(args=None, namespace=None, parser=None):
    """Parse command line arguments."""
    if parser is None:
        parser = get_parser()

    args = parser.parse_args(args, namespace)

    # Common pre-processing of parsed arguments and consistency checks
    # ...

    if getattr(args, 'func', None) is None:
        parser.error('no sub-commnd specified.')

    return args


def _get_kwargs(args):
    kwargs = dict(args._get_kwargs())
    kwargs.pop('loglevel')
    kwargs.pop('func')
    return kwargs


def main(*argv):
    """Main CLI interface."""
    logging.basicConfig(format=LOGFMT, level=logging.WARNING)
    logging.captureWarnings(True)

    args = parse_args(argv if argv else None)
    logging.getLogger().setLevel(args.loglevel)

    try:
        logging.debug('args: %s', args)

        func = args.func
        kwargs = _get_kwargs(args)
        return func(**kwargs)

    except Exception as exc:
        logging.critical('{!r} {}'.format(type(exc).__name__, exc))
        logging.debug('stacktrace:', exc_info=True)
        return EX_FAILURE
    except KeyboardInterrupt:
        logging.warning('Keyboard interrupt received: exit the program')
        return EX_INTERRUPT
