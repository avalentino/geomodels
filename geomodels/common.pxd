# -*- coding: utf-8 -*-
# cython: language_level=3
# distutils: language=c++

cdef extern from "GeographicLib/Config.h":
    const int GEOGRAPHICLIB_VERSION_MAJOR
    const int GEOGRAPHICLIB_VERSION_MINOR
    const int GEOGRAPHICLIB_VERSION_PATCH
    const int GEOGRAPHICLIB_VERSION
    const char[] GEOGRAPHICLIB_VERSION_STRING


cdef extern from "GeographicLib/Constants.hpp":
    int GEOGRAPHICLIB_VERSION_NUM(int, int, int)


cdef extern from "GeographicLib/Math.hpp" namespace "GeographicLib":
    cdef cppclass Math:
        ctypedef double real


ctypedef Math.real real
