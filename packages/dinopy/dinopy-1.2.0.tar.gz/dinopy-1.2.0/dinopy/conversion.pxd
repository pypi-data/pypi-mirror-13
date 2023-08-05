# -*- coding: utf-8 -*-
cimport cython
cimport numpy as np
from cpython cimport bool
from dinopy.definitions cimport *
from libc.stdlib cimport malloc, free
from libc.math cimport pow as cpow
from libc.math cimport log2 as clog2
from libc.math cimport ceil as cceil

# explicitly declare available functions, c-header style
cpdef bytes bytes_to_basenumbers(bytes byte_sequence, bool suppress_iupac= *)
cdef bytes _bytes_to_basenumbers(bytes byte_sequence)
cdef bytes _bytes_to_basenumbers_suppressed(bytes byte_sequence)
cdef bytes _bytearray_to_basenumber_bytes(bytearray byte_sequence)
cdef bytes _bytearray_to_basenumber_bytes_suppressed(bytearray byte_sequence)
cpdef str bytes_to_string(bytes byte_sequence, bool as_list= *)

cpdef bytes string_to_bytes(str sequence, bool suppress_iupac= *)
cpdef bytes string_to_basenumbers(str sequnece, bool suppress_iupac= *)
cpdef list string_list_to_basenumbers(list sequence_list, bool suppress_iupac= *)
cpdef list string_sublists_to_basenumbers(list list_of_lists, bool suppress_iupac= *)

cpdef object basenumbers_to_string(object nrseq, bool as_list= *)
cpdef bytes basenumbers_to_bytes(object basenumbers)

cdef object _change_dtype_bytearray(bytearray line, type dtype)
cdef object _change_dtype_bytes(bytes line, type dtype)

cpdef dict get_inverse_codemap_from_twobit(type dtype)

cpdef unsigned long encode_twobit(object seq, bool sentinel= *)
cpdef unsigned long encode_fourbit(object seq, bool sentinel= *)
cpdef unsigned long encode(object seq, object codemap, bool sentinel= *)

cpdef object decode_twobit(unsigned long seq, int length, type dtype= *)
cpdef object decode_fourbit(unsigned long seq, int length, type dtype= *)
cpdef list decode(unsigned long seq, int length, dict inv_codemap)

cpdef bytes phred_to_sanger(object phred_qs)
cpdef bytes phred_to_solexa(object phred_qs)
cpdef bytes phred_to_illumina13(object phred_qs)
cpdef bytes phred_to_illumina15(object phred_qs)
cpdef bytes phred_to_illumina18(object phred_qs)
cpdef list sanger_to_phred(object sanger_qvs)
cpdef list solexa_to_phred(object solexa_qvs)
cpdef list illumina13_to_phred(object illumina13_qvs)
cpdef list illumina15_to_phred(object illumina15_qvs)
cpdef list illumina18_to_phred(object illumina18_qvs)


