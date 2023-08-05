# -*- coding: utf-8 -*-
from cpython cimport bool, PyObject_CheckBuffer
cimport numpy as np
from libc.math cimport pow as cpow

from dinopy.definitions cimport *

from dinopy.conversion cimport encode, encode_twobit, encode_fourbit
from dinopy.shape cimport Shape
from .definitions cimport valid_dtypes
from .definitions cimport _iupac_mapping

cpdef reverse_complement(object seq)
cdef object _reverse_complement(object seq)
cpdef unsigned long reverse_complement_2bit(unsigned long seq)
cpdef unsigned long reverse_complement_4bit(unsigned long seq)
cpdef complement(object seq)
cdef object _forward_complement(object seq)
cpdef unsigned long complement_2bit(unsigned long seq)
cpdef unsigned long complement_4bit(unsigned long seq)
cpdef np.uint64_t[:] suffix_array(object sequence)
