Installation and Testing
========================

.. highlight:: sh

The GeoModels requires `Python`_ >= 3.10.
To use GeoModels depends on the following Python_ packages:

* `numpy <https://numpy.org>`_
* `tqdm <https://github.com/tqdm/tqdm>`_ (optional)
* `argcomplete <https://github.com/kislyuk/argcomplete>`_ (optional)

The required Python_ packages are automatically installed installed by
Pip_ and setuptools_::

  $ python3 -m pip install geomodels

Please refer to the Pip_ user manual for details about installation
options.

.. _Python: https://www.python.org
.. _Pip: https://pip.pypa.io
.. _setuptools: https://github.com/pypa/setuptools


Installation from sources
-------------------------

The GeoModels package provides some binary extensions so the installation
from sources also requires:

* Cython_
* a C++11 compiler
* GeographicLib_ >= 2.0

The user is in charge of ensuring that the C++ compiler is properly installed
and configured.

GeographicLib_ is bundled with the source tarball available on PyPi_ and
included in the source tree available on the GeoModels `repository`_
on GitHub_.

The installation from sources can be done using the following command
from the root directory of the source tree::

  $ python3 -m pip install .

Please refer to the Pip_ documentation for details about installation
options.

.. _GeographicLib: https://geographiclib.sourceforge.io
.. _Cython: https://cython.org
.. _PyPI: https://pypi.org
.. _repository: https://github.com/avalentino/geomodels.git
.. _GitHub: https://github.com


Using the system GeographicLib_
-------------------------------

In some cases it is desirable to use the system provided GeographicLib_.

Of course in this case the user is in charge of ensuring that GeographicLib_
is properly installed and configured.
On Debian_ based systems (including Ubuntu_) GeographicLib_ (and its
development files) can be installed as follows::

  $ sudo apt install libgeographic-dev

To ensure that the system version of the libraries is used instead of
the bundled copy of GeographicLib_ the `GEOMODELS_FORCE_SYSTEM_LIBS`
environment variable shall be set to `TRUE` as in the following example::

  $ env GEOMODELS_IGNORE_BUNDLED_LIBS=TRUE python3 -m pip install .

Starting from GeographicLib v2.0 the name of the dynamic library has been
changed from `libGeographic.so` to `libGeographicLib.so`.
By default GeoModels uses the new name (and this is the reason why
GeograohicLin >= 2.0 is required), but it is also possible to build geomodels
against GeographicLib >= 1.52. In the latter case the
`GEOMODELS_GEOGRAPHICLIB_NAME` environment variable shall be used to set The
name of the dynamic library::

  $ export GEOMODELS_GEOGRAPHICLIB_NAME=Geographic

note, that the `lib` prefix and the `.so` (`.dylib` on Mac OS-X) extension
are not specified.

Also in this case, please refer to the Pip_ documentation for
details about installation options.

.. note::

   if GeographicLib_ is installed into a non-standard path,
   the used shall set the environment (e.g. `CPPFLAGS`, `CXXFLAGS` and
   `LDFLAGS` for the GNU GCC) to allow the compiler to find the
   GeographicLib_ header files and libraries.

   Also, in this case, the user shall configure the environment to
   allow the system to find and load `GeographicLib`_ shared library
   (e.g. by setting the `LD_LIBRARY_PATH` on GNU/Linux systems).

   Example::

     $ env CPPFLAGS="-I${HOME}/.local/include" \
           LDFLAGS="-L${HOME}/.local/lib" \
	   python3 -m pip install .


.. _Debian: https://www.debian.org
.. _Ubuntu: https://ubuntu.com


Model data installation
-----------------------

GeoModels uses external data to perform geoid, gravity and magnetic
field computations.

If required data are not already available on the system than they can
be downloaded and installed using the command line interface provided
by the GeoModels package::

  $ python3 -m geomodels install-data [-d DATADIR] recommended

The above command installs the `recommended` subset of data (about 20MB)
into the specified `DATAROOT` folder.

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

Please note that with the command line interface it is possible to
install different subsets of data:

:minimal:
    only data for the default model of each kind (geoid, gravity and
    magnetic field) are installed. If GeographicLib_ v1.5.1 is used
    then installed data are: geoids/egm96-5, gravity/egm96 and
    magnetic/wmm2020 (about 20MB)
:recommended:
    the `minimal` set of data (see above) plus few additional and
    commonly used data (magnetic/igrf12).
    The total amount of disk space required is about 20MB.
    It is guaranteed that the `recommended` subset always includes all
    data that are necessary to run the test suite.
:all:
    install all available data (about 645MB of disk space are required)
:geoids:
    install data for all supported geoids
:gravity:
    install data for all supported gravity models
:magnetic:
    install data for all supported magnetic field models

Additionally the command line interface allows also to install data for
a single model. See the command line help for details::

  $ python3 -m geomodels install-data -h

Please refer to :doc:`cli` for a complete description of the command
line interface.


Testing
-------

Once the GeoModels package, and `recommended` data (see above), have been
installed, it is possible to run the test suite to be sure that all works
correctly.

The recommended way to test GeoModels with using PyTest_::

  $ env GEOGRAPHICLIB_DATA=/path/to/data \
    python3 -m pytest --pyargs geomodels

.. _PyTest: http://pytest.org
