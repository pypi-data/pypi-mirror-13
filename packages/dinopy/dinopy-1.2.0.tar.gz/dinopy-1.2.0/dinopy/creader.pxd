# -*- coding: utf-8 -*-
from libc.stdio cimport *
from libc.stdlib cimport malloc, free
from cpython cimport bool

cdef extern from "stdio.h":
    int fileno(FILE *stream)

cdef class CReader:
    cdef FILE*cfile
    cdef str source
    cdef readonly bool closed

    cpdef close(self)
    cpdef int fileno(self)
    cpdef flush(self)
    cpdef bool isatty(self)
    cpdef bool readable(self)
    cpdef long seek(self, long offset, int whence= *)
    cpdef bool seekable(self)
    cpdef long tell(self)
    cpdef truncate(self, int size= *)
    cpdef bool writable(self)
    cpdef writelines(self, list lines)
    cpdef CReader open(self, str filename)
    cpdef bytes read(self, int num_bytes)
    cpdef bytes readline(self, int limit= *)
    cpdef int readinto(self, object sink)
    cpdef list readlines(self, int hint= *)
