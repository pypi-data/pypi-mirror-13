# -*- coding: utf-8 -*-
cimport numpy as np

# type definitions
ctypedef np.uint8_t CHARTYPE_t
ctypedef bint BOOLTYPE_t

cdef type FastaEntry, FastaRead, FastaChromosome, FastaChromosomeInfo, FastaGenome, FastqRead, FastqReadWithoutName, FastqReadWithoutQV, FastqLine

# strings containing all valid IUPAC characters
cdef unicode IUPAC_CHARACTERS, IUPAC_SHAPE_CHARACTERS

# constants for the byte-values of all IUPAC-characters as well as 
# fasta / fastq special characters (\n, space, >, @, +)
cdef:
    char NEWLINE_BYTE
    char GREATER_BYTE
    char AT_BYTE
    char PLUS_BYTE
    char SPACE_BYTE

    char BASE_A
    char BASE_C
    char BASE_G
    char BASE_T
    char BASE_LOWER_A
    char BASE_LOWER_C
    char BASE_LOWER_G
    char BASE_LOWER_T

    char BASE_N
    char BASE_U
    char BASE_R
    char BASE_Y
    char BASE_M
    char BASE_K
    char BASE_W
    char BASE_S
    char BASE_B
    char BASE_D
    char BASE_H
    char BASE_V
    char BASE_LOWER_N
    char BASE_LOWER_U
    char BASE_LOWER_R
    char BASE_LOWER_Y
    char BASE_LOWER_M
    char BASE_LOWER_K
    char BASE_LOWER_W
    char BASE_LOWER_S
    char BASE_LOWER_B
    char BASE_LOWER_D
    char BASE_LOWER_H
    char BASE_LOWER_V

# possible states of the fastq parser
cdef enum FASTQ_PARSER_STATE:
    START, NAME, SEQUENCE, PLUS, QUALITY_VALUES

# make the conversion datastructures publicly available
cdef:
    int *_basenumber_array
    int *_basenumber_array_suppressed
    dict _basenumber_from_byte
    dict _basenumber_from_byte_suppressed
    dict _basenumber_from_unicode
    dict _basenumber_from_unicode_suppressed

    dict _unicode_from_basenumber
    dict _unicode_from_byte
    dict _unicode_from_byte_suppressed

    dict _byte_from_unicode
    dict _byte_from_unicode_suppressed
    dict _byte_from_basenumber

    dict _str_from_2bit
    dict _byte_from_2bit
    dict _basenumber_from_2bit
    dict _str_from_4bit
    dict _byte_from_4bit
    dict _basenumber_from_4bit

    dict _2bit_from_any
    dict _4bit_from_any

    dict _iupac_mapping
    dict _iupac_complement
    dict _complement

    dict linetype_as_str

cdef set valid_dtypes

cdef class IUPACRandomReplacementDict(dict):
    cdef dict __dict__

cpdef IUPACRandomReplacementDict _2bit_from_any_with_iupac_replacement

# Dummy classes to specify data types of sequences
cdef class basenumbers(object):
    """Basenumbers type for dtype parameters.

    - A → 0
    - C → 1
    - G → 2
    - T → 3
    - ...

    Represents bases as integer numbers (saved as bytes).
    See :ref:`dtype` for details.
    """
    pass

cdef class two_bit(object):
    """Two bit encoding type for encoding parameters.

    - A → 0b00
    - C → 0b01
    - G → 0b10
    - T → 0b11

    Encode q-grams as integer numbers using 2bit encoding.
    See :ref:`dtype` for details.
    """
    pass

cdef class four_bit(object):
    """Four bit encoding type for encoding parameters.

    - A → 0b0001
    - C → 0b0010
    - G → 0b0100
    - T → 0b1000
    - ...
    - N → 0b1111

    Encode q-grams as integer numbers using 4bit encoding.
    See :ref:`dtype` for details.
    """
    pass

ctypedef fused seq_type:
    str
    bytes
    bytearray
    basenumbers
    two_bit
    four_bit