#!/usr/bin/env python3
# -*- coding: utf-8 -*-

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


extensions = [
    Extension(
        'geomodels._ext',
        sources=['geomodels/_ext.pyx'],
        libraries=['Geographic'],
        language="c++",
    ),
]


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
    long_description=open('README.rst').read(),
    long_description_content_type='text/x-rst',
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
    entry_points={
        'console_scripts': [
            'geomodels-download = geomodels.__main__:main'
        ]
    },
    test_suite='geomodels.test'
)
