# -*- coding: utf-8 -*-
"""This module provides functions for the conversion between the data types used by dinopy.

This includes:

    - str
    - bytes
    - bytearray
    - :class:`dinopy.basenumbers <dinopy.basenumbers>`
    - 2bit and 4bit encoded sequences

For a full list of data types used by dinopy please take a look at :ref:`dtype`.

"""
import array
import numpy as np
from .exceptions import InvalidDtypeError, InvalidEncodingError, InvalidIUPACAmbiguityCodeError

cimport cython


# bytes to *
@cython.wraparound(False)
cpdef bytes bytes_to_basenumbers(bytes byte_sequence, bool suppress_iupac=False):
    """Translate a sequence of bytes into a basenumber sequence.

    Arguments:
        byte_sequence(bytes): Bases encoded as ascii values
            (65 → A, 67 → C, ...) Works for upper and lower case characters.
        suppress_iupac(bool): If this is set, all non-ACGT-characters will be
            replaced with N. (Default: False)

    Returns:
        bytes: A bytes object containing the sequence encoded as basenumbers.
    """
    if suppress_iupac:
        return _bytes_to_basenumbers_suppressed(byte_sequence)
    else:
        return _bytes_to_basenumbers(byte_sequence)

@cython.wraparound(False)
cdef bytes _bytes_to_basenumbers(bytes byte_sequence):
    """Translate a sequence of bytes into a basenumber sequence.

    Arguments:
        byte_sequence(bytes): Bases encoded as ascii values
            (65 → A, 67 → C, ...) Works for upper and lower case characters.

    Returns:
        bytes: A bytes object containing the sequence encoded as basenumbers.
    """
    cdef int index
    cdef bytes byte
    cdef bytearray basenumber_sequence = bytearray(len(byte_sequence))

    try:
        for index, byte in enumerate(byte_sequence):
            basenumber_sequence[index] = _basenumber_from_byte[byte[0]]  # using byte[0] instead of ord(byte)
        return bytes(basenumber_sequence)
    except KeyError as ke:
        raise InvalidIUPACAmbiguityCodeError(ke)

@cython.wraparound(False)
cdef bytes _bytes_to_basenumbers_suppressed(bytes byte_sequence):
    """Translate bytes into a basenumber seq replacing all non-ACGT chars with N.

    Arguments:
        byte_sequence(bytes): Bases encoded as ascii values
            (65 → A, 67 → C, ...) Works for upper and lower case characters.

    Returns:
        bytes: A bytes object containing the sequence encoded as basenumbers.
        All non-ACGT characters, such as IUPAC characters, are replaced with N.
    """
    cdef int index
    cdef bytes byte
    cdef bytearray basenumber_sequence = bytearray(len(byte_sequence))

    try:
        for index, byte in enumerate(byte_sequence):
            basenumber_sequence[index] = _basenumber_from_byte_suppressed[byte[0]]  # using byte[0] instead of ord(byte)
        return bytes(basenumber_sequence)
    except KeyError as ke:
        raise InvalidIUPACAmbiguityCodeError(ke)

@cython.wraparound(False)
cdef bytes _bytearray_to_basenumber_bytes(bytearray byte_sequence):
    """Translate a sequence of bytes into a basenumber sequence.

    Arguments:
        byte_sequence(bytearray): Bases encoded as ascii values
            (65 → A, 67 → C, ...) Works for upper and lower case characters.

    Returns:
        bytes: A bytes object containing the sequence encoded as basenumbers.
    """
    cdef int index, byte
    cdef bytearray basenumber_sequence = bytearray(len(byte_sequence))

    try:
        for index, byte in enumerate(byte_sequence):
            basenumber_sequence[index] = _basenumber_from_byte[byte]  # using byte[0] instead of ord(byte)
        return bytes(basenumber_sequence)
    except KeyError as ke:
        raise InvalidIUPACAmbiguityCodeError(ke)

@cython.wraparound(False)
cdef bytes _bytearray_to_basenumber_bytes_suppressed(bytearray byte_sequence):
    """Translate bytes into a basenumber seq replacing all non-ACGT chars with N.

    Arguments:
        byte_sequence(bytearray): Bases encoded as ascii values
            (65 → A, 67 → C, ...) Works for upper and lower case characters.

    Returns:
        bytes: A bytes object containing the sequence encoded as basenumbers.
        All non-ACGT characters, such as IUPAC characters, are replaced with N.
    """
    cdef int index, byte
    cdef bytearray basenumber_sequence = bytearray(len(byte_sequence))

    try:
        for index, byte in enumerate(byte_sequence):
            basenumber_sequence[index] = _basenumber_from_byte_suppressed[byte]  # using byte[0] instead of ord(byte)
        return bytes(basenumber_sequence)
    except KeyError as ke:
        raise InvalidIUPACAmbiguityCodeError(ke)

@cython.wraparound(False)
cpdef str bytes_to_string(bytes byte_sequence, bool as_list=False):
    """Translate bytes into a string.

    Arguments:
        byte_sequence(bytes): Bases encoded as ascii values
            (65 → A, 67 → C, ...) Works for upper and lower case characters.
        as_list(bool): Returns the string as a list of charcters instead
             of a (joined) string. (Default: False)
    Returns:
        str or list: A string containing the dna seqeunce encoded as unicode text
        or a list containing the unjoined characters.
    """
    try:
        if as_list:
            return [_unicode_from_byte[i] for i in byte_sequence]
        else:
            return "".join([_unicode_from_byte[i] for i in byte_sequence])
    except KeyError as ke:
        raise InvalidIUPACAmbiguityCodeError(ke)

################################################################################

# string to *
@cython.wraparound(False)
cpdef bytes string_to_bytes(str sequence, bool suppress_iupac=False):
    """Translate a string to a byte sequence.

    Arguments:
        sequence(str): String of IUPAC-characters (upper or lower case).
        suppress_iupac(bool): If this is set, all non-ACGT-characters will be
            replaced with N. (Default: False)

    Returns:
        bytes: A bytes object containing the sequence encoded as bytes.
    """
    try:
        if suppress_iupac:
            return bytes([_byte_from_unicode_suppressed[i] for i in sequence])
        else:
            return bytes([_byte_from_unicode[i] for i in sequence])
    except KeyError as ke:
        raise InvalidIUPACAmbiguityCodeError(ke)

@cython.wraparound(False)
cpdef bytes string_to_basenumbers(str sequence, bool suppress_iupac=False):
    """Translate a string to a sequence of basenumbers.

    Arguments:
        sequence(string): String of IUPAC-characters (upper or lower case).
        suppress_iupac(bool): If this is set, all non-ACGT-characters will be
            replaced with N. (Default: False)

    Returns:
        bytes: A bytes object containing the sequence encoded as basenumbers.
    """
    try:
        if suppress_iupac:
            return bytes([_basenumber_from_unicode_suppressed[i] for i in sequence])
        else:
            return bytes([_basenumber_from_unicode[i] for i in sequence])
    except KeyError as ke:
        raise InvalidIUPACAmbiguityCodeError(ke)

@cython.wraparound(False)
cpdef list string_list_to_basenumbers(list sequence_list, bool suppress_iupac=False):
    """Translate a list of sequences from string to basenumbers.
        Can be used to translate whole reads with a single call.

    Arguments:
        base_list(list of strings): List of strings of IUPAC-characters
            (upper or lower case).
        suppress_iupac(bool): If this is set, all non-ACGT-characters will be
            replaced with N. (Default: False)

    Returns:
        list of bytes: A list containing bytes object containing the sequences encoded as basenumbers.
    """
    return [string_to_basenumbers(seq, suppress_iupac) for seq in sequence_list]

@cython.wraparound(False)
cpdef list string_sublists_to_basenumbers(list list_of_lists, bool suppress_iupac=False):
    """Translate a list of lists of sequences from string to basenumbers.
        Can be used to translate whole lists of reads.

    Warning: this might consume a lot of memory.

    Arguments:
        base_list(nested list of strings): List of lists of strings of IUPAC-characters
            (upper or lower case).
        suppress_iupac(bool): If this is set, all non-ACGT-characters will be
            replaced with N. (Default: False)

    Returns:
        list of list of bytes: A list of lists containing bytes object containing the sequences encoded as basenumbers.
    """
    if suppress_iupac:
        return [string_list_to_basenumbers(base_list, suppress_iupac=True) for base_list in list_of_lists]
    else:
        return [string_list_to_basenumbers(base_list) for base_list in list_of_lists]

################################################################################

# basenumbers to *
@cython.wraparound(False)
cpdef object basenumbers_to_string(object basenumbers, bool as_list=False):
    """Translate a sequence from basenumbers to string

    Arguments:
        basenumbers(iterable): Containing basenumbers (0 → A, 1 → C, ...)
        as_list(bool): Returns the string as a list of charcters instead
             of a (joined) string. (Default: False)

    Returns:
        str: A string containing the sequence.
        If as_list has been set to True, the string will be returned as
        a list of characters.
    """
    try:
        if as_list:
            return [_unicode_from_basenumber[i] for i in basenumbers]
        else:
            return "".join([_unicode_from_basenumber[i] for i in basenumbers])
    except KeyError as ke:
        raise InvalidIUPACAmbiguityCodeError(ke)

@cython.wraparound(False)
cpdef bytes basenumbers_to_bytes(object basenumbers):
    """Translate a sequence from basenumbers to bytes

    Arguments:
        basenumbers(Iterable): Containing basenumbers (0 → A, 1 → C, ...)

    Returns:
        bytes: A bytes object containing the sequence encoded as ascii bytes.
    """
    try:
        return bytes([_byte_from_basenumber[i] for i in basenumbers])
    except KeyError as ke:
        raise InvalidIUPACAmbiguityCodeError(ke)

################################################################################

# change dtype of bytes and bytearrays, this is needed for writing files


@cython.wraparound(False)
cdef object _change_dtype_bytearray(bytearray line, type dtype):
    """Encode the line (bytearray) in the given dtype.

    Arguments:
        line(buffer of characters): A bytearray-encoded line (this can be
            a sequence or a name.)
        dtype(type): Desired data type. (See :ref:`dtype`)

    Returns:
        dtype: The line converted to the specified data type.

    Raises:
        InvalidDtypeError: If an unknown dtype is encountered.
    """
    if dtype == bytes:
        return bytes(line)
    elif dtype == bytearray:
        return line
    elif dtype == basenumbers:
        return _bytearray_to_basenumber_bytes(line)
    elif dtype == str:
        # as line is not restricted to sequences the function
        # bytes_to_string as defined above is NOT sufficient for
        # this conversion.
        return "".join(map(chr, line))
    else:
        raise InvalidDtypeError("Unknown dtype: {}".format(dtype))

@cython.wraparound(False)
cdef object _change_dtype_bytes(bytes line, type dtype):
    """Encode the line (bytes) in the given dtype.

    Arguments:
        line(buffer of characters): A byte-encoded line (this can be
            a sequence or a name.)
        dtype(type): Desired data type. (See :ref:`dtype`)

    Returns:
        dtype: The line converted to the specified data type.

    Raises:
        InvalidDtypeError: If an unknown dtype is encountered.
    """
    if dtype == bytes:
        return line
    elif dtype == bytearray:
        return bytearray(line)
    elif dtype == basenumbers:
        return _bytes_to_basenumbers(line)
    elif dtype == int:
        return _bytes_to_basenumbers(line)
    elif dtype == str:
        # as line is not restricted to sequences the function
        # bytes_to_string as defined above is NOT sufficient for
        # this conversion.
        return "".join(map(chr, line))
    else:
        raise InvalidDtypeError("Unknown dtype: {}".format(dtype))

def _test_encode_line(line, dtype):
    """Wrapper function for testing purposes only"""
    return (_change_dtype_bytearray(line, dtype))

################################################################################

# encoding decoding of bit encoded qgrams

cpdef dict get_inverse_codemap_from_twobit(type dtype):
    """Return the translation map from a two bit encoding to the respective
    dtype, e.g. from two bit to string: `0b00` → `A`, `0b01` → `C` etc.

    Arguments:
        dtype (type): Target dtype for the codemap.

    Returns:
        dict: Translation dict (codemap) from 2bit encoding to the given dtype.

    Raises:
        InvalidDtypeError: If the dtype is not supported / recognized.
    """
    if dtype == str:
        return _str_from_2bit
    elif dtype in (bytes, bytearray):
        return _byte_from_2bit
    elif dtype == basenumbers:
        return _basenumber_from_2bit
    else:
        raise InvalidDtypeError("Unrecognized dtype {}.".format(dtype))

cpdef unsigned long encode_twobit(object seq, bool sentinel=False):
    """Encodes the given sequence using a two bit encoding.
    Note that all two bit encoded sequences share the common prefix :code:`0b11`
    for easier decoding.
    If the sequence contains items other than `'A', 'C', 'G', 'T'`, they will
    be replaced randomly according to the usual :ref:`iupac_mapping`.

    Arguments:
        seq (object): The sequence to be 2bit encoded. Supports any dtype (see: :ref:`dtype`).
        sentinel (bool): Whether to prepend sentinel bits to the resulting sequence;
            this is useful if encoding sequences of variable lengths (but not really
            useful for sequences with fixed and known lengths, such as q-grams).
            If set to `True`, prepend n ones to the resulting sequence,
            where n is the number of bits needed to represent an item of the codemap.
            (Default: `False`).

    Returns:
        unsigned long: The two bit encoded sequence as a single `unsigned long` integer.
    """
    return encode(seq, _2bit_from_any_with_iupac_replacement, sentinel)

cpdef unsigned long encode_fourbit(object seq, bool sentinel=False):
    """Encodes the given sequence using a four bit encoding.
    Note that all four bit encoded sequences share the common prefix :code:`0b1111`
    for easier decoding.

    Arguments:
        seq (object): The sequence to be 4bit encoded. Supports any dtype (see: :ref:`dtype`).
        sentinel (bool): Whether to prepend sentinel bits to the resulting sequence;
            this is useful if encoding sequences of variable lengths (but not really
            useful for sequences with fixed and known lengths, such as q-grams).
            If set to `True`, prepend n ones to the resulting sequence,
            where n is the number of bits needed to represent an item of the codemap.
            (Default: `False`).

    Returns:
        unsigned long: The four bit encoded sequence as a single `unsigned long` integer.
    """
    return encode(seq, _4bit_from_any, sentinel)

cpdef unsigned long encode(object seq, object codemap, bool sentinel=False):
    """Translates an iterable sequence to a long representation using the given codemap

    Arguments:
        seq (object): The iterable sequence to be encoded.
        codemap (dict): A dictionary specifying a mapping from an item in seq to some bits.
        sentinel (bool): Whether to prepend sentinel bits to the resulting sequence;
            this is useful if encoding sequences of variable lengths (but not really
            useful for sequences with fixed and known lengths, such as q-grams).
            If set to `True`, prepend n ones to the resulting sequence,
            where n is the number of bits needed to represent an item of the codemap.
            (Default: `False`).

    Returns:
        unsigned long: Value encoding the given sequence in a more compact bitstring version.

    Note:
        This is a generic encode functions and requires a codemap (dictionary containing a
        translation for each possible item of the sequence).

        Codemaps to translate all dtypes to 2bit and 4bit are available in the :mod:`dinopy.definitions`
        module. For these translations you can use the specialized functions :func:`encode_twobit` and
        :func:`encode_fourbit`.
    """
    # using "dict codemap" doesn't work for IUPACRandomReplacementDict even though it is a dict...
    cdef int bits_needed = <int> cceil(clog2(len(set(codemap.values()))))  # different keys may map to the same value
    cdef unsigned long bits = 0
    if sentinel:
        bits = <unsigned long> cpow(2, bits_needed) - 1  # ensure common prefix for easier decoding
    for c in seq:
        bits <<= bits_needed
        bits |= codemap[c]
    return bits

cpdef object decode_twobit(unsigned long twobit_seq, int length, type dtype=bytes):
    """Decode a 2bit encoded sequence into a sequence of type `dtype`. Inverse of :meth:`encode_twobit`.

    Arguments:
        twobit_seq (unsigned long): A 2bit representation of a sequence, as produced by :meth:`encode`.
        length (int): The length of the original ('decoded') sequence. If :code:`length == -1`,
            assume leading sentinel bits, i.e. n ones where n is the number of bits needed
            to represent an item of the codemap.
        dtype (type): Target dtype to decode the sequence to (see :ref:`dtype`).

    Returns:
        dtype: The sequence obtained by applying the inverse of :meth:`encode` to a bit representation of said sequence.

    Raises:
        InvalidDtypeError: If an unrecognized dtype has been passed.
    """
    if dtype == bytes:
        return bytes(decode(twobit_seq, length, _byte_from_2bit))
    elif dtype == bytearray:
        return bytearray(decode(twobit_seq, length, _byte_from_2bit))
    elif dtype in (str, unicode):
        return "".join(decode(twobit_seq, length, _str_from_2bit))
    elif dtype == basenumbers:
        return bytes(decode(twobit_seq, length, _basenumber_from_2bit))
    else:
        raise InvalidDtypeError("Invalid dtype {}".format(dtype))

cpdef object decode_fourbit(unsigned long fourbit_seq, int length, type dtype=bytes):
    """Decode a 4bit encoded sequence into dtype. Inverse of :meth:`encode_fourbit`.

    Arguments:
        fourbit_seq (unsigned long): A 4bit representation of a sequence, as produced by :meth:`encode_fourbit`.
        length (int): The length of the original ('decoded') sequence. If :code:`length == -1`,
            assume leading sentinel bits, i.e. n ones where n is the number of bits needed
            to represent an item of the codemap.
        dtype (type): Target dtype to decode the sequence to (see :ref:`dtype`).

    Returns:
        the decoded sequence of type `dtype`.

    Raises:
        InvalidDtypeError: If an unrecognized dtype has been passed.
    """
    if dtype == bytes:
        return bytes(decode(fourbit_seq, length, _byte_from_4bit))
    elif dtype == bytearray:
        return bytearray(decode(fourbit_seq, length, _byte_from_4bit))
    elif dtype in (str, unicode):
        return "".join(decode(fourbit_seq, length, _str_from_4bit))
    elif dtype == basenumbers:
        return bytes(decode(fourbit_seq, length, _basenumber_from_4bit))
    else:
        raise InvalidDtypeError("Invalid dtype {}".format(dtype))

cpdef list decode(unsigned long bit_seq, int length, dict inv_codemap):
    """Decode a bit encoded sequence. Inverse of :meth:`dinopy.auxiliary.encode`.

    Arguments:
        seq (unsigned long): A bit representation of a sequence, as produced by :meth:`encode`.
        length (int): The length of the original ('decoded') sequence. If :code:`length == -1`,
            assume leading sentinel bits, i.e. n ones where n is the number of bits needed
            to represent a single item of the codemap.
        inv_codemap (dict): The inverse map of the map used in :meth:`encode`.

    Returns:
        list: The sequence obtained by applying the inverse of :meth:`encode` to a bit representation of said sequence.

    Note:
        This is a generic decode functions and requires a codemap (dictionary containing a
        translation for each possible item of the sequence).

        Codemaps to translate to 2bit and 4bit to all dtypes are available in the :mod:`dinopy.definitions`
        module. For these translations you can use the specialized functions :func:`decode_twobit` and
        :func:`decode_fourbit`.
    """
    cdef list seq
    cdef int bits_needed = <int> cceil(clog2(len(inv_codemap)))
    cdef unsigned long mask = <unsigned long> cpow(2, bits_needed) - 1
    if length == -1:  # with sentinel bits
        length = bit_seq.bit_length() / bits_needed - 1  # -1 to skip common prefix
    seq = []
    for _ in range(length):
        seq.append(inv_codemap[bit_seq & mask])
        bit_seq >>= bits_needed
    return seq[::-1]


################################################################################

# conversion of quality values <-> quality scores

cpdef bytes phred_to_sanger(object phred_qs):
    """Translate phred quality scores to sanger quality values.

    Arguments:
        phred_qs (int buffer): PHRED quality scores.

    Returns:
        bytes: Sanger quality values.
    """
    cdef:
        int length = len(phred_qs)
        int i
        # allocate an array of integers of length equal to the input
        cdef unsigned int *quality_values = <unsigned int *> malloc(length * sizeof(int))
    try:
        # add the offset to each item in the input
        for i in range(length):
            quality_values[i] = phred_qs[i] + 33
        return bytes([quality_values[i] for i in range(length)])
    finally:
        # return allocated memory to system
        free(quality_values)

cpdef bytes phred_to_solexa(object phred_qs):
    """Translate phred quality scores to solexa quality values.

    Arguments:
        phred_qs (int buffer): PHRED quality scores.

    Returns:
        bytes: Solexa quality values.
    """
    cdef:
        int length = len(phred_qs)
        int i
        # allocate an array of integers of length equal to the input
        cdef unsigned int *quality_values = <unsigned int *> malloc(length * sizeof(int))
    try:
        # add the offset to each item in the input
        for i in range(length):
            quality_values[i] = phred_qs[i] + 64
        return bytes([quality_values[i] for i in range(length)])
    finally:
        # return allocated memory to system
        free(quality_values)

cpdef bytes phred_to_illumina13(object phred_qs):
    """Translate phred quality scores to illumina 1.3 quality values.

    Arguments:
        phred_qs (int buffer): PHRED quality scores.

    Returns:
        bytes: Illumina 1.3 quality values.
    """
    cdef:
        int length = len(phred_qs)
        int i
        # allocate an array of integers of length equal to the input
        cdef unsigned int *quality_values = <unsigned int *> malloc(length * sizeof(int))
    try:
        # add the offset to each item in the input
        for i in range(length):
            quality_values[i] = phred_qs[i] + 64
        return bytes([quality_values[i] for i in range(length)])
    finally:
        # return allocated memory to system
        free(quality_values)

cpdef bytes phred_to_illumina15(object phred_qs):
    """Translate phred quality scores to illumina 1.5 quality values.

    Arguments:
        phred_qs (int buffer): PHRED quality scores.

    Returns:
        bytes: Illumina 1.5 quality values.
    """
    cdef:
        int length = len(phred_qs)
        int i
        # allocate an array of integers of length equal to the input
        cdef unsigned int *quality_values = <unsigned int *> malloc(length * sizeof(int))
    try:
        # add the offset to each item in the input
        for i in range(length):
            quality_values[i] = phred_qs[i] + 64
        return bytes([quality_values[i] for i in range(length)])
    finally:
        # return allocated memory to system
        free(quality_values)

cpdef bytes phred_to_illumina18(object phred_qs):
    """Translate phred quality scores to illumina 1.8 quality values.

    Arguments:
        phred_qs (int buffer): PHRED quality scores.

    Returns:
        bytes: Illumina 1.8 quality values.
    """
    cdef:
        int length = len(phred_qs)
        int i
        # allocate an array of integers of length equal to the input
        cdef unsigned int *quality_values = <unsigned int *> malloc(length * sizeof(int))
    try:
        # add the offset to each item in the input
        for i in range(length):
            quality_values[i] = phred_qs[i] + 33
        return bytes([quality_values[i] for i in range(length)])
    finally:
        # return allocated memory to system
        free(quality_values)

cpdef list sanger_to_phred(object sanger_qvs):
    """Translate sanger quality values to phred quality scores.

    Arguments:
        sanger_qvs (int buffer): Sanger quality values.

    Returns:
        list: PHRED quality scores.
    """
    cdef:
        int i
        int length = len(sanger_qvs)
        # allocate an array of integers of length equal to the input
        cdef int *quality_scores = <int *> malloc(length * sizeof(int))
    try:
        for i in range(length):
            quality_scores[i] = sanger_qvs[i] - 33
        # convert array to python type for return
        return [quality_scores[i] for i in range(length)]
    finally:
        # return allocated memory to system
        free(quality_scores)

cpdef list solexa_to_phred(object solexa_qvs):
    """Translate solexa quality values to phred quality scores.

    Arguments:
        solexa_qvs (int buffer): Solexa quality values.

    Returns:
        list: PHRED quality scores.
    """
    cdef:
        int i
        int length = len(solexa_qvs)
        # allocate an array of integers of length equal to the input
        cdef int *quality_scores = <int *> malloc(length * sizeof(int))
    try:
        for i in range(length):
            quality_scores[i] = solexa_qvs[i] - 64
        # convert array to python type for return
        return [quality_scores[i] for i in range(length)]
    finally:
        # return allocated memory to system
        free(quality_scores)

cpdef list illumina13_to_phred(object illumina13_qvs):
    """Translate illumina 1.3 quality values to phred quality scores.

    Arguments:
        illumina13_qvs (int buffer): Illumina 1.3 quality values.

    Returns:
        list: PHRED quality scores.
    """
    cdef:
        int i
        int length = len(illumina13_qvs)
        # allocate an array of integers of length equal to the input
        cdef int *quality_scores = <int *> malloc(length * sizeof(int))
    try:
        for i in range(length):
            quality_scores[i] = illumina13_qvs[i] - 64
        # convert array to python type for return
        return [quality_scores[i] for i in range(length)]
    finally:
        # return allocated memory to system
        free(quality_scores)

cpdef list illumina15_to_phred(object illumina15_qvs):
    """Translate illumina 1.5 quality values to phred quality scores.

    Arguments:
        illumina153_qvs (int buffer): Illumina 1.5 quality values.

    Returns:
        list: PHRED quality scores.
    """
    cdef:
        int i
        int length = len(illumina15_qvs)
        # allocate an array of integers of length equal to the input
        cdef int *quality_scores = <int *> malloc(length * sizeof(int))
    try:
        for i in range(length):
            quality_scores[i] = illumina15_qvs[i] - 64
        # convert array to python type for return
        return [quality_scores[i] for i in range(length)]
    finally:
        # return allocated memory to system
        free(quality_scores)

cpdef list illumina18_to_phred(object illumina18_qvs):
    """Translate illumina 1.8 quality values to phred quality scores.

    Arguments:
        illumina18_qvs (int buffer): Illumina 1.8 quality values.

    Returns:
        list: PHRED quality scores.
    """
    cdef:
        int i
        int length = len(illumina18_qvs)
        # allocate an array of integers of length equal to the input
        cdef int *quality_scores = <int *> malloc(length * sizeof(int))
    try:
        for i in range(length):
            quality_scores[i] = illumina18_qvs[i] - 33
        # convert array to python type for return
        return [quality_scores[i] for i in range(length)]
    finally:
        # return allocated memory to system
        free(quality_scores)
