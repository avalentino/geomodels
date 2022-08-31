#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import os
import sys
import platform
from setuptools import setup, Extension


if os.name == 'posix':
    if platform.system() == 'FreeBSD':
        mandir = 'man'
    else:
        mandir = os.path.join('share', 'man')
    datafiles = [(os.path.join(mandir, 'man1'), ['docs/man/geomodels-cli.1'])]
else:
    datafiles = None


EXTERNAL = 'external'
IGNORE_BUNDLED_LIBS_STR = os.environ.get('GEOMODELS_IGNORE_BUNDLED_LIBS')
IGNORE_BUNDLED_LIBS = bool(
    IGNORE_BUNDLED_LIBS_STR in ('1', 'ON', 'TRUE', 'YES')
)


if os.path.exists(EXTERNAL) and not IGNORE_BUNDLED_LIBS:
    def mkconfig(outpath):
        configdata = """\
#define GEOGRAPHICLIB_VERSION_STRING "2.1.1"
#define GEOGRAPHICLIB_VERSION_MAJOR 2
#define GEOGRAPHICLIB_VERSION_MINOR 1
#define GEOGRAPHICLIB_VERSION_PATCH 1
#define GEOGRAPHICLIB_DATA "/usr/local/share/GeographicLib"

// These are macros which affect the building of the library
#define GEOGRAPHICLIB_HAVE_LONG_DOUBLE {GEOGRAPHICLIB_HAVE_LONG_DOUBLE}
#define GEOGRAPHICLIB_WORDS_BIGENDIAN {GEOGRAPHICLIB_WORDS_BIGENDIAN}
#define GEOGRAPHICLIB_PRECISION 2

#if !defined(GEOGRAPHICLIB_SHARED_LIB)
#define GEOGRAPHICLIB_SHARED_LIB 0
#endif
"""
        GEOGRAPHICLIB_HAVE_LONG_DOUBLE = 0
        GEOGRAPHICLIB_WORDS_BIGENDIAN = 0 if sys.byteorder == 'little' else 1

        data = configdata.format(
            GEOGRAPHICLIB_HAVE_LONG_DOUBLE=GEOGRAPHICLIB_HAVE_LONG_DOUBLE,
            GEOGRAPHICLIB_WORDS_BIGENDIAN=GEOGRAPHICLIB_WORDS_BIGENDIAN,
        )

        if not os.path.exists(outpath):
            with open(outpath, 'w') as fd:
                fd.write(data)
            print('configuration file written to: ', outpath)
        else:
            print('configuration file already exists: ', outpath)

    import glob

    geographiclib_src = glob.glob(
        os.path.join(EXTERNAL, 'GeographicLib*', 'src', '*.cpp'))
    geographiclib_include = glob.glob(
        os.path.join(EXTERNAL, 'GeographicLib*', 'include'))
    geographiclib_include = (
        geographiclib_include[0] if geographiclib_include else None)
    geomodels_ext = Extension(
        'geomodels._ext',
        sources=['geomodels/_ext.pyx'] + geographiclib_src,
        include_dirs=[geographiclib_include],
        libraries=[],
        language='c++',
        extra_compile_args=['-std=c++0x', '-Wall', '-Wextra'],
    )
    mkconfig(os.path.join(geographiclib_include, 'GeographicLib', 'Config.h'))
else:
    geomodels_ext = Extension(
        'geomodels._ext',
        sources=['geomodels/_ext.pyx'],
        libraries=['Geographic'],
        language='c++',
    )

extensions = [geomodels_ext]


with open('README.rst') as fd:
    description = fd.read().replace('.. doctest', '').replace(':doc:', '')


setup(
    long_description=description,
    long_description_content_type='text/x-rst',
    ext_modules=extensions,
    data_files=datafiles,
)
