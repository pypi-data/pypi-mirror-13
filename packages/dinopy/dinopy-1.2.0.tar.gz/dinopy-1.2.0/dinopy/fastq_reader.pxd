# -*- coding: utf-8 -*-
cimport cython

from dinopy.definitions cimport *
from cpython cimport bool
from dinopy.conversion cimport _change_dtype_bytes
from dinopy.input_opener cimport InputOpener

cdef class FastqReader:
    cdef int _last_state
    cdef object  _quality_tally
    cdef tuple _valid_states_before_name
    cdef bool _quality_tally_ready
    cdef object _source

    cpdef tuple _classify_line(self, bytes line, type dtype)

    cpdef int _ordering(self, str key)

    cpdef tuple guess_quality_format(self, int max_reads= *)

    cpdef print_quality_tally(self, file= *)
