# -*- coding: utf-8 -*-

"""Command Line Interface (CLI) for the geomodels package."""

import logging
import argparse

from . import __version__
from .data import get_default_data_path, get_base_url, install
from .data import EModelType, EGeoidModel, EGravityModel, EMagneticModel

try:
    import argcomplete
except ImportError:
    argcomplete = False


EX_FAILURE = 1
EX_INTERRUPT = 130


PROG = __package__
LOGFMT = '%(levelname)s: %(message)s'
# LOGFMT = '%(asctime)s %(levelname)-8s -- %(message)s'


def get_parser():
    """Instantiate the command line argument parser."""
    description = """This program downloads and installs the datasets
used by the GeographicLib library tool to compute magnetic fields.
"""
    parser = argparse.ArgumentParser(description=description, prog=PROG)
    parser.add_argument(
        '--version', action='version', version='%(prog)s v' + __version__)

    # Command line options
    parser.add_argument(
        '-b', '--base-url', default=get_base_url(),
        help='specifies the base URL for the download (default: %(default)s).')
    parser.add_argument(
        '-d', '--datadir', default=get_default_data_path(),
        help='specifies where the datasets should be stored '
             '(default: %(default)s).')

    # Positional arguments
    choices = ['all']
    choices.extend(model.value for model in EModelType)
    choices.extend(model.value for model in EGeoidModel)
    choices.extend(model.value for model in EGravityModel)
    choices.extend(model.value for model in EMagneticModel)
    parser.add_argument(
        'model', choices=choices,
        help='model(s) to be installed (default: %(default)s)')

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

    return args


def main(*argv):
    """Main CLI interface."""
    logging.basicConfig(format=LOGFMT, level=logging.WARNING)
    logging.captureWarnings(True)

    args = parse_args(argv if argv else None)

    try:
        logging.debug('args: %s', args)

        if args.model == 'all':
            model = None
        else:
            enums = (EModelType, EGeoidModel, EGravityModel, EModelType)
            for enumtype in enums:
                try:
                    model = enumtype(args.model)
                except ValueError:
                    pass
                else:
                    break
            else:
                raise RuntimeError('unexpected model: {!r}'.format(args.model))

        install(model, args.datadir, args.base_url)
    except Exception as exc:
        logging.critical('{!r} {}'.format(type(exc).__name__, exc))
        logging.debug('stacktrace:', exc_info=True)
        return EX_FAILURE
    except KeyboardInterrupt:
        logging.warning('Keyboard interrupt received: exit the program')
        return EX_INTERRUPT
