"""Command Line Interface (CLI) for the geomodels Python package."""

import os
import enum
import glob
import logging
import pathlib
import argparse

from . import __version__
from .data import (
    get_default_data_path,
    get_base_url,
    install,
    EModelGroup,
    EModelType,
    EGeoidModel,
    EGravityModel,
    EMagneticModel,
)
from .wmmf import import_igrf_txt
from .tests import print_versions
from ._typing import PathType

EX_FAILURE = 1
EX_INTERRUPT = 130

PROG = __package__ + "-cli"
LOGFMT = "%(levelname)s: %(message)s"
DEFAULT_LOGLEVEL = "WARNING"


class EInfoMode(enum.Enum):
    """Enumeration describing which king of info shall be provided."""

    INFO = "info"
    DATA = "data"
    ALL = "all"


def _autocomplete(parser: argparse.ArgumentParser) -> None:
    try:
        import argcomplete
    except ImportError:
        pass
    else:
        argcomplete.autocomplete(parser)


def _format_data_info(datadir=None):
    if datadir is None:
        datadir = get_default_data_path()

    lines = [f"data directory: {datadir!r}"]
    for modelenum in (EGeoidModel, EGravityModel, EMagneticModel):
        modeltype = modelenum.get_model_type().value
        modeltype_dir = os.path.join(datadir, modeltype)
        lines.append(f"* model: {modeltype} ({modeltype_dir!r})")
        for item in modelenum:
            pattern = os.path.join(modeltype_dir, item.value + "*")
            installed = "INSTALLED " if glob.glob(pattern) else "NOT INSTALLED"
            lines.append(f"  {item.name:12s} - {installed}")

    return "\n".join(lines)


def info(mode=EInfoMode.ALL, datadir=None):
    """Provide information about the installation and environment.

    Information provided include: the platform, the library versions and
    installed data.
    """
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
        raise RuntimeError(f"unexpected model: {model!r}")

    progress = not no_progress
    install(model, datadir, base_url, progress=progress)


def import_igrf(
    path: PathType, outpath: PathType | None = None, force: bool = False
):
    """Import magnetic field data from IGRF text format.

    Import Spherical Harmonics coefficients for the IGRF magnetic field
    model from text file in IGRF standard format.

    See: https://www.ngdc.noaa.gov/IAGA/vmod/igrf.html.
    """
    wmmdata = import_igrf_txt(path)

    if outpath is None:
        outpath = pathlib.Path(get_default_data_path()) / "magnetic"

    wmmdata.save(outpath, force)


def _add_logging_control_args(
    parser: argparse.ArgumentParser, default_loglevel: str = DEFAULT_LOGLEVEL
) -> argparse.ArgumentParser:
    """Add command line options for logging control."""
    loglevels = [logging.getLevelName(level) for level in range(10, 60, 10)]

    parser.add_argument(
        "--loglevel",
        default=default_loglevel,
        choices=loglevels,
        help="logging level (default: %(default)s)",
    )
    parser.add_argument(
        "-q",
        "--quiet",
        dest="loglevel",
        action="store_const",
        const="ERROR",
        help=(
            "suppress standard output messages, only errors are printed "
            "to screen (set 'loglevel' to 'ERROR')"
        ),
    )
    parser.add_argument(
        "-v",
        "--verbose",
        dest="loglevel",
        action="store_const",
        const="INFO",
        help="print verbose output messages (set 'loglevel' to 'INFO')",
    )
    parser.add_argument(
        # "-d",
        "--debug",
        dest="loglevel",
        action="store_const",
        const="DEBUG",
        help="print debug messages (set 'loglevel' to 'DEBUG')",
    )

    return parser


def _get_synopsis(docstring: str | None) -> str:
    return docstring.splitlines()[0] if docstring is not None else ""


def get_info_parser(subparsers=None) -> argparse.ArgumentParser:
    """Set up the argument parser for the `info` sub-command."""
    name = "info"
    synopsis = _get_synopsis(info.__doc__)
    doc = info.__doc__

    if subparsers is None:
        parser = argparse.ArgumentParser(prog=name, description=doc)
    else:
        parser = subparsers.add_parser(name, description=doc, help=synopsis)

    parser.set_defaults(func=info)

    # command line options
    parser.add_argument(
        "-d",
        "--datadir",
        default=get_default_data_path(),
        help=(
            "specifies where the model data are stored (default: %(default)r)."
        ),
    )
    parser.add_argument(
        "-a",
        "--all",
        dest="mode",
        action="store_const",
        const=EInfoMode.ALL,
        default=EInfoMode.INFO,
        help=(
            "show both versions and platform info and also information "
            "about installed data"
        ),
    )
    parser.add_argument(
        "--data",
        dest="mode",
        action="store_const",
        const=EInfoMode.DATA,
        help="show info about installed data",
    )

    return parser


def get_install_data_parser(subparsers=None) -> argparse.ArgumentParser:
    """Set up the argument parser for the `install-data` sub-command."""
    name = "install-data"
    synopsis = _get_synopsis(install_data.__doc__)
    doc = install_data.__doc__

    if subparsers is None:
        parser = argparse.ArgumentParser(
            prog=name,
            description=doc,
            formatter_class=argparse.RawDescriptionHelpFormatter,
        )
    else:
        parser = subparsers.add_parser(
            name,
            description=doc,
            help=synopsis,
            formatter_class=argparse.RawDescriptionHelpFormatter,
        )

    parser.set_defaults(func=install_data)

    # command line options
    parser.add_argument(
        "-b",
        "--base-url",
        default=get_base_url(),
        help="specifies the base URL for the download (default: %(default)r).",
    )
    parser.add_argument(
        "-d",
        "--datadir",
        default=get_default_data_path(),
        help=(
            "specifies where the datasets should be stored "
            "(default: %(default)r)."
        ),
    )
    parser.add_argument(
        "--no-progress",
        action="store_true",
        default=False,
        help="suppress progress bar display",
    )

    # positional arguments
    choices = [model.value for model in EModelGroup]
    choices.extend(model.value for model in EModelType)
    choices.extend(model.value for model in EGeoidModel)
    choices.extend(model.value for model in EGravityModel)
    choices.extend(model.value for model in EMagneticModel)
    parser.add_argument(
        "model", choices=choices, help="model(s) to be installed"
    )

    return parser


def get_import_igrf_parser(subparsers=None) -> argparse.ArgumentParser:
    """Set up the  argument parser for the `import-igrf` sub-command."""
    name = "import-igrf"
    synopsis = _get_synopsis(import_igrf.__doc__)
    doc = import_igrf.__doc__

    if subparsers is None:
        parser = argparse.ArgumentParser(prog=name, description=doc)
    else:
        parser = subparsers.add_parser(name, description=doc, help=synopsis)

    parser.set_defaults(func=import_igrf)

    # command line options
    parser.add_argument(
        "-o",
        "--outpath",
        default=pathlib.Path(get_default_data_path()) / "magnetic",
        help='specifies the output data path (default: "%(default)s").',
    )
    parser.add_argument(
        "--force",
        action="store_true",
        default=False,
        help="overwrite existing files (default: %(default)s).",
    )

    # positional arguments
    parser.add_argument("path", help="path or URL of the IGRF text file")

    return parser


def get_parser() -> argparse.ArgumentParser:
    """Instantiate the command line argument (sub-)parser."""
    parser = argparse.ArgumentParser(prog=PROG, description=__doc__)
    parser.add_argument(
        "--version", action="version", version="%(prog)s v" + __version__
    )

    # Command line options
    _add_logging_control_args(parser)

    # Sub-command management
    subparsers = parser.add_subparsers(title="sub-commands")  # , metavar="")
    get_info_parser(subparsers)
    get_install_data_parser(subparsers)
    get_import_igrf_parser(subparsers)

    _autocomplete(parser)

    return parser


def parse_args(args=None, namespace=None, parser=None):
    """Parse command line arguments."""
    if parser is None:
        parser = get_parser()

    args = parser.parse_args(args, namespace)

    # Common pre-processing of parsed arguments and consistency checks
    # ...

    if getattr(args, "func", None) is None:
        parser.error("no sub-command specified.")

    return args


def _get_kwargs(args):
    kwargs = vars(args).copy()
    kwargs.pop("func", None)
    kwargs.pop("loglevel", None)
    return kwargs


def main(*argv):
    """Implement the main CLI interface."""
    # setup logging
    logging.basicConfig(format=LOGFMT, level=DEFAULT_LOGLEVEL)
    logging.captureWarnings(True)
    log = logging.getLogger(__name__)

    # parse cmd line arguments
    args = parse_args(argv if argv else None)

    try:
        # NOTE: use the root logger to set the logging level
        logging.getLogger().setLevel(args.loglevel)

        log.debug("args: %s", args)
        kwargs = _get_kwargs(args)
        return args.func(**kwargs)
    except Exception as exc:  # noqa: B902
        log.critical(
            "unexpected exception caught: %r %s", type(exc).__name__, exc
        )
        log.debug("stacktrace:", exc_info=True)
        return EX_FAILURE
    except KeyboardInterrupt:
        log.warning("Keyboard interrupt received: exit the program")
        return EX_INTERRUPT
