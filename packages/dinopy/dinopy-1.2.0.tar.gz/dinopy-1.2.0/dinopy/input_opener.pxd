# -*- coding: utf-8 -*-
from cpython cimport bool

cdef class InputOpener:
    cdef object source
    cdef object input_iterable
    cdef bool input_closable, native_io

    cpdef object __enter__(self)
    cpdef __exit__(self, object type, object value, object traceback)
