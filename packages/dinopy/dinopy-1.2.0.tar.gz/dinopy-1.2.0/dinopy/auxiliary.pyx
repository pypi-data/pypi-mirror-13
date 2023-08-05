# -*- coding: utf-8 -*-
"""This module contains helpful functions for testing.

  - A q-gram generator, that creates all qgrams of a given length in
    a specified dtype.

"""
from random import choice
from numpy import array
from .exceptions import InvalidDtypeError

cimport cython

def qgram_generator(int size, type dtype=basenumbers):
    """Create an iterator over *all* different qgrams of the given size.

    Arguments:
        size (int): Length of the q-grams that will be created.
        dtype (type): Type of the created q-grams. (see: :ref:`dtype`)

    Yields:
        dtype: All q-grams of the given length (size).

    Raises:
        InvalidDtypeError: If an unsupported dtype has been passed.
    """
    cdef object base

    if dtype == str:
        base = "ACGT"
    elif dtype == basenumbers:
        base = b"\x00\x01\x10\x11"
    elif dtype == bytes:
        base = b"ACGT"
    elif dtype == bytearray:
        base = bytearray([BASE_A, BASE_C, BASE_G, BASE_T])
    else:
        raise InvalidDtypeError("Unsupported dtype {}".format(str(dtype)))
    for i in range(0, <long> cpow(4, size) - 1):
        yield _int_to_base(i, size, base)

cpdef _int_to_base(long l, int size, object base):
    """Converts an integer representation to the representation induced by `base`.
    For example `_int_to_base(3, 4, ['A', 'C', 'G', 'T'])` results in `AAAT`.

    Arguments:
        l (long): an integer representation of a sequence
        size (int): the sequence's length
        base (object): an array of base value items, such as `['A', 'C', 'G', 'T']` or `[0, 1, 2, 3]`.

    Returns:
        bytes or str: The dtype version of the given integer encoded q-gram.
    """
    cdef int base_length = len(base)
    cdef long m = 0
    cdef list qgram = []
    while size > 0:
        m = l % base_length
        qgram.append(base[m])
        l /= base_length
        size -= 1
    if isinstance(base, bytes):
        return bytes(qgram[::-1])
    elif isinstance(base, bytearray):
        return bytearray(qgram[::-1])
    elif isinstance(base, str):
        return "".join(qgram[::-1])
    else:
        return qgram[::-1]

