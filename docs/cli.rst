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

  usage: geomodels-cli [-h] [--version]
                       [--loglevel {DEBUG,INFO,WARNING,ERROR,CRITICAL}]
                       [-q] [-v] [--debug]
                      {info,install-data,import-igrf} ...

  Command Line Interface (CLI) for the geomodels Python package.

  options:
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
    {info,install-data,import-igrf}
      info                Provide information about the installation
                          and environment.
      install-data        Download and install the data necessary for
                          models computation.
      import-igrf         Import magnetic field data from IGRF text format.

.. note::

   Please note that options for logging level configuration shall
   precede the sub-command name and specific sub-command options,
   e.g.::

     $ geomodels-cli --debug info


Example output::

  $ geomodels-cli --version

  geomodels-cli v1.0.0


Info tool
---------

The online help of the "info" tool::

  $ geomodels-cli info -h

  usage: geomodels-cli info [-h] [-d DATADIR] [-a] [--data]

  Provide information about the installation and environment.
  Information provided include: the platform, the library
  versions and installed data.

  options:
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
  GeographicLib version: 2.5
  GEOGRAPHICLIB_DATA:    data
  Python version:        3.12.7
  Platform:              Linux-6.11.0-13-generic-x86_64-with-glibc2.40
  Byte-ordering:         little
  Default encoding:      utf-8
  Default FS encoding:   utf-8
  Locale:                ('it_IT', 'UTF-8')

  data directory: 'data'
  * model: geoids ('data/geoids')
    EGM84_30     - INSTALLED
    EGM84_15     - INSTALLED
    EGM96_15     - INSTALLED
    EGM96_5      - INSTALLED
    EGM2008_5    - INSTALLED
    EGM2008_2_5  - INSTALLED
    EGM2008_1    - INSTALLED
  * model: gravity ('data/gravity')
    EGM84        - INSTALLED
    EGM96        - INSTALLED
    EGM2008      - INSTALLED
    GRS80        - INSTALLED
    WGS84        - INSTALLED
  * model: magnetic ('data/magnetic')
    WMM2010      - INSTALLED
    WMM2015      - INSTALLED
    WMM2015V2    - INSTALLED
    WMM2020      - INSTALLED
    WMM2025      - INSTALLED
    WMMHR2025    - INSTALLED
    IGRF11       - INSTALLED
    IGRF12       - INSTALLED
    IGRF13       - INSTALLED
    IGRF14       - INSTALLED
    EMM2010      - INSTALLED
    EMM2015      - INSTALLED
    EMM2017      - INSTALLED


Install data tool
-----------------

The online help of the "install-data" tool::

  $ geomodels-cli install-data -h

  usage: geomodels-cli install-data [-h] [-b BASE_URL] [-d DATADIR]
                                    [--no-progress]
                                    {all,minimal,recommended,geoids,
                                     gravity,magnetic,egm84-30,egm84-15,
                                     egm96-15,egm96-5,egm2008-5,
                                     egm2008-2_5,egm2008-1,egm84,egm96,
                                     egm2008,grs80,wgs84,wmm2010,wmm2015,
                                     wmm2015v2,wmm2020,wmm2025,wmmhr2025,
                                     igrf11,igrf12,igrf13,igrf14,
                                     emm2010,emm2015,emm2017}

  Download and install the data necessary for models computation.

      GeoModels uses external data to perform geoid, gravity and magnetic
      field computations.

      It is possible to install different subsets of data:

      :minimal:
          only data for the default model of each kind (geoid,
          gravity and magnetic field) are installed,
      :recommended:
          install the `minimal` set of data (see above) plus few
          additional and commonly used data (it is guaranteed that
          the `recommended` subset always includes all data that
          are necessary to run the test suite),
      :all:
          install all available data (about 670MB of disk space
          required),
      :geoids:
          install data for all supported geoids,
      :gravity:
          install data for all supported gravity models,
      :magnetic:
          install data for all supported magnetic field models.

      Additionally the it is possible to install data for a single model.


  positional arguments:
    {all,minimal,recommended,geoids,gravity,magnetic,egm84-30,
     egm84-15,egm96-15,egm96-5,egm2008-5,egm2008-2_5,egm2008-1,egm84,
     egm96,egm2008,grs80,wgs84,wmm2010,wmm2015,wmm2015v2,wmm2020,
     wmm2025,wmmhr2025,igrf11,igrf12,igrf13,igrf14,emm2010,emm2015,emm2017}
                          model(s) to be installed

  options:
    -h, --help            show this help message and exit
    -b BASE_URL, --base-url BASE_URL
                          specifies the base URL for the download (default:
                          https://downloads.sourceforge.net/project/geographiclib).
    -d DATADIR, --datadir DATADIR
                          specifies where the datasets should be stored
                          (default: '/usr/local/share/GeographicLib').
    --no-progress         suppress progress bar display


Import IGRF data tool
---------------------

The online help of the "import-igrf" tool::

  $ geomodels-cli import-igrf -h

  usage: geomodels-cli import-igrf [-h] [-o OUTPATH] [--force] path

  Import magnetic field data from IGRF text format.
  Import Spherical Harmonics coefficients for the IGRF
  magnetic field model from text file in IGRF standard format.
  See: https://www.ngdc.noaa.gov/IAGA/vmod/igrf.html.

  positional arguments:
    path                  path or URL of the IGRF text file

  options:
    -h, --help            show this help message and exit
    -o OUTPATH, --outpath OUTPATH
                          specifies the output data path (default:
                          "/usr/local/share/GeographicLib/magnetic").
    --force               overwrite existing files (default: False).
