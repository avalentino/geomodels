Command line interface
======================

The GeoModel package also provides a command line interface that can be
used to:

* display information about the:

  - GeoModels version and GeographicLib_ library version
  - platform and environment info
  - data directory and installed model data

* install model data that are used by the GeoModels and by the
  underlying GeographicLib_ library to perform geographic models
  computations
* import magnetic field spherical harmonics coefficients for IGRF format
* run the test suite

.. _GeographicLib: https://geographiclib.sourceforge.io


Invocation
----------

The GeoModels package provides a script named `geomodels-cli` which can
be run as follows::

  $ geomodels-cli [OPTIONS] ARGS

An alternative invocation method is::

  $ python3 -m geomodels [OPTIONS] ARGS


Main command line interface
---------------------------

The online help of the main command line interface can be obtained as
follows::

  $ geomodels-cli -h

  usage: geomodels [-h] [--version]
                   [--loglevel {DEBUG,INFO,WARNING,ERROR,CRITICAL}]
                   [-q] [-v] [--debug]
                   {info,install-data,import-igrf,test} ...

  Command Line Interface (CLI) for the geomodels package.

  optional arguments:
    -h, --help            show this help message and exit
    --version             show program's version number and exit
    --loglevel {DEBUG,INFO,WARNING,ERROR,CRITICAL}
                          logging level (default: WARNING)
    -q, --quiet           suppress standard output messages, only
                          errors are printed to screen (set
                          "loglevel" to "ERROR")
    -v, --verbose         print verbose output messages (set
                          "loglevel" to "INFO")
    --debug               print debug messages (set "loglevel" to
                          "DEBUG")

  sub-commands:
    {info,install-data,test}
      info                Provide information about the platform,
                          library versions and
      install-data        Download and install the data necessary for
                          models computation.
      import-igrf         import magnetic field data from igrf text format.
      test                run the test suite for the geomodels
                          package.

.. note::

   Please note that options for logging level configuration shall
   precede the sub-command name and specific sub-command options,
   e.g.::

     $ geomodels-cli --debug test


Example output::

  $ geomodels-cli --version

  geomodels v1.0.0


Info tool
---------

The online help of the "info" tool::

  $ geomodels-cli info -h

  usage: geomodels info [-h] [-d DATADIR] [-a] [--data]

  Provide information about the platform, library versions and
  installed data.

  optional arguments:
    -h, --help            show this help message and exit
    -d DATADIR, --datadir DATADIR
                          specifies where the model data are stored
                          (default: '/usr/local/share/GeographicLib').
    -a, --all             show both versions and platform info and
                          also information about installed data
    --data                show info about installed data


Sample output::

  $ geomodels-cli info --all

  geomodels version:     1.0.0
  GeographicLib version: 1.50.1
  Python version:        3.7.5
  Platform:              Linux-5.3.0-26-generic-x86_64-with-Ubuntu-19.10-eoan
  Byte-ordering:         little
  Default encoding:      utf-8
  Default FS encoding:   utf-8
  Default locale:        (it_IT, UTF-8)

  data directory: 'data/'
  * model: geoids ('data/geoids')
    EGM84_30     - NOT INSTALLED
    EGM84_15     - NOT INSTALLED
    EGM96_15     - NOT INSTALLED
    EGM96_5      - INSTALLED
    EGM2008_5    - NOT INSTALLED
    EGM2008_2_5  - NOT INSTALLED
    EGM2008_1    - NOT INSTALLED
  * model: gravity ('data/gravity')
    EGM84        - NOT INSTALLED
    EGM96        - INSTALLED
    EGM2008      - NOT INSTALLED
    WGS84        - NOT INSTALLED
  * model: magnetic ('data/magnetic')
    WMM2010      - NOT INSTALLED
    WMM2015      - INSTALLED
    WMM2020      - INSTALLED
    IGRF11       - NOT INSTALLED
    IGRF12       - INSTALLED
    EMM2010      - NOT INSTALLED
    EMM2015      - NOT INSTALLED
    EMM2017      - NOT INSTALLED


Install data tool
-----------------

The online help of the "install-data" tool::

  $ geomodels-cli install-data -h

  usage: geomodels install-data [-h] [-b BASE_URL] [-d DATADIR]
                                {all,minimal,recommended,geoids,
                                 gravity, magnetic,egm84-30,egm84-15,
                                 egm96-15,egm96-5, egm2008-5,
                                 egm2008-2_5,egm2008-1,egm84,egm96,
                                 egm2008,wgs84,wmm2010,wmm2015,
                                 wmm2020,igrf11, igrf12,emm2010,
                                 emm2015,emm2017}

  Download and install the data necessary for models computation.
  GeoModels uses external data to perform geoid, gravity and magnetic
  field computations. It is possible to install different subsets of
  data:
  `minimal` only data for the default model of each kind
  (geoid, gravity and magnetic field) are installed,
  `recommended` install the `minimal` set of data (see above) plus
  few additional and commonly used data (it is guaranteed that the
  `recommended` subset always includes all data that are necessary to
  run the test suite),
  `all` install all available data (about 670MB of disk space
  required),
  `geoids` install data for all supported geoids,
  `gravity` install data for all supported gravity models,
  `magnetic` install data for all supported magnetic field models.
  Additionally the it is possible to install data for a single model.

  positional arguments:
    {all,minimal,recommended,geoids,gravity,magnetic,egm84-30,
     egm84-15,egm96-15,egm96-5,egm2008-5,egm2008-2_5,egm2008-1,egm84,
     egm96,egm2008, wgs84,wmm2010,wmm2015,wmm2020,igrf11,igrf12,
     emm2010,emm2015,emm2017}
                          model(s) to be installed

  optional arguments:
    -h, --help            show this help message and exit
    -b BASE_URL, --base-url BASE_URL
                          specifies the base URL for the download
                          (default:
                           'https://downloads.sourceforge.net/project/geographiclib').
    -d DATADIR, --datadir DATADIR
                          specifies where the datasets should be
                          stored (default:
                          '/usr/local/share/GeographicLib').


Import IGRF data tool
---------------------

The online help of the "import-igrf" tool::

  $ python3 -m geomodels import-igrf -h
  usage: geomodels-cli import-igrf [-h] [-o OUTPATH] [--force] path

  Import magnetic field data from IGRF text format.

  positional arguments:
    path                  path or URL of the IGRF text file

  optional arguments:
    -h, --help            show this help message and exit
    -o OUTPATH, --outpath OUTPATH
                          specifies the output data path (default:
                          "/usr/share/GeographicLib/magnetic").
    --force               overwrite existing files (default: False).


Test tool
---------

The online help of the "test" tool::

  $ geomodels-cli test -h

  usage: geomodels test [-h] [-d DATADIR] [--verbosity VERBOSITY]
                        [--failfast]

  Run the test suite for the geomodels package.

  optional arguments:
    -h, --help            show this help message and exit
    -d DATADIR, --datadir DATADIR
                          specifies where the model data are stored
                          (default: '/usr/local/share/GeographicLib').
    --verbosity VERBOSITY
                          verbosity level for the unittest runner
                          (default: 1).
    --failfast            stop the test run on the first error or
                          failure (default: False).

Sample output::

  $ geomodels-cli test

  geomodels version:     1.0.0
  GeographicLib version: 1.50.1
  Python version:        3.7.5
  Platform:              Linux-5.3.0-26-generic-x86_64-with-Ubuntu-19.10-eoan
  Byte-ordering:         little
  Default encoding:      utf-8
  Default FS encoding:   utf-8
  Default locale:        (it_IT, UTF-8)

  ............................................................................
  ............................................................................
  ........
  ----------------------------------------------------------------------
  Ran 160 tests in 0.450s

  OK
