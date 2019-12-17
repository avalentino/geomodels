=========
GeoModels
=========

:copyright: 2019 Antonio Valentino
:license: MIT
:url: https://github.com/avalentino/geomodels

.. image:: https://travis-ci.org/avalentino/geomodels.svg?branch=master
    :alt: Travis-CI status page
    :target: https://travis-ci.org/avalentino/geomodels

.. image:: https://img.shields.io/pypi/v/geomodels
    :alt: Latest Version
    :target: https://pypi.org/project/geomodels

.. image:: https://img.shields.io/pypi/pyversions/geomodels
    :alt: Supported Python versions
    :target: https://pypi.org/project/geomodels

.. image:: https://img.shields.io/pypi/l/geomodels
    :alt: License
    :target: https://pypi.org/project/geomodels


About
=====

GeoModels provides tools for the management of Earth models like
geoids, gravity models, and magnetic field models.

It also provides some utility function to download and install support
data to that are necessary for Earth models computation.

It is basically a Cython_ wrapper for part of the the GeographicLib_
C++ library.

.. _GeographicLib: https://geographiclib.sourceforge.io
.. _Cython: https://cython.org


Installation
============

The GeoModels requires `Python`_ >= 3.6.
To use GeoModels it is necessary to have the following Python_ packages
installed:

* `numpy <https://numpy.org>`_
* `tqdm <https://github.com/tqdm/tqdm>`_ (optional)
* `argcomplete <https://github.com/kislyuk/argcomplete>`_ (optional)

The `geomodels` package provides some binary extensions so the
installation from sources also requires:

* `Cython`_
* a C/C++ compiler
* `GeographicLib`_ >= 1.49

The required Python_ packages are automatically installed installed by Pip_
and setuptools_ but the user is in charge of ensuring that the C++ compiler
and `GeographicLib`_ are properly installed and configured.

.. note::

    if `GeographicLib`_ is installed into a non-standard path,
    the used shall set the environment (e.g. `CPPFLAGS`, `CXXFLAGS` and
    `LDFLAGS` for the GNU GCC) to allow the compiler to find the
    `GeographicLib`_ header files and libraries.

    Also, in this case, the used shall configure the environment to allow
    the system to find and load `GeographicLib`_ shared library (e.g. by
    setting the `LD_LIBRARY_PATH` on GNU/Linux systems).


The installation form sources can be done using the following command::

  $ python3 -m pip install PATH_TO_GEOMODELS_SOURCES_OR_TARBALL

Please refer to the Pip_ user manual for details about installation options.

Developers may want to build the package inplace for development and
testing purposes.  In this case the following command can be used from
within the root of the package source tree::

  $ python3 setup.py build_ext --inplace

.. _Python: https://www.python.org
.. _Pip: https://pip.pypa.io
.. _setuptools: https://github.com/pypa/setuptools


Testing
=======

The recommended way to run tests is to use `PyTest`_ form the root of the
`geomodels` package source tree::

  $ python3 -m pytest

The above, of course, requires the `PyTest`_ to be installed.

In alternative the following command can be used::

  $ python3 setup.py test

.. note::

    running tests requires that model data, used by the underlying
    GeographicLib_, are correctly installed in the default system location.

    More in detail, the following data models are sued for testing:

    :geoid data:
        'egm96-5', and data for the default model
    :gravity data:
        'egm96', and data for the default model
    :magnetic field data:
        'wmm2015', 'igrf12' and data for the default model


.. _PyTest: http://pytest.org


License
=======

GeoModels is released under the terms of the `MIT/X11 License`_
(see LICENSE file).

.. _`MIT/X11 License`: https://opensource.org/licenses/MIT
