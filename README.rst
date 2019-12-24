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

  $ python3 -m pip install geomodels

Please refer to the Pip_ user manual for details about installation options.

.. _Python: https://www.python.org
.. _Pip: https://pip.pypa.io
.. _setuptools: https://github.com/pypa/setuptools


Model data installation
-----------------------

GeoModels uses external data to perform geoid, gravity and magnetic field
computations.

If required data are not already available on the system that thay can be
downloaded and installed using the `geomodels-download` command line tool
that is provided by the GeoTools package::

  $ geomodels-download [-d DATADIR] recommended

The above command installs the `recommended` subset of data (about 20MB)
into the specified `DATAROOT`folder.
If `DATAROOT` is not explicitly specified using the `-d` (or `--datadir`)
option then the default system path is used (e.g.
`/usr/local/share/GeographicLib`).

In any case it is necessary to have write permission on the `DATADIR` folder,
so to install into the default system path it will be probably necessary to
use `sudo` or some equivalent method.

If data are not installed into the default system folder than it is necessary
to set the `GEOGRAPHICLIB_DATA` environment variable to the data installation
path. E.g., on systems using bash one can use the following command::

  export GEOGRAPHICLIB_DATA=/path/to/data

Please note that with the `geomodels-download` command line tool it is
possible to install different subsets of data:

:minimal:
    only data for the default model of each kind (geoid, gravity and magnetic
    field) are installed. If GeographicLib_ v1.5.1 is used then installed
    data are: geoids/egm96-5, gravity/egm96 and magnetic/wmm2020 (about 20MB)
:recommended:
    the `minimal` set of data (see above) plus few additional and commonly
    used data (magnetic/igrf12).
    The total amount of disk space required is about 20MB.
    It is guaranteed that the `recommended` subset always includes all data
    that are necessary to run the test suite.
:all:
   install all available data (about 670MB of disk space are required)

Additionally the `geomodels-download` command line tool allows also to install
data for a single model. See the command line help for details::

  $ geomodels-download -h


Testing
-------

Once the GeoModels package and necessary data have been installed, it is
possible to run the test suite to be sure that all works correctly.
The recommended way to test GeoModels with using PyTest_::

  $ env GEOGRAPHICLIB_DATA=/path/to/data python3 -m pytest --pyargs geomodels

.. _PyTest: http://pytest.org


License
=======

GeoModels is released under the terms of the `MIT/X11 License`_
(see LICENSE file).

.. _`MIT/X11 License`: https://opensource.org/licenses/MIT
