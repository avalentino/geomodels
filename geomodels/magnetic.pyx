# -*- coding: utf-8 -*-
# cython: language_level=3
# distutils: language=c++

"""Model of the earth's magnetic field.

Evaluate the earth's magnetic field according to a model.  At present only
internal magnetic fields are handled.  These are due to the earth's code
and crust; these vary slowly (over many years).  Excluded are the effects
of currents in the ionosphere and magnetosphere which have daily and
annual variations.

See:

* General information:
  - http://geomag.org/models/index.html
* WMM2010:
  - https://ngdc.noaa.gov/geomag/WMM/DoDWMM.shtml
  - https://ngdc.noaa.gov/geomag/WMM/data/WMM2010/WMM2010COF.zip
* WMM2015:
  - https://ngdc.noaa.gov/geomag/WMM/DoDWMM.shtml
  - https://ngdc.noaa.gov/geomag/WMM/data/WMM2015/WMM2015COF.zip
* IGRF11:
  - https://ngdc.noaa.gov/IAGA/vmod/igrf.html
  - https://ngdc.noaa.gov/IAGA/vmod/igrf11coeffs.txt
  - https://ngdc.noaa.gov/IAGA/vmod/geomag70_linux.tar.gz
* EMM2010:
  - https://ngdc.noaa.gov/geomag/EMM/index.html
  - https://ngdc.noaa.gov/geomag/EMM/data/geomag/EMM2010_Sph_Windows_Linux.zip
* EMM2015:
  - https://ngdc.noaa.gov/geomag/EMM/index.html
  - https://www.ngdc.noaa.gov/geomag/EMM/data/geomag/EMM2015_Sph_Linux.zip
* EMM2017:
  - https://ngdc.noaa.gov/geomag/EMM/index.html
  - https://www.ngdc.noaa.gov/geomag/EMM/data/geomag/EMM2017_Sph_Linux.zip
"""

import os
import numpy as np

cimport cython
from libcpp.string cimport string


cdef extern from "GeographicLib/MagneticModel.hpp" namespace "GeographicLib":
    cdef cppclass MagneticModel:
        ctypedef double real
        MagneticModel(const string& name, const string& path) nogil except +
        # @TODO: const Geocentric& earth=Geocentric.WGS84()

        void operator()(real t, real lat, real lon, real h,
                        real& Bx, real& By, real& Bz) nogil const
        void operator()(real t, real lat, real lon, real h,
                        real& Bx, real& By, real& Bz,
                        real& Bxt, real& Byt, real& Bzt) nogil const

        # MagneticCircle Circle(real t, real lat, real h) const

        @staticmethod
        void FieldComponents(real Bx, real By, real Bz,
                             real& H, real& F, real& D, real& I) nogil

        # @staticmethod
        # void FieldComponents(real Bx, real By, real Bz,
        #                      real Bxt, real Byt, real Bzt,
        #                      real& H, real& F, real& D, real& I,
        #                      real& Ht, real& Ft, real& Dt, real& It) nogil

        const string& Description() const
        const string& DateTime() const
        const string& MagneticFile() const
        const string& MagneticModelName() const
        const string& MagneticModelDirectory() const

        real MinHeight() const
        real MaxHeight() const
        real MinTime() const
        real MaxTime() const
        real MajorRadius() const
        real Flattening() const

        @staticmethod
        string DefaultMagneticPath()

        @staticmethod
        string DefaultMagneticName();


cdef class MagneticFieldModel:
    """Magnetic Field Model.

    :param str name:
        the name of the model
    :param path:
        (optional) directory for data file
    :raises GeographicErr:
         if the data file cannot be found, is unreadable, or is corrupt
    :raises MemoryError:
         if the memory necessary for storing the model can't be allocated

    A filename is formed by appending ".wmm" (World Magnetic Model) to
    the name.  If path is specified (and is non-empty), then the file
    is loaded from directory, path.  Otherwise the path is given by the
    DefaultMagneticPath().

    This file contains the metadata which specifies the properties of the
    model.  The coefficients for the spherical harmonic sums are obtained
    from a file obtained by appending ".cof" to metadata file (so the
    filename ends in ".wwm.cof").

    The model is not tied to a particular ellipsoidal model of the earth.
    The final earth argument to the constructor specifies an ellipsoid to
    allow geodetic coordinates to the transformed into the spherical
    coordinates used in the spherical harmonic sum.
    """
    cdef MagneticModel *_ptr

    def __cinit__(self, name, path=''):
        # @TODO: support for 'earth' parameter (default: WGS84)
        cdef string c_name = os.fsencode(name)
        cdef string c_path = os.fsencode(path)

        with nogil:
            self._ptr = new MagneticModel(c_name, c_path)

    def __dealloc__(self):
        del self._ptr

    @cython.boundscheck(False)
    @cython.wraparound(False)
    def __call__(self, double t, lat, lon, h, bint time_derivatives=False):
        """Compute the magnetic field.

        Evaluate the components of the geomagnetic field and
        (optionally) their time derivatives

        :param t:
            the time (years)
        :param lat:
            latitude of the point (degrees)
        :param lon:
            longitude of the point (degrees)
        :param h:
            the height of the point above the ellipsoid (meters)
        :param bool time_derivatives:
            also returns time derivatives of the magnetic field
        :returns:
            Bx, By, Bz: the easterly, northerly and vertical (up)
            components of the magnetic field (nanotesla).

            If time_derivativesis set to True then the following touple
            is returned: (Bx, By, Bz, Bxt, Byt, Bzt), where  Bxt, Byt
            and Bzt are the rate of change of Bx, By and Bz
            respectively (nT/yr).
        """
        cdef bint is_scalar = np.isscalar(h)

        lat = np.asarray(lat)
        lon = np.asarray(lon)
        h = np.asarray(h)

        for name, param in (('lat', lat), ('lon', lon), ('h', h)):
            dt = param.dtype
            if not (np.issubdtype(dt, np.floating) or
                    np.issubdtype(dt, np.integer)):
                raise TypeError('{}: {!r}}'.format(name, param))

        shape = h.shape
        if lat.shape != shape or lon.shape != shape:
            raise ValueError('lat, lon and h shall have the same shape')

        cdef long size = h.size
        dtype = np.float64

        lat = np.ascontiguousarray(lat.reshape([size]), dtype=dtype)
        lon = np.ascontiguousarray(lon.reshape([size]), dtype=dtype)
        h = np.ascontiguousarray(h.reshape([size]), dtype=dtype)

        Bx = np.empty(shape=[size], dtype=dtype)
        By = np.empty(shape=[size], dtype=dtype)
        Bz = np.empty(shape=[size], dtype=dtype)

        cdef double[::1] vlat = lat
        cdef double[::1] vlon = lon
        cdef double[::1] vh = h

        cdef double[::1] vBx = Bx
        cdef double[::1] vBy = By
        cdef double[::1] vBz = Bz
        cdef double[::1] vBxt
        cdef double[::1] vByt
        cdef double[::1] vBzt

        cdef long i = 0

        if not time_derivatives:
            with nogil:
                for i in range(size):
                    cython.operator.dereference(self._ptr)(
                        t, vlat[i], vlon[i], vh[i], vBx[i], vBy[i], vBz[i])

            if is_scalar:
                Bx = np.asscalar(Bx)
                By = np.asscalar(By)
                Bz = np.asscalar(Bz)
            else:
                Bx = Bx.reshape(shape)
                By = By.reshape(shape)
                Bz = Bz.reshape(shape)

            return Bx, By, Bz
        else:
            Bxt = np.empty(shape=shape, dtype=dtype)
            Byt = np.empty(shape=shape, dtype=dtype)
            Bzt = np.empty(shape=shape, dtype=dtype)

            vBxt = Bxt
            vByt = Byt
            vBzt = Bzt

            with nogil:
                for i in range(size):
                    cython.operator.dereference(self._ptr)(
                        t, vlat[i], vlon[i], vh[i],
                        vBx[i], vBy[i], vBz[i],
                        vBxt[i], vByt[i], vBzt[i])

            if is_scalar:
                Bx = np.asscalar(Bx)
                By = np.asscalar(By)
                Bz = np.asscalar(Bz)

                Bxt = np.asscalar(Bxt)
                Byt = np.asscalar(Byt)
                Bzt = np.asscalar(Bzt)
            else:
                Bx = Bx.reshape(shape)
                By = By.reshape(shape)
                Bz = Bz.reshape(shape)

                Bxt = Bxt.reshape(shape)
                Byt = Bxt.reshape(shape)
                Bzt = Bxt.reshape(shape)

            return Bx, By, Bz, Bxt, Byt, Bzt

    # @TODO: MagneticCircle Circle(real t, real lat, real h) const
    # def circle(...):
    #     """Create a MagneticCircle object.
    #
    #     A MagneticCircle object to allow the geomagnetic field at many
    #     points with constant \e lat, \e h, and \e t and varying `lon`
    #     to be computed efficiently.
    #
    #     :param t:
    #         the time (years).
    #     :param lat:
    #         latitude of the point (degrees).
    #     :param h:
    #         the height of the point above the ellipsoid (meters).
    #     :raises MenoryError:
    #         if the memory necessary for creating a MagneticCircle
    #         can't be allocated.
    #     :returns:
    #         a MagneticCircle object whose MagneticCircle.__call__(lon)
    #         member function computes the field at particular values of
    #         `lon`.
    #
    #     If the field at several points on a circle of latitude need to be
    #     calculated then creating a MagneticCircle and using its member
    #     functions will be substantially faster, especially for high-degree
    #     models.
    #     """
    #     pass

    @staticmethod
    def field_components(double Bx, double By, double Bz):
        """Compute various quantities dependent on the magnetic field.

        :param float Bx:
            the x (easterly) component of the magnetic field (nT)
        :param float By:
            the y (northerly) component of the magnetic field (nT)
        :param float Bz:
            the z (vertical, up positive) component of the magnetic field (nT)
        :returns:
            * H the horizontal magnetic field (nT)
            * F the total magnetic field (nT)
            * D the declination of the field (degrees east of north)
            * I the inclination of the field (degrees down from horizontal)
        """
        cdef double H=0, F=0, D=0, I=0
        with nogil:
            MagneticModel.FieldComponents(Bx, By, Bz, H, F, D, I)
        return H, F, D, I

    # @staticmethod
    # def field_components_and_rate(double Bx, double By, double Bz,
    #                               double Bxt, double Byt, double Bzt):
    #     """Compute quantities dependent on the magnetic field and its rate
    #     of change.
    #
    #     :param float Bx:
    #         the x (easterly) component of the magnetic field (nT)
    #     :param float By:
    #         the y (northerly) component of the magnetic field (nT)
    #     :param float Bz:
    #         the z (vertical, up positive) component of the magnetic field (nT)
    #     :param float Bxt:
    #         the rate of change of Bx (nT/yr)
    #     :param float Byt:
    #         the rate of change of By (nT/yr)
    #     :param float Bzt:
    #         the rate of change of Bz (nT/yr)
    #
    #     :returns:
    #         * H the horizontal magnetic field (nT)
    #         * F the total magnetic field (nT)
    #         * D the declination of the field (degrees east of north)
    #         * I the inclination of the field (degrees down from horizontal)
    #         * Ht the rate of change of H (nT/yr)
    #         * Ft the rate of change of F (nT/yr)
    #         * Dt the rate of change of D (degrees/yr)
    #         * It the rate of change of I (degrees/yr)
    #     """
    #     cdef double H=0, F=0, D=0, I=0, Ht=0, Ft=0, Dt=0, It=0
    #     with nogil:
    #         MagneticModel.FieldComponents(Bx, By, Bz, Bxt, Byt, Bzt,
    #                                       H, F, D, I, Ht, Ft, Dt, It)
    #     return H, F, D, I, Ht, Ft, Dt, It

    def description(self) -> str:
        """Return the description of the magnetic model.

        Return the description of the magnetic model if available,
        from the Description file in the data file;
        if absent, return "NONE".
        """
        return self._ptr.Description().decode('utf-8')

    def datetime(self) -> str:
        """Return date of the model.

        Return date of the model, if available, from the ReleaseDate
        field in the data file; if absent, return "UNKNOWN".
        """
        return self._ptr.DateTime().decode('utf-8')

    def magnetic_file(self) -> str:
        """Full file name used to load the magnetic model."""
        return self._ptr.MagneticFile().decode('urf-8')

    def magnetic_model_name(self) -> str:
        """Name used to load the magnetic model.

        The 'name' used to load the magnetic model (from the first
        argument of the constructor, but this may be overridden by
        the model file).
        """
        return self._ptr.MagneticModelName().decode('utf-8')

    def magnetic_model_directory(self) -> str:
        """Directory used to load the magnetic model."""
        return self._ptr.MagneticModelDirectory().decode('utf-8')

    def min_height(self) -> float:
        """Minimum height.

        The minimum height above the ellipsoid (in meters) for which
        this MagneticModel should be used.

        Because the model will typically provide useful results
        slightly outside the range of allowed heights,
        no check of t argument is made by the MagneticModel.__call__()
        operator.
        """
        return self._ptr.MinHeight()

    def max_height(self) -> float:
        """Maximum height.

        The maximum height above the ellipsoid (in meters) for which
        this MagneticModel should be used.

        Because the model will typically provide useful results
        slightly outside the range of allowed heights,
        no check of t argument is made by the MagneticModel.__call__()
        operator.
        """
        return self._ptr.MaxHeight()

    def min_time(self) -> float:
        """The minimum time (in years) for which this model should be used.

        Because the model will typically provide useful results
        slightly outside the range of allowed times,
        no check of t argument is made by the MagneticModel.__call__()
        operator.
        """
        return self._ptr.MinTime()

    def max_time(self) -> float:
        """The maximum time (in years) for which this moel should be used.

        Because the model will typically provide useful results
        slightly outside the range of allowed times,
        no check of t argument is made by the MagneticModel.__call__()
        operator.
        """
        return self._ptr.MaxTime()

    def major_radius(self) -> float:
        """The equatorial radius of the ellipsoid (meters).

        This is the value of 'a' inherited from the Geocentric object
        used in the constructor.
        """
        return self._ptr.MajorRadius()

    def flattening(self) -> float:
        """The flattening of the ellipsoid.

        This is the value inherited from the Geocentric object
        used in the constructor.
        """
        return self._ptr.Flattening()

    @staticmethod
    def default_magnetic_path() -> str:
        """Return the default path for magnetic model data files.

        This is the value of the environment variable
        GEOGRAPHICLIB_MAGNETIC_PATH, if set; otherwise, it is
        $GEOGRAPHICLIB_DATA/magnetic if the environment variable
        GEOGRAPHICLIB_DATA is set; otherwise, it is a compile-time default
        (/usr/local/share/GeographicLib/magnetic on non-Windows systems and
        C:/ProgramData/GeographicLib/magnetic on Windows systems).
        """
        return MagneticModel.DefaultMagneticPath().decode('utf-8')

    @staticmethod
    def default_magnetic_name() -> str:
        """The default name for the magnetic model.

        This is the value of the environment variable
        GEOGRAPHICLIB_MAGNETIC_NAME, if set; otherwise,
        it is "wmm2015".
        The MagneticFieldModel class does not use this function;
        it is just provided as a convenience for a calling program
        when constructing a MagneticFieldModel object.
        """
        return MagneticModel.DefaultMagneticName().decode('utf-8')
