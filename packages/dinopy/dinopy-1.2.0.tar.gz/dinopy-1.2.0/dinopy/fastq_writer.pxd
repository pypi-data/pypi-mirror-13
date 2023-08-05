# -*- coding: utf-8 -*-

cimport cython
from cpython cimport bool
from dinopy.definitions cimport basenumbers, two_bit, four_bit
from dinopy.conversion cimport basenumbers_to_bytes, string_to_bytes
from .output_opener cimport OutputOpener

cdef class FastqWriter(OutputOpener):

    cpdef write_reads(
            self,
            object reads,
            bool quality_values= *,
            type dtype= *,
    )

    cpdef write(
            self,
            object seq,
            bytes name,
            bytes quality_values= *,
            type dtype= *,
    )

    cdef _write_bytes(self, bytes seq, bytes name, bytes quality_values)
