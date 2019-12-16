#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import re
from setuptools import setup, Extension, find_packages


def get_version(versionfile, strip_extra=False):
    try:
        data = versionfile.read()
    except AttributeError:
        with open(versionfile) as fd:
            data = fd.read()

    mobj = re.search(
        r'''^__version__\s*=\s*(?P<quote>['"])(?P<version>.*)(?P=quote)''',
        data, re.MULTILINE)

    if strip_extra:
        mobj = re.match(r'(?P<version>\d+(\.\d+)*)', mobj.group('version'))

    return mobj.group('version')


extensions = [
    Extension(
        'geomodels._ext',
        sources=['geomodels/_ext.pyx'],
        libraries=['Geographic'],
        language="c++",
    ),
]


classifiers = [
    'Development Status :: 3 - Alpha',
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
    description='Cython wrappers for GeographicLib earth data models',
    # long_description=long_description,
    # long_description_content_type='text/x-rst',
    url='https://github.com/avalentino/geomodels',
    author='Antonio Valentino',
    author_email='antonio.valentino@tiscali.it',
    license='MIT',
    classifiers=classifiers,
    packages=find_packages(),
    ext_modules=extensions,
    setup_requires=['cython'],
    install_requires=['numpy'],
    extras_require={
        'download': 'tqdm',
        'cli': 'argcomplete',
    },
    python_requires='>=3.6',
    # package_data={
    #     'sample': ['package_data.dat'],
    # },
    # data_files=[('data', ['data/data_file'])],
    # entry_points={
    #  ...
    # },
    test_suite='geomodels.test'
)
