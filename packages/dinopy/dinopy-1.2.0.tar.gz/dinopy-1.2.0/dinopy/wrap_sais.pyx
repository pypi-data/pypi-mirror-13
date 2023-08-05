# Note: obviously specifying both the distutils hints *and* extern from *.cpp breaks things.
## distutils: language = c++
## distutils: sources = dinopy/cpp/sais.cpp
from cpython.mem cimport PyMem_Malloc, PyMem_Free

cdef extern from "cpp/sais.cpp":
   cdef void SA_IS(unsigned char *s, int* SA, int n, int K, int cs, int level)
#cdef extern void SA_IS(unsigned char *s, int* SA, int n, int K, int cs)

cdef int* suffix_array(bytes sequence):
    cdef:
        int n = len(sequence), num_buckets = 128, sizeof_char = 8
        unsigned char* s = <unsigned char*> sequence
        int* SA = <int*> PyMem_Malloc(n * sizeof(int))
    SA_IS(s, SA, n, num_buckets, sizeof_char, 0)
    return SA
    #PyMem_Free(SA)
#cdef extern void SA_IS(unsigned char *s, int* SA, int n, int K, int cs)
