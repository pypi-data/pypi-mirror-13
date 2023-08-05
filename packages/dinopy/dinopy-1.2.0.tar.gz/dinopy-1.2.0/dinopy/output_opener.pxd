# -*- coding: utf-8 -*-
from cpython cimport bool

cdef class OutputOpener:
    cdef object sink
    cdef object writer
    cdef str output_type
    cdef bool output_closable, append, force_overwrite, opened
    cdef str mode

    cpdef bool is_open(self)
    cpdef object __enter__(self)
    cpdef __exit__(self, object type, object value, object traceback)
    cpdef close(self)
