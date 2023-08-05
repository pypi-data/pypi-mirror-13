# -*- coding: utf-8 -*-
cimport cython

from dinopy.input_opener cimport InputOpener as InputOpener
from dinopy.definitions cimport *
from dinopy.conversion cimport _change_dtype_bytearray, _change_dtype_bytes

cdef class FastaReader:
    cdef str _fai_path
    cdef object _source, _fai

    cpdef genome(self, dtype= *)
    cdef _genome_str(self)
    cpdef random_access(self, object selected_chromosome, int start, int end, dtype=*)
