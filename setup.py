#!/usr/bin/env python3

import os
import re
import sys
import pathlib
import platform

from setuptools import setup, Extension


def mkconfig(srcpath, outpath, have_lohg_double=0):
    data = pathlib.Path(srcpath).joinpath("CMakeLists.txt").read_text()
    mobj = re.search(
        r"""\
set\s*\(\s*PROJECT_VERSION_MAJOR\s+(?P<VERSION_MAJOR>\d+)\s*\)\s*
set\s*\(\s*PROJECT_VERSION_MINOR\s+(?P<VERSION_MINOR>\d+)\s*\)\s*
set\s*\(\s*PROJECT_VERSION_PATCH\s+(?P<VERSION_PATCH>\d+)\s*\)\s*
""",
        data,
        re.MULTILINE,
    )

    version_major = mobj.group("VERSION_MAJOR")
    version_minor = mobj.group("VERSION_MINOR")
    version_patch = mobj.group("VERSION_PATCH")

    if version_patch == "0":
        version_string = ".".join([version_major, version_minor])
    else:
        version_string = ".".join(
            [version_major, version_minor, version_patch],
        )

    bigendian = 0 if sys.byteorder == "little" else 1

    configdata = f"""\
#define GEOGRAPHICLIB_VERSION_STRING "{version_string}"
#define GEOGRAPHICLIB_VERSION_MAJOR {version_major}
#define GEOGRAPHICLIB_VERSION_MINOR {version_minor}
#define GEOGRAPHICLIB_VERSION_PATCH {version_patch}
#define GEOGRAPHICLIB_DATA "/usr/local/share/GeographicLib"

// These are macros which affect the building of the library
#define GEOGRAPHICLIB_HAVE_LONG_DOUBLE {have_lohg_double}
#define GEOGRAPHICLIB_WORDS_BIGENDIAN {bigendian}
#define GEOGRAPHICLIB_PRECISION 2

#if !defined(GEOGRAPHICLIB_SHARED_LIB)
#define GEOGRAPHICLIB_SHARED_LIB 0
#endif
"""

    outpath = pathlib.Path(outpath)
    if not outpath.exists():
        outpath.write_text(configdata)
        print(f"configuration file written to: {outpath}")
    else:
        print(f"configuration file already exists: {outpath}")


if os.name == "posix":
    if platform.system() == "FreeBSD":
        mandir = pathlib.Path("man")
    else:
        mandir = pathlib.Path("share/man")
    datafiles = [
        (
            str(mandir / "man1"),
            ["docs/man/geomodels-cli.1"],
        )
    ]
else:
    datafiles = []


IGNORE_BUNDLED_LIBS_STR = os.environ.get("GEOMODELS_IGNORE_BUNDLED_LIBS")
IGNORE_BUNDLED_LIBS = bool(
    IGNORE_BUNDLED_LIBS_STR in ("1", "ON", "TRUE", "YES")
)
SRCPATH = pathlib.Path("extern/geographiclib")


if SRCPATH.exists() and not IGNORE_BUNDLED_LIBS:
    geographiclib_src = SRCPATH.glob("src/*.cpp")
    geographiclib_include = list(SRCPATH.glob("include"))[0]
    geomodels_ext = Extension(
        "geomodels._ext",
        sources=["geomodels/_ext.pyx"] + [str(p) for p in geographiclib_src],
        include_dirs=[str(geographiclib_include)],
        libraries=[],
        language="c++",
        extra_compile_args=["-std=c++11", "-Wall"],
    )
    outpath = geographiclib_include / "GeographicLib" / "Config.h"
    mkconfig(SRCPATH, outpath)
else:
    libname = os.environ.get("GEOMODELS_GEOGRAPHICLIB_NAME", "GeographicLib")
    geomodels_ext = Extension(
        "geomodels._ext",
        sources=["geomodels/_ext.pyx"],
        libraries=[libname],
        language="c++",
    )


description = pathlib.Path("README.rst").read_text()
description = description.replace(".. doctest", "").replace(":doc:", "")


setup(
    long_description=description,
    long_description_content_type="text/x-rst",
    ext_modules=[geomodels_ext],
    data_files=datafiles,
)
