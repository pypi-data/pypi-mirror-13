# -*- coding: utf-8 -*-
cimport cython
from dinopy.definitions cimport *
from cpython cimport bool
cimport numpy as np

cdef class Shape:
    cdef readonly np.ndarray bool_shape
    cdef readonly list index_shape_care, index_shape_dont_care
    cdef readonly int length, num_care, num_dont_care
    cdef str representation
    cdef bool solid

    cpdef bool is_solid(self)
    cdef np.ndarray _parse_bool_shape(self, object shape)
    cdef _bshape_from_str(self, np.ndarray bshape, str shape)
    cdef _bshape_from_bytes(self, np.ndarray bshape, bytes shape)
    cdef _bshape_from_list(self, np.ndarray bshape, list items)
