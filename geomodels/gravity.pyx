# -*- coding: utf-8 -*-
# cython: language_level=3
# distutils: language=c++

r"""Model of the earth's gravity field.

Evaluate the earth's gravity field according to a model.  The supported
models treat only the gravitational field exterior to the mass of the
earth.  When computing the field at points near (but above) the surface
of the earth a small correction can be applied to account for the mass
of the atmosphere above the point in question; see \ref gravityatmos.
Determining the height of the geoid above the ellipsoid entails
correcting for the mass of the earth above the geoid.
The egm96 and egm2008 include separate correction terms to account for
this mass.

Definitions and terminology (from Heiskanen and Moritz, Sec 2-13):

* $V$ = gravitational potential
* $\Phi$ = rotational potential
* $W = V + \Phi = T + U$ = total potential
* $V_{0}$ = normal gravitation potential
* $U = V_{0} + \Phi$ = total normal potential
* $T = W - U = V - V_{0}$ = anomalous or disturbing potential
* $g = \nabla W = \gamma + \delta$
* $f = \nabla \Phi$
* $\Gamma = \nabla V_{0}$
* $\gamma = &nabla U$
* $\delta = \nabla T$ = gravity disturbance vector = $g_{P} - \gamma_{P}$
* $\delta g$ = gravity disturbance = $g_{P} - \gamma_{P}$
* $\Delta g$ = gravity anomaly vector = $g_{P} - \gamma_{Q}$
  here the line $PQ$ is perpendicular to ellipsoid and the potential at
  $P$ equals the normal potential at $Q$
* $\Delta g$ = gravity anomaly = $g{P} - \gamma_{Q}$
* $(\xi, \eta)$ deflection of the vertical, the difference in
  directions of $g_{P}$ and $\gamma_{Q}, \xi = NS, \eta = EW$.
* $X$, $Y$, $Z$, geocentric coordinates
* $x$, $y$, $z$, local cartesian coordinates used to denote the east,
  north and up directions.

References:

* W. A. Heiskanen and H. Moritz, Physical Geodesy (Freeman, San
  Francisco, 1967).

See https://geographiclib.sourceforge.io/html/gravity.html.
"""

import os

import numpy as np

cimport cython
from libcpp.string cimport string

from .gravity cimport CGravityModel
from .error import GeographicErr
from ._utils import (
    as_contiguous_1d_llh, as_contiguous_1d_components, reshape_components,
)


cdef class GravityModel:
    """Gravity model.

    :param str name:
        the name of the model
    :param path:
        (optional) directory for data file
    :raises GeographicErr:
        if the data file cannot be found, is unreadable, or is corrupt
    :raises MemoryError:
        if the memory necessary for storing the model can't be
        allocated

    A filename is formed by appending ".egm" (World Gravity Model) to
    the name.  If `path` is specified (and is non-empty), then the file
    is loaded from directory, `path`.  Otherwise the path is given by
    :meth:`default_gravity_path`.

    This file contains the metadata which specifies the properties of
    the model.  The coefficients for the spherical harmonic sums are
    obtained from a file obtained by appending ".cof" to metadata file
    (so the filename ends in ".egm.cof").
    """
    cdef CGravityModel *_ptr

    # @TODO: support GeographicLib v1.50
    # def __cinit__(self, name, path='', int Nmax=-1, int Mmax=-1):
    def __cinit__(self, name, path=''):
        cdef string c_name = os.fsencode(name)
        cdef string c_path = os.fsencode(path)

        try:
            with nogil:
                # @TODO: support GeographicLib v1.50
                # self._ptr = new CGravityModel(c_name, c_path, Nmax, Mmax)
                self._ptr = new CGravityModel(c_name, c_path)
        except RuntimeError as exc:
            raise GeographicErr(str(exc)) from exc

    def __dealloc__(self):
        del self._ptr

    @cython.boundscheck(False)
    @cython.wraparound(False)
    cdef compute_gracity(self,
                         double[::1] vlat, double[::1] vlon, double[::1] vh):
        cdef long size = vlat.size
        dtype = np.float64

        W = np.empty(shape=[size], dtype=dtype)
        gx = np.empty(shape=[size], dtype=dtype)
        gy = np.empty(shape=[size], dtype=dtype)
        gz = np.empty(shape=[size], dtype=dtype)

        cdef double[::1] vW = W
        cdef double[::1] vgx = gx
        cdef double[::1] vgy = gy
        cdef double[::1] vgz = gz

        cdef long i = 0
        with nogil:
            for i in range(size):
                vW[i] = self._ptr.Gravity(vlat[i], vlon[i], vh[i],
                                          vgx[i], vgy[i], vgz[i])

        return W, gx, gy, gz

    def gravity(self, lat, lon, h):
        """Evaluate the gravity at an arbitrary point above (or below)
        the ellipsoid.

        The function includes the effects of the earth's rotation.

        :param lat:
            the geographic latitude (degrees)
        :param lon:
            the geographic longitude (degrees)
        :param h:
            the height above the ellipsoid (meters)
        :returns:
            * W the sum of the gravitational and centrifugal potentials
              ([m**2 / s**2])
            * gx the easterly component of the acceleration ([m / s**2])
            * gy the northerly component of the acceleration ([m / s**2])
            * gz the upward component of the acceleration ([m / s**2]);
              this is usually negative
        """
        lat, lon, h, shape = as_contiguous_1d_llh(lat, lon, h, np.float64)
        W, gx, gy, gz = self.compute_gracity(lat, lon, h)
        return reshape_components(shape, W, gx, gy, gz)

    @cython.boundscheck(False)
    @cython.wraparound(False)
    cdef compute_disturbance(self,
                         double[::1] vlat, double[::1] vlon, double[::1] vh):
        cdef long size = vlat.size
        dtype = np.float64

        T = np.empty(shape=[size], dtype=dtype)
        deltax = np.empty(shape=[size], dtype=dtype)
        deltay = np.empty(shape=[size], dtype=dtype)
        deltaz = np.empty(shape=[size], dtype=dtype)

        cdef double[::1] vT = T
        cdef double[::1] vdeltax = deltax
        cdef double[::1] vdeltay = deltay
        cdef double[::1] vdeltaz = deltaz

        cdef long i = 0
        with nogil:
            for i in range(size):
                vT[i] = self._ptr.Disturbance(
                    vlat[i], vlon[i], vh[i],
                    vdeltax[i], vdeltay[i], vdeltaz[i])

        return T, deltax, deltay, deltaz

    def disturbance(self, lat, lon, h):
        """Evaluate the gravity disturbance vector at an arbitrary
        point above (or below) the ellipsoid.

        :param lat:
            the geographic latitude (degrees)
        :param lon:
            the geographic longitude (degrees)
        :param h:
            the height above the ellipsoid (meters)
        :returns:
            * T the corresponding disturbing potential ([m**2 / s**2])
            * deltax the easterly component of the disturbance vector
              ([m / s**2])
            * deltay the northerly component of the disturbance vector
              ([m / s**2])
            * deltaz the upward component of the disturbance vector
              ([m / s**2])
        """
        lat, lon, h, shape = as_contiguous_1d_llh(lat, lon, h, np.float64)
        T, deltax, deltay, deltaz = self.compute_disturbance(lat, lon, h)
        return reshape_components(shape, T, deltax, deltay, deltaz)

    @cython.boundscheck(False)
    @cython.wraparound(False)
    cdef compute_geoid_height(self, double[::1] vlat, double[::1] vlon):
        cdef long size = vlat.size
        dtype = np.float64

        h = np.empty(shape=[size], dtype=dtype)
        cdef double[::1] vh = h

        cdef long i = 0
        with nogil:
            for i in range(size):
                vh[i] = self._ptr.GeoidHeight(vlat[i], vlon[i])

        return h

    def geoid_height(self, lat, lon):
        """Evaluate the geoid height.

        :param lat:
            the geographic latitude (degrees)
        :param lon:
            the geographic longitude (degrees)
        :returns:
            `N` the height of the geoid above the reference ellipsoid
            (meters)

        Some approximations are made in computing the geoid height so that the
        results of the NGA codes are reproduced accurately.
        """
        lat, lon, shape = as_contiguous_1d_components(
            lat, lon, dtype=np.float64)
        h = self.compute_geoid_height(lat, lon)
        return reshape_components(shape, h)

    @cython.boundscheck(False)
    @cython.wraparound(False)
    cdef compute_spherical_anomaly(
            self, double[::1] vlat, double[::1] vlon, double[::1] vh):
        cdef long size = vlat.size
        dtype = np.float64

        Dg01 = np.empty(shape=[size], dtype=dtype)
        xi = np.empty(shape=[size], dtype=dtype)
        eta = np.empty(shape=[size], dtype=dtype)

        cdef double[::1] vDg01 = Dg01
        cdef double[::1] vxi = xi
        cdef double[::1] veta = eta

        cdef long i = 0
        with nogil:
            for i in range(size):
                self._ptr.SphericalAnomaly(vlat[i], vlon[i], vh[i],
                                           vDg01[i], vxi[i], veta[i])

        return Dg01, xi, eta

    def spherical_anomaly(self, lat, lon, h):
        """Evaluate the components of the gravity anomaly vector using
        the spherical approximation.

        :param lat:
            the geographic latitude (degrees)
        :param lon:
            the geographic longitude (degrees)
        :param h:
            the height above the ellipsoid (meters)
        :returns:
            * Dg01 the gravity anomaly ([m / s**2])
            * xi the northerly component of the deflection of the
              vertical (degrees)
            * eta the easterly component of the deflection of the
              vertical (degrees).

        The spherical approximation (see Heiskanen and Moritz,
        Sec 2-14) is used so that the results of the NGA codes are
        reproduced accurately.
        """
        lat, lon, h, shape = as_contiguous_1d_llh(lat, lon, h, np.float64)
        Dg01, xi, eta = self.compute_spherical_anomaly(lat, lon, h)
        return reshape_components(shape, Dg01, xi, eta)

    @cython.boundscheck(False)
    @cython.wraparound(False)
    cdef compute_w(self, double[::1] vx, double[::1] vy, double[::1] vz):
        cdef long size = vx.size
        dtype = np.float64

        out = np.empty(shape=[size], dtype=dtype)
        gx = np.empty(shape=[size], dtype=dtype)
        gy = np.empty(shape=[size], dtype=dtype)
        gz = np.empty(shape=[size], dtype=dtype)

        cdef double[::1] vout = out
        cdef double[::1] vgx = gx
        cdef double[::1] vgy = gy
        cdef double[::1] vgz = gz

        cdef long i = 0
        with nogil:
            for i in range(size):
                vout[i] = self._ptr.W(vx[i], vy[i], vz[i],
                                      vgx[i], vgy[i], vgz[i])

        return out, gx, gy, gz

    def w(self, x, y, z):
        """Evaluate the components of the acceleration due to gravity
        and the centrifugal acceleration in geocentric coordinates.

        :param x:
            geocentric coordinate of point (meters)
        :param y:
            geocentric coordinate of point (meters)
        :param z:
            geocentric coordinate of point (meters)
        :returns:
            * W = V + Phi, the sum of the gravitational and centrifugal
              potentials ([m**2 /  s**2])
            * gx the x component of the acceleration ([m / s**2])
            * gy the y component of the acceleration ([m / s**2])
            * gz the z component of the acceleration ([m / s**2])
        """
        x, y, z, shape = as_contiguous_1d_components(
            x, y, z, labels=['x', 'y', 'z'], dtype=np.float64)
        out, gx, gy, gz = self.compute_w(x, y, z)
        return reshape_components(shape, out, gx, gy, gz)

    @cython.boundscheck(False)
    @cython.wraparound(False)
    cdef compute_v(self, double[::1] vx, double[::1] vy, double[::1] vz):
        cdef long size = vx.size
        dtype = np.float64

        out = np.empty(shape=[size], dtype=dtype)
        gx = np.empty(shape=[size], dtype=dtype)
        gy = np.empty(shape=[size], dtype=dtype)
        gz = np.empty(shape=[size], dtype=dtype)

        cdef double[::1] vout = out
        cdef double[::1] vgx = gx
        cdef double[::1] vgy = gy
        cdef double[::1] vgz = gz

        cdef long i = 0
        with nogil:
            for i in range(size):
                vout[i] = self._ptr.V(vx[i], vy[i], vz[i],
                                      vgx[i], vgy[i], vgz[i])

        return out, gx, gy, gz

    def v(self, x, y, z):
        """Evaluate the components of the gravity disturbance in
        geocentric coordinates.

        :param x:
            geocentric coordinate of point (meters)
        :param y:
            geocentric coordinate of point (meters)
        :param z:
            geocentric coordinate of point (meters)
        :returns:
            * V = W - Phi, the gravitational potential ([m**2 /  s**2])
            * gx the x component of the acceleration ([m / s**2])
            * gy the y component of the acceleration ([m / s**2])
            * gz the z component of the acceleration ([m / s**2])
        """
        x, y, z, shape = as_contiguous_1d_components(
            x, y, z, labels=['x', 'y', 'z'], dtype=np.float64)
        out, gx, gy, gz = self.compute_v(x, y, z)
        return reshape_components(shape, out, gx, gy, gz)

    @cython.boundscheck(False)
    @cython.wraparound(False)
    cdef compute_t_components(self,
                              double[::1] vx, double[::1] vy, double[::1] vz):
        cdef long size = vx.size
        dtype = np.float64

        out = np.empty(shape=[size], dtype=dtype)
        deltax = np.empty(shape=[size], dtype=dtype)
        deltay = np.empty(shape=[size], dtype=dtype)
        deltaz = np.empty(shape=[size], dtype=dtype)

        cdef double[::1] vout = out
        cdef double[::1] vdeltax = deltax
        cdef double[::1] vdeltay = deltay
        cdef double[::1] vdeltaz = deltaz

        cdef long i = 0
        with nogil:
            for i in range(size):
                vout[i] = self._ptr.T(vx[i], vy[i], vz[i],
                                      vdeltax[i], vdeltay[i], vdeltaz[i])

        return out, deltax, deltay, deltaz

    def t_components(self, x, y, z):
        """Evaluate the components of the gravity disturbance in
        geocentric coordinates.

        :param x:
            geocentric coordinate of point (meters)
        :param y:
            geocentric coordinate of point (meters)
        :param z:
            geocentric coordinate of point (meters)
        :returns:
            * T = W - U, the disturbing potential (also called the
              anomalous potential) ([m**2 / s**2])
            * deltaX the x component of the gravity disturbance
              ([m / s**2])
            * deltaY the Y component of the gravity disturbance
              ([m / s**2])
            * deltaZ the Z component of the gravity disturbance
              ([m / s**2])
        """
        x, y, z, shape = as_contiguous_1d_components(
            x, y, z, labels=['x', 'y', 'z'], dtype=np.float64)
        out, gx, gy, gz = self.compute_t_components(x, y, z)
        return reshape_components(shape, out, gx, gy, gz)

    @cython.boundscheck(False)
    @cython.wraparound(False)
    cdef compute_t(self, double[::1] vx, double[::1] vy, double[::1] vz):
        cdef long size = vx.size
        dtype = np.float64

        out = np.empty(shape=[size], dtype=dtype)
        cdef double[::1] vout = out

        cdef long i = 0
        with nogil:
            for i in range(size):
                vout[i] = self._ptr.T(vx[i], vy[i], vz[i])

        return out

    def t(self, x, y, z):
        """Evaluate disturbing potential in geocentric coordinates.

        :param x:
            geocentric coordinate of point (meters)
        :param y:
            geocentric coordinate of point (meters)
        :param z:
            geocentric coordinate of point (meters)
        :returns:
            T = W - U, the disturbing potential (also called the
            anomalous potential) ([m**2 / s**2])
        """
        x, y, z, shape = as_contiguous_1d_components(
            x, y, z, labels=['x', 'y', 'z'], dtype=np.float64)
        out = self.compute_t(x, y, z)
        return reshape_components(shape, out)

    @cython.boundscheck(False)
    @cython.wraparound(False)
    cdef compute_u(self, double[::1] vx, double[::1] vy, double[::1] vz):
        cdef long size = vx.size
        dtype = np.float64

        out = np.empty(shape=[size], dtype=dtype)
        gammax = np.empty(shape=[size], dtype=dtype)
        gammay = np.empty(shape=[size], dtype=dtype)
        gammaz = np.empty(shape=[size], dtype=dtype)

        cdef double[::1] vout = out
        cdef double[::1] vgammax = gammax
        cdef double[::1] vgammay = gammay
        cdef double[::1] vgammaz = gammaz

        cdef long i = 0
        with nogil:
            for i in range(size):
                vout[i] = self._ptr.U(vx[i], vy[i], vz[i],
                                      vgammax[i], vgammay[i], vgammaz[i])

        return out, gammax, gammay, gammaz

    def u(self, x, y, z):
        """Evaluate the components of the acceleration due to normal
        gravity and the centrifugal acceleration in geocentric coordinates.

        :param x:
            geocentric coordinate of point (meters)
        :param y:
            geocentric coordinate of point (meters)
        :param z:
            geocentric coordinate of point (meters)
        :returns:
            * U = V0 + Phi, the sum of the normal gravitational and
              centrifugal potentials ([m**2 / s**2])
            * gammaX the x component of the normal acceleration ([m / s**2])
            * gammaY the y component of the normal acceleration ([m / s**2])
            * gammaZ the z component of the normal acceleration ([m / s**2])
        """
        x, y, z, shape = as_contiguous_1d_components(
            x, y, z, labels=['x', 'y', 'z'], dtype=np.float64)
        out, gammax, gammay, gammaz = self.compute_u(x, y, z)
        return reshape_components(shape, out, gammax, gammay, gammaz)

    @cython.boundscheck(False)
    @cython.wraparound(False)
    cdef compute_phi(self, double[::1] vx, double[::1] vy):
        cdef long size = vx.size
        dtype = np.float64

        out = np.empty(shape=[size], dtype=dtype)
        fx = np.empty(shape=[size], dtype=dtype)
        fy = np.empty(shape=[size], dtype=dtype)

        cdef double[::1] vout = out
        cdef double[::1] vfx = fx
        cdef double[::1] vfy = fy

        cdef long i = 0
        with nogil:
            for i in range(size):
                vout[i] = self._ptr.Phi(vx[i], vy[i], vfx[i], vfy[i])

        return out, fx, fy

    def phi(self, x, y):
        """Evaluate the centrifugal acceleration in geocentric coordinates.

        :param x:
            geocentric coordinate of point (meters)
        :param y:
            geocentric coordinate of point (meters)
        :returns:
            * Phi, the centrifugal potential ([m**2 / s**2])
            * fx the x component of the centrifugal acceleration (m / s**2])
            * fy the y component of the centrifugal acceleration (m / s**2])
        """
        x, y, shape = as_contiguous_1d_components(
            x, y, labels=['x', 'y'], dtype=np.float64)
        out, fx, fy = self.compute_phi(x, y)
        return reshape_components(shape, out, fx, fy)

    # @TODO:
    # GravityCircle Circle(real lat, real h, unsigned caps=ALL) const except +
    # const NormalGravity& ReferenceEllipsoid() const

    def description(self) -> str:
        """The description of the gravity model.

        If the gravity model description is absent in the data file
        return "NONE".
        """
        return self._ptr.Description().decode('utf-8')

    def datetime(self) -> str:
        """Date of the gravity model.

        If absent, return "UNKNOWN".
        """
        return self._ptr.DateTime().decode('utf-8')

    def gravity_file(self) -> str:
        """Full file name used to load the gravity model."""
        return self._ptr.GravityFile().decode('utf-8')

    def gravity_model_name(self) -> str:
        """Return the "name" used to load the gravity model.

        "name" is the first argument of the constructor, but this may
        be overridden by the model file).
        """
        return self._ptr.GravityModelName().decode('utf-8')

    def gravity_model_directory(self) -> str:
        """Return the directory used to load the gravity model."""
        return self._ptr.GravityModelDirectory().decode('utf-8')

    def equatorial_radius(self) -> float:
        """The equatorial radius of the ellipsoid (meters)."""
        # return self._ptr.EquatorialRadius()  # @TODO: new in v1.50
        return self._ptr.MajorRadius()

    def flattening(self) -> float:
        """The flattening of the ellipsoid."""
        return self._ptr.Flattening()

    def mass_constant(self) -> float:
        """The mass constant of the model ([GM] = m**3 /s**2).

        It is the product of `G` the gravitational constant and `M` the
        mass of the earth (usually including the mass of the earth's
        atmosphere).
        """
        return self._ptr.MassConstant()

    def reference_mass_constant(self) -> float:
        """The mass constant of the reference ellipsoid.

        [GM] = m**3 / s**2.
        """
        return self._ptr.ReferenceMassConstant()

    def angular_velocity(self) -> float:
        """The angular velocity of the model and the reference ellipsoid.

        :math:`[\omega] = rad/s`
        """
        return self._ptr.AngularVelocity()

    # @TODO: methods added in GeographicLib v1.50.
    # def degree(self) -> int:
    #     """The maximum degree of the components of the model (Nmax)."""
    #     return self._ptr.Dergee()
    #
    # def order(self) -> int:
    #     """The maximum order of the components of the model (Mmax)."""
    #     return self._ptr.Order()

    @staticmethod
    def default_gravity_path() -> str:
        """the default path for gravity model data files.

        This is the value of the environment variable
        `GEOGRAPHICLIB_GRAVITY_PATH`, if set; otherwise, it is
        `$GEOGRAPHICLIB_DATA/gravity` if the environment variable
        `GEOGRAPHICLIB_DATA` is set; otherwise, it is a compile-time
        default.
        """
        return CGravityModel.DefaultGravityPath().decode('utf-8')

    @staticmethod
    def default_gravity_name() -> str:
        """The default name for the gravity model.

        This is the value of the environment variable
        `GEOGRAPHICLIB_GRAVITY_NAME`, if set; otherwise, it is "egm96".
        The :class:`GravityModel` class does not use this function;
        it is just provided as a convenience for a calling program when
        constructing a :class:`GravityModel` object.
        """
        return CGravityModel.DefaultGravityName().decode('utf-8')
