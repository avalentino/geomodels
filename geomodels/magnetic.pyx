# -*- coding: utf-8 -*-
# cython: language_level=3
# distutils: language=c++

"""Model of the earth's magnetic field.

Evaluate the earth's magnetic field according to a model.  At present only
internal magnetic fields are handled.  These are due to the earth's code
and crust; these vary slowly (over many years).  Excluded are the effects
of currents in the ionosphere and magnetosphere which have daily and
annual variations.

See https://geographiclib.sourceforge.io/html/magnetic.html.
"""

import os
import numpy as np

cimport cython
from libcpp.string cimport string

from .magnetic cimport CMagneticModel
from .error import GeographicErr
from ._utils import (
    as_contiguous_1d_llh, as_contiguous_1d_components, reshape_components,
)


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
    :meth:`MagneticFieldModel.default_magnetic_path`.

    This file contains the metadata which specifies the properties of the
    model.  The coefficients for the spherical harmonic sums are obtained
    from a file obtained by appending ".cof" to metadata file (so the
    filename ends in ".wwm.cof").

    The model is not tied to a particular ellipsoidal model of the earth.
    The final earth argument to the constructor specifies an ellipsoid to
    allow geodetic coordinates to the transformed into the spherical
    coordinates used in the spherical harmonic sum.
    """
    cdef CMagneticModel *_ptr

    def __cinit__(self, name, path=''):
        # @TODO: support for 'earth' parameter (default: WGS84)
        cdef string c_name = os.fsencode(name)
        cdef string c_path = os.fsencode(path)

        try:
            with nogil:
                self._ptr = new CMagneticModel(c_name, c_path)
        except RuntimeError as exc:
            raise GeographicErr(str(exc)) from exc

    def __dealloc__(self):
        del self._ptr

    @cython.boundscheck(False)
    @cython.wraparound(False)
    cdef compute(self,
                 double t, double[::1] vlat, double[::1] vlon, double[::1] vh):
        cdef long size = vlat.size
        dtype = np.float64

        Bx = np.empty(shape=[size], dtype=dtype)
        By = np.empty(shape=[size], dtype=dtype)
        Bz = np.empty(shape=[size], dtype=dtype)

        cdef double[::1] vBx = Bx
        cdef double[::1] vBy = By
        cdef double[::1] vBz = Bz

        cdef long i = 0
        with nogil:
            for i in range(size):
                cython.operator.dereference(self._ptr)(
                    t, vlat[i], vlon[i], vh[i], vBx[i], vBy[i], vBz[i])

        return Bx, By, Bz

    @cython.boundscheck(False)
    @cython.wraparound(False)
    cdef compute_with_rate(self, double t,
                           double[::1] vlat, double[::1] vlon, double[::1] vh,):
        cdef long size = vlat.size
        dtype = np.float64

        Bx = np.empty(shape=[size], dtype=dtype)
        By = np.empty(shape=[size], dtype=dtype)
        Bz = np.empty(shape=[size], dtype=dtype)
        Bxt = np.empty(shape=[size], dtype=dtype)
        Byt = np.empty(shape=[size], dtype=dtype)
        Bzt = np.empty(shape=[size], dtype=dtype)

        cdef double[::1] vBx = Bx
        cdef double[::1] vBy = By
        cdef double[::1] vBz = Bz
        cdef double[::1] vBxt = Bxt
        cdef double[::1] vByt = Byt
        cdef double[::1] vBzt = Bzt

        cdef long i = 0
        with nogil:
            for i in range(size):
                cython.operator.dereference(self._ptr)(
                    t, vlat[i], vlon[i], vh[i],
                    vBx[i], vBy[i], vBz[i], vBxt[i], vByt[i], vBzt[i])

        return Bx, By, Bz, Bxt, Byt, Bzt

    def __call__(self, double t, lat, lon, h, bint rate=False):
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
        :param bool rate:
            also returns first time derivative of the magnetic field
            components (default: False)
        :returns:
            Bx, By, Bz: the easterly, northerly and vertical (up)
            components of the magnetic field (nanotesla).

            If time_derivatives is set to True then the following tuple
            is returned: (Bx, By, Bz, Bxt, Byt, Bzt), where  Bxt, Byt
            and Bzt are the rate of change of Bx, By and Bz
            respectively (nT/yr).
        """
        dtype = np.float64
        lat, lon, h, shape = as_contiguous_1d_llh(lat, lon, h, dtype)

        if not rate:
            Bx, By, Bz = self.compute(t, lat, lon, h)
            return reshape_components(shape, Bx, By, Bz)
        else:
            Bx, By, Bz, Bxt, Byt, Bzt = self.compute_with_rate(t, lat, lon, h)
            return reshape_components(shape, Bx, By, Bz, Bxt, Byt, Bzt)

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

    @cython.boundscheck(False)
    @cython.wraparound(False)
    @staticmethod
    cdef compute_field_components(
            double[::1] vBx, double[::1] vBy, double[::1] vBz):
        cdef long size = vBx.size
        dtype = np.float64

        H = np.empty(shape=[size], dtype=dtype)
        F = np.empty(shape=[size], dtype=dtype)
        D = np.empty(shape=[size], dtype=dtype)
        I = np.empty(shape=[size], dtype=dtype)

        cdef double[::1] vH = H
        cdef double[::1] vF = F
        cdef double[::1] vD = D
        cdef double[::1] vI = I

        cdef long i = 0
        with nogil:
            for i in range(size):
                CMagneticModel.FieldComponents(
                    vBx[i], vBy[i], vBz[i], vH[i], vF[i], vD[i], vI[i])

        return H, F, D, I

    @staticmethod
    def field_components(Bx, By, Bz):
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
        dtype = np.float64
        Bx, By, Bz, shape = as_contiguous_1d_components(
            Bx, By, Bz, labels=['Bx', 'By', 'Bz'], dtype=dtype)

        H, F, D, I = MagneticFieldModel.compute_field_components(Bx, By, Bz)

        return reshape_components(shape, H, F, D, I)

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
        from the :meth:`MagneticFieldModel.description` file in the
        data file; if absent, return "NONE".
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
        return self._ptr.MagneticFile().decode('utf-8')

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
        no check of t argument is made by the
        :meth:`MagneticFieldModel.__call__` operator.
        """
        return self._ptr.MinHeight()

    def max_height(self) -> float:
        """Maximum height.

        The maximum height above the ellipsoid (in meters) for which
        this MagneticModel should be used.

        Because the model will typically provide useful results
        slightly outside the range of allowed heights,
        no check of t argument is made by the
        :meth:`MagneticFieldModel.__call__` operator.
        """
        return self._ptr.MaxHeight()

    def min_time(self) -> float:
        """The minimum time (in years) for which this model should be used.

        Because the model will typically provide useful results
        slightly outside the range of allowed times,
        no check of t argument is made by the
        :meth:`MagneticFieldModel.__call__` operator.
        """
        return self._ptr.MinTime()

    def max_time(self) -> float:
        """The maximum time (in years) for which this model should be used.

        Because the model will typically provide useful results
        slightly outside the range of allowed times,
        no check of the `t` argument is made by the
        :meth:`MagneticFieldModel.__call__` operator.
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
        `GEOGRAPHICLIB_MAGNETIC_PATH`, if set; otherwise, it is
        `$GEOGRAPHICLIB_DATA/magnetic` if the environment variable
        `GEOGRAPHICLIB_DATA` is set; otherwise, it is a compile-time
        default.
        """
        return CMagneticModel.DefaultMagneticPath().decode('utf-8')

    @staticmethod
    def default_magnetic_name() -> str:
        """The default name for the magnetic model.

        This is the value of the environment variable
        `GEOGRAPHICLIB_MAGNETIC_NAME`, if set; otherwise,
        it is "wmm2015".
        The :class:`MagneticFieldModel` class does not use this function;
        it is just provided as a convenience for a calling program
        when constructing a :class:`MagneticFieldModel` object.
        """
        return CMagneticModel.DefaultMagneticName().decode('utf-8')
