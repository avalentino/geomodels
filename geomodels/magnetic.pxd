# -*- coding: utf-8 -*-
# cython: language_level=3
# distutils: language=c++

from libcpp.string cimport string

from .common cimport real


cdef extern from "GeographicLib/MagneticModel.hpp" namespace "GeographicLib" nogil:
    cdef cppclass CMagneticModel 'GeographicLib::MagneticModel':
        CMagneticModel(const string& name, const string& path) except +
        # @TODO: const Geocentric& earth=Geocentric.WGS84()

        void operator()(real t, real lat, real lon, real h,
                        real& Bx, real& By, real& Bz) const
        void operator()(real t, real lat, real lon, real h,
                        real& Bx, real& By, real& Bz,
                        real& Bxt, real& Byt, real& Bzt) const

        # MagneticCircle Circle(real t, real lat, real h) const

        @staticmethod
        void FieldComponents(real Bx, real By, real Bz,
                             real& H, real& F, real& D, real& I)

        # @staticmethod
        # void FieldComponents(real Bx, real By, real Bz,
        #                      real Bxt, real Byt, real Bzt,
        #                      real& H, real& F, real& D, real& I,
        #                      real& Ht, real& Ft, real& Dt, real& It)

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
        string DefaultMagneticName()
