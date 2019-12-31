GeoModels
=========

:copyright: 2019-2020 Antonio Valentino
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
-----

GeoModels provides tools for the management of Earth models like
geoids, gravity models, and magnetic field models.

It also provides some utility function to download and install support
data to that are necessary for Earth models computation.

It is basically a Cython_ wrapper for part of the the GeographicLib_
C++ library.

.. _GeographicLib: https://geographiclib.sourceforge.io
.. _Cython: https://cython.org


Installation
------------

The GeoModels requires `Python`_ >= 3.6.
To use GeoModels depends on the following Python_ packages:

* `numpy <https://numpy.org>`_
* `tqdm <https://github.com/tqdm/tqdm>`_ (optional)
* `argcomplete <https://github.com/kislyuk/argcomplete>`_ (optional)

The required Python_ packages are automatically installed installed by
Pip_ and setuptools_::

  $ python3 -m pip install geomodels

Please refer to the Pip_ user manual for details about installation
options and to the :doc:`installation` section in the documentation
for details about installation form sources.

.. _Python: https://www.python.org
.. _Pip: https://pip.pypa.io
.. _setuptools: https://github.com/pypa/setuptools


Model data installation
-----------------------

GeoModels uses external data to perform geoid, gravity and magnetic
field computations.

If required data are not already available on the system than they can
be downloaded and installed using the command line interface provided
by the GeoModels package::

  $ python -m geomodels install-data [-d DATADIR] recommended

The above command installs the `recommended` subset of data (about 20MB)
into the specified `DATAROOT`folder.
If `DATAROOT` is not explicitly specified using the `-d` (or `--datadir`)
option then the default system path is used (e.g.
`/usr/local/share/GeographicLib`).

In any case it is necessary to have write permission on the `DATADIR`
folder, so to install into the default system path it will be probably
necessary to use `sudo` or some equivalent method.

If data are not installed into the default system folder than it is
necessary to set the `GEOGRAPHICLIB_DATA` environment variable to the
data installation path to allow GeographicLib_ to find data.
E.g., on systems using bash one can use the following command::

  export GEOGRAPHICLIB_DATA=/path/to/data


Testing
-------

Once the GeoModels package and necessary data have been installed, it
is possible to run the test suite to be sure that all works correctly.
The recommended way to test GeoModels with using PyTest_::

  $ env GEOGRAPHICLIB_DATA=/path/to/data \
    python3 -m pytest --pyargs geomodels

.. _PyTest: http://pytest.org


Usage example
-------------

.. doctest::

   >>> from geomodels import GeoidModel
   >>> geoid = GeoidModel()
   >>> geoid.description()
   'WGS84 EGM96, 5-minute grid'
   >>> geoid(lat=40.667, lon=16.6)  # -> geoid height
   45.914894760480024


License
-------

GeoModels is released under the terms of the `MIT/X11 License`_
(see LICENSE file).

.. _`MIT/X11 License`: https://opensource.org/licenses/MIT
