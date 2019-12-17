# -*- coding: utf-8 -*-
# cython: language_level=3
# distutils: language=c++

"""Looking up the height of the geoid above the ellipsoid.

This class evaluates the height of one of the standard geoids, EGM84,
EGM96, or EGM2008 by bilinear or cubic interpolation into a rectangular
grid of data.

See https://geographiclib.sourceforge.io/html/geoid.html.

The geoids are defined in terms of spherical harmonics.  However in order
to provide a quick and flexible method of evaluating the geoid heights,
this class evaluates the height by interpolation into a grid of
precomputed values.

The height of the geoid above the ellipsoid, `N,` is sometimes called the
geoid undulation.  It can be used to convert a height above the ellipsoid,
`h`, to the corresponding height above the geoid (the orthometric height,
roughly the height above mean sea level), `H`, using the relations::

    h = N + H
    H = -N + h

This class is typically `not` thread safe in that a single instantiation
cannot be safely used by multiple threads because of the way the object
reads the data set and because it maintains a single-cell cache.  If
multiple threads need to calculate geoid heights they should all construct
thread-local instantiations.  Alternatively, set the optional \e
threadsafe parameter to true in the constructor.  This causes the
constructor to read all the data into memory and to turn off the
single-cell caching which results in a Geoid object which \e is thread
safe.

See https://geographiclib.sourceforge.io/html/geoid.html.
"""

import os
import enum

import numpy as np

cimport cython
from libcpp.string cimport string

from .geoid cimport CGeoid
from .error import GeographicErr
from ._utils import (
    as_contiguous_1d_llh, as_contiguous_1d_components, reshape_components,
)


ctypedef CGeoid.convertflag ConvDir


class EHeightConvDir(enum.IntEnum):
    ELLIPSOIDTOGEOID = -1
    NONE = 0
    GEOIDTOELLIPSOID = 1


cdef class GeoidModel:
    """Geoid model.

    :param name:
        the name of the geoid
    :param path:
        (optional) directory for data file
    :param cubic:
        (optional) interpolation method; false means `bilinear`,
        true (the default) means `cubic`.
    :param threadsafe:
        (optional), if true, construct a thread safe object.
        The default is false
    :raises GeographicErr:
        if the data file cannot be found, is unreadable, or is corrupt
    :raises GeographicErr:
        if `threadsafe` is True but the memory necessary for caching
        the data can't be allocated.

    The data file is formed by appending ".pgm" to the name.
    If `path` is specified (and is non-empty), then the file is loaded
    from directory, `path`.
    Otherwise the path is given by :meth:`default_geoid_path`.
    If the `threadsafe` parameter is True, the data set is read into
    memory, the data file is closed, and single-cell caching is turned
    off; this results in a :class:`Geoid` object which is thread safe.
    """
    cdef CGeoid *_ptr

    def __cinit__(self, name, path='', bint cubic=True, bint threadsafe=False):
        cdef string c_name = os.fsencode(name)
        cdef string c_path = os.fsencode(path)

        try:
            with nogil:
                self._ptr = new CGeoid(c_name, c_path, cubic, threadsafe)
        except RuntimeError as exc:
            raise GeographicErr(str(exc)) from exc

    def __dealloc__(self):
        del self._ptr

    def cache_area(self, south: float, west: float, north: float, east: float):
        """Set up a cache.

        :param float south:
            south latitude (degrees) of the south edge of the cached area.
        :param west:
            west longitude (degrees) of the west edge of the cached area.
        :param north:
            north latitude (degrees) of the north edge of the cached area.
        :param east:
            east longitude (degrees) of the east edge of the cached area.
        :raises GeographicErr:
            if the memory necessary for caching the data can't be
            allocated (in this case, you will have no cache and can try
            again with a smaller area).
        :raises GeographicErr:
            if there's a problem reading the data.
        :raises GeographicErr:
            if this is called on a threadsafe :class:`Geoid`.

        Cache the data for the specified "rectangular" area bounded by
        the parallels `south` and `north` and the meridians `west` and
        `east`.
        `east` is always interpreted as being east of `west`, if
        necessary by adding 360 deg; to its value.
        `south` and `north` should be in the range [-90 deg, +90 deg].
        """
        try:
            with nogil:
                self._ptr.CacheArea(south, west, north, east)
        except RecursionError as exc:
            raise GeographicErr(str(exc)) from exc

    def cache_all(self):
        """Cache all the data.

        :raises GeographicErr:
            if the memory necessary for caching the data can't be
            allocated (in this case, you will have no cache and can try
            again with a smaller area).
        :raises GeographicErr:
            if there's a problem reading the data.
        :raises GeographicErr:
            if this is called on a threadsafe :class:`Geoid`.

        On most computers, this is fast for data sets with grid
        resolution of 5' or coarser. For a 1' grid, the required RAM is
        450MB; a 2.5' grid needs 72MB; and a 5' grid needs 18MB.
        """
        try:
            with nogil:
                self._ptr.CacheAll()
        except RecursionError as exc:
            raise GeographicErr(str(exc)) from exc

    def cache_clear(self):
        """Clear the cache.

        This never throws an error.
        This does nothing with a thread safe :class:`Geoid`.
        """
        self._ptr.CacheClear()

    @cython.boundscheck(False)
    @cython.wraparound(False)
    cdef compute(self, double[::1] vlat, double[::1] vlon):
        cdef long size = vlat.size
        h = np.empty(shape=[size], dtype=np.float64)
        cdef double[::1] vh = h

        try:
            with nogil:
                for i in range(size):
                    vh[i] = cython.operator.dereference(self._ptr)(
                        vlat[i], vlon[i])
        except RecursionError as exc:
            raise GeographicErr(str(exc)) from exc

        return h

    def __call__(self, lat, lon):
        """Compute the geoid height at a point.

        :param lat:
            latitude of the point (degrees).
        :param lon:
            longitude of the point (degrees).
        :raises GeographicErr:
            if there's a problem reading the data.
            This never happens if (`lat`, `lon`) is within a
            successfully cached area.
        :returns:
            the height of the geoid above the ellipsoid (meters).

        The latitude should be in [-90 deg, +90deg].
        """
        dtype = np.float64
        lat, lon, shape = as_contiguous_1d_components(
            lat, lon, labels=['lat', 'lon'], dtype=dtype)
        h = self.compute(lat, lon)
        return reshape_components(shape, h)

    @cython.boundscheck(False)
    @cython.wraparound(False)
    cdef core_convert_height(self,
                             double[::1] vlat, double[::1] vlon, double[::1] vh,
                             ConvDir direction):
        cdef long size = vlat.size
        out = np.empty(shape=[size], dtype=np.float64)
        cdef double[::1] vout = out
        cdef long i = 0

        try:
            with nogil:
                for i in range(size):
                    vout[i] = self._ptr.ConvertHeight(
                        vlat[i], vlon[i], vh[i], direction)
        except RecursionError as exc:
            raise GeographicErr(str(exc)) from exc

        return out

    def convert_height(self, lat, lon, h, dir: EHeightConvDir):
        """Convert a height above the geoid to a height above the
        ellipsoid and vice versa.

        :param lat:
            latitude of the point (degrees).
        :param lon:
            longitude of the point (degrees).
        :param h:
            height of the point (meters).
        :param dir:
            a :class:`EHeightConvDir` specifying the direction of the
            conversion; :data:`EHeightConvDir.GEOIDTOELLIPSOID` means
            convert a height above the geoid to a height above the
            ellipsoid; :data:`Geoid.ELLIPSOIDTOGEOID` means convert a
            height above the ellipsoid to a height above the geoid.
        :raises GeographicErr:
            if there's a problem reading the data; this never happens
            if (`lat`, `lon`) is within a successfully cached area.
        :returns:
            converted height (meters).
        """
        dir = EHeightConvDir(dir)
        dtype = np.float64
        lat, lon, h, shape = as_contiguous_1d_llh(lat, lon, h, dtype)

        out = self.core_convert_height(lat, lon, h, dir.value)

        return reshape_components(shape, out)

    def description(self) -> str:
        """Return geoid description, if available, in the data file.

        If the geoid description is absent in the data file
        return "NONE".
        """
        return self._ptr.Description().decode('utf-8')

    def datetime(self) -> str:
        """Return date of the data file.

        If absent, return "UNKNOWN".
        """
        return self._ptr.DateTime().decode('utf-8')

    def geoid_file(self) -> str:
        """Return full file name used to load the geoid data."""
        return self._ptr.GeoidFile().decode('utf-8')

    def geoid_name(self) -> str:
        """Return the "name" used to load the geoid data.

        "name" is the first argument of the constructor.
        """
        return self._ptr.GeoidName().decode('utf-8')

    def geoid_directory(self) -> str:
        """Return the directory used to load the geoid data."""
        return self._ptr.GeoidDirectory().decode('utf-8')

    def interpolation(self) -> str:
        """Return interpolation method ("cubic" or "bilinear")."""
        # @TODO: use an enum
        return self._ptr.Interpolation().decode('utf-8')

    def max_error(self) -> float:
        """Return an estimate of the maximum interpolation and
        quantization error [m].

        This relies on the value being stored in the data file.
        If the value is absent, return -1.
        """
        return self._ptr.MaxError()

    def rms_error(self) -> float:
        """Return an estimate of the RMS interpolation and
        quantization error [m].

        This relies on the value being stored in the data file.
        If the value is absent, return -1.
        """
        return self._ptr.RMSError()

    def offset(self) -> float:
        """Offset (meters).

        This in used in converting from the pixel values in the data
        file to geoid heights.
        """
        return self._ptr.Offset()

    def scale(self) -> float:
        """Scale (meters).

        This in used in converting from the pixel values in the data
        file to geoid heights.
        """
        return self._ptr.Scale()

    def threadsafe(self) -> bool:
        """Return true if the object is constructed to be thread safe."""
        return self._ptr.ThreadSafe()

    def cache(self) -> bool:
        """Return true if a data cache is active."""
        return self._ptr.Cache()

    def cache_west(self) -> float:
        """West edge of the cached area.

        The cache includes this edge.
        """
        return self._ptr.CacheWest()

    def cache_east(self) -> float:
        """East edge of the cached area.

        The cache excludes this edge.
        """
        return self._ptr.CacheEast()

    def cache_north(self) -> float:
        """North edge of the cached area.

        The cache includes this edge.
        """
        return self._ptr.CacheNorth()

    def cache_south(self) -> float:
        """South edge of the cached area.

        The cache excludes this edge unless it's the south pole.
        """
        return self._ptr.CacheSouth()

    def equator_radius(self) -> float:
        """The equatorial radius of the ellipsoid (meters).

        (The WGS84 value is returned because the supported geoid
        models are all based on this ellipsoid.)
        """
        # return self._ptr.EquatorialRadius() # GEOGRAPHICLIB_VERSION >= 105000
        return self._ptr.MajorRadius()

    def flattening(self) -> float:
        """The flattening of the ellipsoid.

        (The WGS84 value is returned because the supported geoid
        models are all based on this ellipsoid.
        """
        return self._ptr.Flattening()

    @staticmethod
    def default_geoid_path() -> str:
        """The default path for geoid data files.

        This is the value of the environment variable
        `GEOGRAPHICLIB_GEOID_PATH`, if set; otherwise, it is
        `${GEOGRAPHICLIB_DATA}/geoids` if the environment variable
        `GEOGRAPHICLIB_DATA` is set; otherwise, it is a compile-time
        default.
        """
        return CGeoid.DefaultGeoidPath().decode('utf-8')

    @staticmethod
    def default_geoid_name() ->  str:
        """The default name for the geoid.

        This is the value of the environment variable
        `GEOGRAPHICLIB_GEOID_NAME`, if set; otherwise, it is "egm96-5".
        The GeoidModel class does not use this function; it is just
        provided as a convenience for a calling program when
        constructing a :class:`GeoidModel` object.
        """
        return CGeoid.DefaultGeoidName().decode('utf-8')
