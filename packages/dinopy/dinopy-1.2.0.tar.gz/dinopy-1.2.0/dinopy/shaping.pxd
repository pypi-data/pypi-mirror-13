# -*- coding: utf-8 -*-
from dinopy.definitions cimport *
cimport numpy as np
from cpython cimport bool
cimport cpython.array as array
from dinopy.definitions cimport *
from dinopy.shape cimport Shape
from libc.math cimport pow as cpow

# explicitly declare available functions, c-header style
cpdef object apply_shape(object qgram, object shape)
cpdef list windows_list(ref_genome, object qgram_shape)
cdef unsigned long _apply_shape_int(unsigned long qgram, Shape shape, int num_bits, bool sentinel= *)
cdef np.ndarray _apply_shape_numpy_array(np.ndarray qgram, Shape qgram_shape)
