#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import os
import sys
import platform
from setuptools import setup, Extension, find_packages


def get_version(filename, strip_extra=False):
    import re
    from distutils.version import LooseVersion

    data = open(filename).read()
    mobj = re.search(
        r'''^__version__\s*=\s*(?P<quote>['"])(?P<version>.*)(?P=quote)''',
        data, re.MULTILINE)
    version = LooseVersion(mobj.group('version'))

    if strip_extra:
        return '.'.join(map(str, version.version[:3]))
    else:
        return version.vstring


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
        language="c++",
        extra_compile_args=['-std=c++0x', '-Wall', '-Wextra'],
    )
else:
    geomodels_ext = Extension(
        'geomodels._ext',
        sources=['geomodels/_ext.pyx'],
        libraries=['Geographic'],
        language="c++",
    )

extensions = [geomodels_ext]


requires = ['numpy']
if sys.version_info[:2] < (3, 7):
    requires.append('dataclasses')


with open('README.rst') as fd:
    description = fd.read().replace('.. doctest', '').replace(':doc:', '')


classifiers = [
    'Development Status :: 4 - Beta',
    'Intended Audience :: Developers',
    "Intended Audience :: Science/Research",
    'License :: OSI Approved :: MIT License',
    'Programming Language :: Python :: 3',
    'Programming Language :: Python :: 3.6',
    'Programming Language :: Python :: 3.7',
    'Programming Language :: Python :: 3.8',
    "Topic :: Scientific/Engineering :: GIS",
    "Topic :: Software Development :: Libraries :: Python Modules",
]


setup(
    name='geomodels',
    version=get_version('geomodels/__init__.py'),
    description='Python package for Earth data models management',
    long_description=description,
    long_description_content_type='text/x-rst',
    url='https://github.com/avalentino/geomodels',
    author='Antonio Valentino',
    author_email='antonio.valentino@tiscali.it',
    license='MIT',
    classifiers=classifiers,
    packages=find_packages(),
    ext_modules=extensions,
    setup_requires=['cython'],
    install_requires=requires,
    data_files=datafiles,
    extras_require={
        'download': 'tqdm',
        'cli': 'argcomplete',
    },
    python_requires='>=3.6',
    entry_points={
        'console_scripts': [
            'geomodels-cli = geomodels.__main__:main'
        ]
    },
    package_data={
        'geomodels.tests': ['data/*.txt'],
    },
    test_suite='geomodels.tests'
)
