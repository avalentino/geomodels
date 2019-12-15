# -*- coding: utf-8 -*-
# cython: language_level=3
# distutils: language=c++

from libcpp cimport bool
from libcpp.string cimport string

from .common cimport real


cdef extern from "GeographicLib/Geoid.hpp" namespace "GeographicLib" nogil:
    cdef cppclass CGeoid 'GeographicLib::Geoid':
        ctypedef enum convertflag:
            ELLIPSOIDTOGEOID = -1,
            NONE = 0,
            GEOIDTOELLIPSOID = 1

        CGeoid(const string& name, const string& path, bool cubic,
               bool threadsafe) except +

        void CacheArea(real south, real west, real north, real east) except +  # const
        void CacheAll() except +  # const
        void CacheClear() const

        real operator()(real lat, real lon) except +  # const
        real ConvertHeight(real lat, real lon, real h, convertflag d) except +  # const

        const string& Description() const
        const string& DateTime() const
        const string& GeoidFile() const
        const string& GeoidName() const
        const string& GeoidDirectory() const
        const string Interpolation() const

        real MaxError() const
        real RMSError() const
        real Offset() const
        real Scale() const
        bool ThreadSafe() const

        bool Cache() const
        real CacheWest() const
        real CacheEast() const
        real CacheNorth() const
        real CacheSouth() const

        real EquatorialRadius() const
        real MajorRadius () const       # DEPRECATED
        real Flattening() const

        @staticmethod
        string DefaultGeoidPath()
        @staticmethod
        string DefaultGeoidName()