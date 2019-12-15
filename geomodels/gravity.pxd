# -*- coding: utf-8 -*-
# cython: language_level=3
# distutils: language=c++

from libcpp.string cimport string

from .common cimport real


cdef extern from "GeographicLib/GravityModel.hpp" namespace "GeographicLib" nogil:
    cdef cppclass CGravityModel 'GeographicLib::GravityModel':
        # ctypedef enum mask:
        #     NONE,
        #     GRAVITY,
        #     DISTURBANCE,
        #     DISTURBING_POTENTIAL,
        #     SPHERICAL_ANOMALY,
        #     GEOID_HEIGHT,
        #     ALL

        CGravityModel(const string& name, const string& path) except +
        # @TODO: new in GeographicLib v1.50
        # CGravityModel(const string& name, const string& path,
        #              int Nmax, int Mmax) except +

        real Gravity(real lat, real lon, real h,
                     real& gx, real& gy, real& gz) const
        real Disturbance(real lat, real lon, real h,
                         real& deltax, real& deltay, real& deltaz) const
        real GeoidHeight(real lat, real lon) const
        void SphericalAnomaly(real lat, real lon, real h,
                              real& Dg01, real& xi, real& eta) const
        real W(real X, real Y, real Z, real& gX, real& gY, real& gZ) const
        real V(real X, real Y, real Z, real& GX, real& GY, real& GZ) const
        real T(real X, real Y, real Z,
               real& deltaX, real& deltaY, real& deltaZ) const
        real T(real X, real Y, real Z) const
        real U(real X, real Y, real Z,
               real& gammaX, real& gammaY, real& gammaZ) const
        real Phi(real X, real Y, real& fX, real& fY) const

        # GravityCircle Circle(real lat, real h, unsigned caps=ALL) const except +
        # const NormalGravity& ReferenceEllipsoid() const

        const string& Description() const
        const string& DateTime() const
        const string& GravityFile() const
        const string& GravityModelName() const
        const string& GravityModelDirectory() const
        real EquatorialRadius() const
        real MassConstant() const
        real ReferenceMassConstant() const
        real AngularVelocity() const
        real Flattening() const
        int Degree() const
        int Order() const
        real MajorRadius() const

        @staticmethod
        string DefaultGravityPath()

        @staticmethod
        string DefaultGravityName()
