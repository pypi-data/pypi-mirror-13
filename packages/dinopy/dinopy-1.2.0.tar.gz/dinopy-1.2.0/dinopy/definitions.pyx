# -*- coding: utf-8 -*-
"""This module contains all important definitions used by dinopy:

    - Custom types (like basenumbers and two_bit, see :ref:`dtype`)
    - Dictionaries used for conversions
    - Constants for the byte values of DNA- and FASTA-/FASTQ-characters
    - Return types (NamedTuple)

Note:
    Some of the defined variables, like the conversion dicts, are
    cdefed and can only be accessed from cython.
    To convert between sequence types please use the conversion methods from
    :mod:`dinopy.conversion`.
"""
from collections import namedtuple
from itertools import chain
from random import choice

cimport cython

FastaEntry = namedtuple("Entry", "sequence name length interval")
FastaGenome = namedtuple("Genome", "sequence info")
FastaChromosomeInfo = namedtuple("ChromosomeInfo", "name length interval")
FastaRead = namedtuple("Read", "sequence name")
FastaChromosome = namedtuple("Chromosome", "sequence name length")

FastqRead = namedtuple("Read", "sequence name quality")
FastqReadWithoutName = namedtuple("ReadWithoutName", "sequence quality")
FastqReadWithoutQV = namedtuple("ReadWithoutQV", "sequence name")
FastqLine = namedtuple("Line", "type value")

NEWLINE_BYTE = 10
GREATER_BYTE = 62
AT_BYTE = 64
PLUS_BYTE = 43
SPACE_BYTE = 32

IUPAC_CHARACTERS = u'ACGTNURYMKWSBDHVacgtnurymkwsbdhv'
IUPAC_SHAPE_CHARACTERS = u'#_ACGTNURYMKWSBDHVacgtnurymkwsbdhv'

BASE_A = 65
BASE_C = 67
BASE_G = 71
BASE_T = 84
BASE_LOWER_A = 97
BASE_LOWER_C = 99
BASE_LOWER_G = 103
BASE_LOWER_T = 116

BASE_N = 78
BASE_U = 85
BASE_R = 82
BASE_Y = 89
BASE_M = 77
BASE_K = 75
BASE_W = 87
BASE_S = 83
BASE_B = 66
BASE_D = 68
BASE_H = 72
BASE_V = 86
BASE_LOWER_N = 110
BASE_LOWER_U = 117
BASE_LOWER_R = 114
BASE_LOWER_Y = 121
BASE_LOWER_M = 109
BASE_LOWER_K = 107
BASE_LOWER_W = 119
BASE_LOWER_S = 115
BASE_LOWER_B = 98
BASE_LOWER_D = 100
BASE_LOWER_H = 104
BASE_LOWER_V = 118

cdef dict _2bit_from_any = {
    BASE_LOWER_A: 0b00,
    BASE_LOWER_C: 0b01,
    BASE_LOWER_G: 0b10,
    BASE_LOWER_T: 0b11,
    BASE_A: 0b00,
    BASE_C: 0b01,
    BASE_G: 0b10,
    BASE_T: 0b11,
    'A': 0b00,
    'C': 0b01,
    'G': 0b10,
    'T': 0b11,
    'a': 0b00,
    'c': 0b01,
    'g': 0b10,
    't': 0b11,
    0: 0b00,
    1: 0b01,
    2: 0b10,
    3: 0b11
}

cdef dict _4bit_from_any = {
    'A': 1,
    'C': 2,
    'G': 4,
    'T': 8,
    'N': 15,
    'U': 8,
    'R': 5,
    'Y': 10,
    'M': 3,
    'K': 12,
    'W': 9,
    'S': 6,
    'B': 14,
    'D': 13,
    'H': 11,
    'V': 7,
    'a': 1,
    'c': 2,
    'g': 4,
    't': 8,
    'n': 15,
    'u': 8,
    'r': 5,
    'y': 10,
    'm': 3,
    'k': 12,
    'w': 9,
    's': 6,
    'b': 14,
    'd': 13,
    'h': 11,
    'v': 7,

    BASE_LOWER_A: 1,
    BASE_LOWER_C: 2,
    BASE_LOWER_G: 4,
    BASE_LOWER_T: 8,
    BASE_LOWER_N: 15,
    BASE_A: 1,
    BASE_C: 2,
    BASE_G: 4,
    BASE_T: 8,
    BASE_N: 15,

    BASE_U: 8,
    BASE_R: 5,
    BASE_Y: 10,
    BASE_M: 3,
    BASE_K: 12,
    BASE_W: 9,
    BASE_S: 6,
    BASE_B: 14,
    BASE_D: 13,
    BASE_H: 11,
    BASE_V: 7,

    BASE_LOWER_U: 8,
    BASE_LOWER_R: 5,
    BASE_LOWER_Y: 10,
    BASE_LOWER_M: 3,
    BASE_LOWER_K: 12,
    BASE_LOWER_W: 9,
    BASE_LOWER_S: 6,
    BASE_LOWER_B: 14,
    BASE_LOWER_D: 13,
    BASE_LOWER_H: 11,
    BASE_LOWER_V: 7,

    0: 1,
    1: 2,
    2: 4,
    3: 8,
    4: 15,
    5: 8,
    6: 5,
    7: 10,
    8: 3,
    9: 12,
    10: 9,
    11: 6,
    12: 14,
    13: 13,
    14: 11,
    15: 7,

    b'\x00': 1,
    b'\x01': 2,
    b'\x02': 4,
    b'\x03': 8,
    b'\x04': 15,
    b'\x05': 8,
    b'\x06': 5,
    b'\x07': 10,
    b'\x08': 3,
    b'\x09': 12,
    b'\x0A': 9,
    b'\x0B': 6,
    b'\x0C': 14,
    b'\x0D': 13,
    b'\x0E': 11,
    b'\x0F': 7,
}

cdef dict _str_from_2bit = {
    0b00: 'A',
    0b01: 'C',
    0b10: 'G',
    0b11: 'T',
}

cdef dict _byte_from_2bit = {
    0b00: BASE_A,
    0b01: BASE_C,
    0b10: BASE_G,
    0b11: BASE_T,
}

cdef dict _basenumber_from_2bit = {
    0b00: 0,
    0b01: 1,
    0b10: 2,
    0b11: 3,
}

cdef dict _str_from_4bit = {
    0b0000: "_",
    0b0001: "A",
    0b0010: "C",
    0b0011: "M",
    0b0100: "G",
    0b0101: "R",
    0b0110: "S",
    0b0111: "V",
    0b1000: "T",
    0b1001: "W",
    0b1010: "Y",
    0b1011: "H",
    0b1100: "K",
    0b1101: "D",
    0b1110: "B",
    0b1111: "N",
}

cdef dict _byte_from_4bit = {
    0b0000: 0,   #
    0b0001: BASE_A,   # A
    0b0010: BASE_C,   # C
    0b0011: BASE_M,   # M
    0b0100: BASE_G,   # G
    0b0101: BASE_R,   # R
    0b0110: BASE_S,   # S
    0b0111: BASE_V,   # V
    0b1000: BASE_T,   # T
    0b1001: BASE_W,   # W
    0b1010: BASE_Y,  # Y
    0b1011: BASE_H,  # H
    0b1100: BASE_K,  # K
    0b1101: BASE_D,  # D
    0b1110: BASE_B,  # B
    0b1111: BASE_N,  # N
}

cdef dict _basenumber_from_4bit = {
    0b0000: 0,   #
    0b0001: 1,   # A
    0b0010: 2,   # C
    0b0011: 3,   # M
    0b0100: 4,   # G
    0b0101: 5,   # R
    0b0110: 6,   # S
    0b0111: 7,   # V
    0b1000: 8,   # T
    0b1001: 9,   # W
    0b1010: 10,  # Y
    0b1011: 11,  # H
    0b1100: 12,  # K
    0b1101: 13,  # D
    0b1110: 14,  # B
    0b1111: 15,  # N
}

cdef dict _basenumber_from_byte = {
    BASE_LOWER_A: 0,
    BASE_LOWER_C: 1,
    BASE_LOWER_G: 2,
    BASE_LOWER_T: 3,
    BASE_LOWER_N: 4,
    BASE_A: 0,
    BASE_C: 1,
    BASE_G: 2,
    BASE_T: 3,
    BASE_N: 4,

    BASE_U: 5,
    BASE_R: 6,
    BASE_Y: 7,
    BASE_M: 8,
    BASE_K: 9,
    BASE_W: 10,
    BASE_S: 11,
    BASE_B: 12,
    BASE_D: 13,
    BASE_H: 14,
    BASE_V: 15,

    BASE_LOWER_U: 5,
    BASE_LOWER_R: 6,
    BASE_LOWER_Y: 7,
    BASE_LOWER_M: 8,
    BASE_LOWER_K: 9,
    BASE_LOWER_W: 10,
    BASE_LOWER_S: 11,
    BASE_LOWER_B: 12,
    BASE_LOWER_D: 13,
    BASE_LOWER_H: 14,
    BASE_LOWER_V: 15,
}

#  reduced version mapping all non-ACGT characters to N
cdef dict _basenumber_from_byte_suppressed = {
    BASE_LOWER_A: 0,
    BASE_LOWER_C: 1,
    BASE_LOWER_G: 2,
    BASE_LOWER_T: 3,
    BASE_LOWER_N: 4,
    BASE_A: 0,
    BASE_C: 1,
    BASE_G: 2,
    BASE_T: 3,
    BASE_N: 4,

    BASE_U: 4,
    BASE_R: 4,
    BASE_Y: 4,
    BASE_M: 4,
    BASE_K: 4,
    BASE_W: 4,
    BASE_S: 4,
    BASE_B: 4,
    BASE_D: 4,
    BASE_H: 4,
    BASE_V: 4,

    BASE_LOWER_U: 4,
    BASE_LOWER_R: 4,
    BASE_LOWER_Y: 4,
    BASE_LOWER_M: 4,
    BASE_LOWER_K: 4,
    BASE_LOWER_W: 4,
    BASE_LOWER_S: 4,
    BASE_LOWER_B: 4,
    BASE_LOWER_D: 4,
    BASE_LOWER_H: 4,
    BASE_LOWER_V: 4,
}

cdef dict _unicode_from_byte = {
    BASE_LOWER_A: "A",
    BASE_LOWER_C: "C",
    BASE_LOWER_G: "G",
    BASE_LOWER_T: "T",
    BASE_LOWER_N: "N",
    BASE_A: "A",
    BASE_C: "C",
    BASE_G: "G",
    BASE_T: "T",
    BASE_N: "N",

    BASE_U: "U",
    BASE_R: "R",
    BASE_Y: "Y",
    BASE_M: "M",
    BASE_K: "K",
    BASE_W: "W",
    BASE_S: "S",
    BASE_B: "B",
    BASE_D: "D",
    BASE_H: "H",
    BASE_V: "V",

    BASE_LOWER_U: "U",
    BASE_LOWER_R: "R",
    BASE_LOWER_Y: "Y",
    BASE_LOWER_M: "M",
    BASE_LOWER_K: "K",
    BASE_LOWER_W: "W",
    BASE_LOWER_S: "S",
    BASE_LOWER_B: "B",
    BASE_LOWER_D: "D",
    BASE_LOWER_H: "H",
    BASE_LOWER_V: "V",
}

cdef dict _unicode_from_byte_suppressed = {
    BASE_LOWER_A: "A",
    BASE_LOWER_C: "C",
    BASE_LOWER_G: "G",
    BASE_LOWER_T: "T",
    BASE_LOWER_N: "N",
    BASE_A: "A",
    BASE_C: "C",
    BASE_G: "G",
    BASE_T: "T",
    BASE_N: "N",

    BASE_U: "N",
    BASE_R: "N",
    BASE_Y: "N",
    BASE_M: "N",
    BASE_K: "N",
    BASE_W: "N",
    BASE_S: "N",
    BASE_B: "N",
    BASE_D: "N",
    BASE_H: "N",
    BASE_V: "N",

    BASE_LOWER_U: "N",
    BASE_LOWER_R: "N",
    BASE_LOWER_Y: "N",
    BASE_LOWER_M: "N",
    BASE_LOWER_K: "N",
    BASE_LOWER_W: "N",
    BASE_LOWER_S: "N",
    BASE_LOWER_B: "N",
    BASE_LOWER_D: "N",
    BASE_LOWER_H: "N",
    BASE_LOWER_V: "N",
}

cdef dict _basenumber_from_unicode = {
    'A': 0,
    'C': 1,
    'G': 2,
    'T': 3,
    'N': 4,
    'U': 5,
    'R': 6,
    'Y': 7,
    'M': 8,
    'K': 9,
    'W': 10,
    'S': 11,
    'B': 12,
    'D': 13,
    'H': 14,
    'V': 15,
    'a': 0,
    'c': 1,
    'g': 2,
    't': 3,
    'n': 4,
    'u': 5,
    'r': 6,
    'y': 7,
    'm': 8,
    'k': 9,
    'w': 10,
    's': 11,
    'b': 12,
    'd': 13,
    'h': 14,
    'v': 15,
}

cdef dict _basenumber_from_unicode_suppressed = {
    'A': 0,
    'C': 1,
    'G': 2,
    'T': 3,
    'N': 4,
    'U': 4,
    'R': 4,
    'Y': 4,
    'M': 4,
    'K': 4,
    'W': 4,
    'S': 4,
    'B': 4,
    'D': 4,
    'H': 4,
    'V': 4,
    'a': 0,
    'c': 1,
    'g': 2,
    't': 3,
    'n': 4,
    'u': 4,
    'r': 4,
    'y': 4,
    'm': 4,
    'k': 4,
    'w': 4,
    's': 4,
    'b': 4,
    'd': 4,
    'h': 4,
    'v': 4,
}

cdef dict _unicode_from_basenumber = {
    0: 'A',
    1: 'C',
    2: 'G',
    3: 'T',
    4: 'N',
    5: 'U',
    6: 'R',
    7: 'Y',
    8: 'M',
    9: 'K',
    10: 'W',
    11: 'S',
    12: 'B',
    13: 'D',
    14: 'H',
    15: 'V',
}

cdef dict _byte_from_unicode = {
    'A': BASE_A,
    'C': BASE_C,
    'G': BASE_G,
    'T': BASE_T,
    'N': BASE_N,
    'U': BASE_U,
    'R': BASE_R,
    'Y': BASE_Y,
    'M': BASE_M,
    'K': BASE_K,
    'W': BASE_W,
    'S': BASE_S,
    'B': BASE_B,
    'D': BASE_D,
    'H': BASE_H,
    'V': BASE_V,
    'a': BASE_A,
    'c': BASE_C,
    'g': BASE_G,
    't': BASE_T,
    'n': BASE_N,
    'u': BASE_U,
    'r': BASE_R,
    'y': BASE_Y,
    'm': BASE_M,
    'k': BASE_K,
    'w': BASE_W,
    's': BASE_S,
    'b': BASE_B,
    'd': BASE_D,
    'h': BASE_H,
    'v': BASE_V,
}

cdef dict _byte_from_unicode_suppressed = {
    'A': BASE_A,
    'C': BASE_C,
    'G': BASE_G,
    'T': BASE_T,
    'N': BASE_N,
    'U': BASE_N,
    'R': BASE_N,
    'Y': BASE_N,
    'M': BASE_N,
    'K': BASE_N,
    'W': BASE_N,
    'S': BASE_N,
    'B': BASE_N,
    'D': BASE_N,
    'H': BASE_N,
    'V': BASE_N,
    'a': BASE_A,
    'c': BASE_C,
    'g': BASE_G,
    't': BASE_T,
    'n': BASE_N,
    'u': BASE_N,
    'r': BASE_N,
    'y': BASE_N,
    'm': BASE_N,
    'k': BASE_N,
    'w': BASE_N,
    's': BASE_N,
    'b': BASE_N,
    'd': BASE_N,
    'h': BASE_N,
    'v': BASE_N,
}

cdef dict _byte_from_basenumber = {
    0: BASE_A,
    1: BASE_C,
    2: BASE_G,
    3: BASE_T,
    4: BASE_N,
    5: BASE_U,
    6: BASE_R,
    7: BASE_Y,
    8: BASE_M,
    9: BASE_K,
    10: BASE_W,
    11: BASE_S,
    12: BASE_B,
    13: BASE_D,
    14: BASE_H,
    15: BASE_V,
}

cdef dict _iupac_mapping = {
    BASE_N: [BASE_A, BASE_C, BASE_G, BASE_T],
    BASE_U: [BASE_T],
    BASE_R: [BASE_A, BASE_G],
    BASE_Y: [BASE_C, BASE_T],
    BASE_M: [BASE_A, BASE_C],
    BASE_K: [BASE_G, BASE_T],
    BASE_W: [BASE_A, BASE_T],
    BASE_S: [BASE_C, BASE_G],
    BASE_B: [BASE_C, BASE_G, BASE_T],
    BASE_D: [BASE_A, BASE_G, BASE_T],
    BASE_H: [BASE_A, BASE_C, BASE_T],
    BASE_V: [BASE_A, BASE_C, BASE_G],
    BASE_LOWER_N: [BASE_LOWER_A, BASE_LOWER_C, BASE_LOWER_G, BASE_LOWER_T],
    BASE_LOWER_U: [BASE_LOWER_T],
    BASE_LOWER_R: [BASE_LOWER_A, BASE_LOWER_G],
    BASE_LOWER_Y: [BASE_LOWER_C, BASE_LOWER_T],
    BASE_LOWER_M: [BASE_LOWER_A, BASE_LOWER_C],
    BASE_LOWER_K: [BASE_LOWER_G, BASE_LOWER_T],
    BASE_LOWER_W: [BASE_LOWER_A, BASE_LOWER_T],
    BASE_LOWER_S: [BASE_LOWER_C, BASE_LOWER_G],
    BASE_LOWER_B: [BASE_LOWER_C, BASE_LOWER_G, BASE_LOWER_T],
    BASE_LOWER_D: [BASE_LOWER_A, BASE_LOWER_G, BASE_LOWER_T],
    BASE_LOWER_H: [BASE_LOWER_A, BASE_LOWER_C, BASE_LOWER_T],
    BASE_LOWER_V: [BASE_LOWER_A, BASE_LOWER_C, BASE_LOWER_G],
    'N': ['A', 'C', 'G', 'T'],
    'U': ['T'],
    'R': ['A', 'G'],
    'Y': ['C', 'T'],
    'M': ['A', 'C'],
    'K': ['G', 'T'],
    'W': ['A', 'T'],
    'S': ['C', 'G'],
    'B': ['C', 'G', 'T'],
    'D': ['A', 'G', 'T'],
    'H': ['A', 'C', 'T'],
    'V': ['A', 'C', 'G'],
    'n': ['a', 'c', 'g', 't'],
    'u': ['t'],
    'r': ['a', 'g'],
    'y': ['c', 't'],
    'm': ['a', 'c'],
    'k': ['g', 't'],
    'w': ['a', 't'],
    's': ['c', 'g'],
    'b': ['c', 'g', 't'],
    'd': ['a', 'g', 't'],
    'h': ['a', 'c', 't'],
    'v': ['a', 'c', 'g'],
    4: [0, 1, 2, 3],
    5: [3],
    6: [0, 2],
    7: [1, 3],
    8: [0, 1],
    9: [2, 3],
    10: [0, 3],
    11: [1, 2],
    12: [1, 2, 3],
    13: [0, 2, 3],
    14: [0, 1, 3],
    15: [0, 1, 2],
}

cdef dict _complement = {
    BASE_A: BASE_T,
    BASE_T: BASE_A,
    BASE_C: BASE_G,
    BASE_G: BASE_C,
    BASE_N: BASE_N,
    BASE_LOWER_A: BASE_LOWER_T,
    BASE_LOWER_T: BASE_LOWER_A,
    BASE_LOWER_C: BASE_LOWER_G,
    BASE_LOWER_G: BASE_LOWER_C,
    BASE_LOWER_N: BASE_LOWER_N,
    "A": "T",
    "T": "A",
    "C": "G",
    "G": "C",
    "a": "t",
    "t": "a",
    "c": "g",
    "g": "c",
    "N": "N",
    "n": "n",
    0: 3,
    3: 0,
    1: 2,
    2: 1,
    4: 4,
    b'\x00': b'x\03',
    b'\x03': b'x\00',
    b'\x01': b'x\02',
    b'\x02': b'x\01',
    b'\x04': b'x\04',

    # IUPAC Ambiguity codes
    BASE_U: BASE_A,
    BASE_R: BASE_Y,
    BASE_Y: BASE_R,
    BASE_M: BASE_K,
    BASE_K: BASE_M,
    BASE_W: BASE_W,
    BASE_S: BASE_S,
    BASE_B: BASE_V,
    BASE_D: BASE_H,
    BASE_H: BASE_D,
    BASE_V: BASE_B,
    BASE_LOWER_U: BASE_LOWER_A,
    BASE_LOWER_R: BASE_LOWER_Y,
    BASE_LOWER_Y: BASE_LOWER_R,
    BASE_LOWER_M: BASE_LOWER_K,
    BASE_LOWER_K: BASE_LOWER_M,
    BASE_LOWER_W: BASE_LOWER_W,
    BASE_LOWER_S: BASE_LOWER_S,
    BASE_LOWER_B: BASE_LOWER_V,
    BASE_LOWER_D: BASE_LOWER_H,
    BASE_LOWER_H: BASE_LOWER_D,
    BASE_LOWER_V: BASE_LOWER_B,
    "U": "A",
    "R": "Y",
    "Y": "R",
    "M": "K",
    "K": "M",
    "W": "W",
    "S": "S",
    "B": "V",
    "D": "H",
    "H": "D",
    "V": "B",
    "u": "a",
    "r": "y",
    "y": "r",
    "m": "k",
    "k": "m",
    "w": "w",
    "s": "s",
    "b": "v",
    "d": "h",
    "h": "d",
    "v": "b",
    5: 0,
    6: 7,
    7: 6,
    8: 9,
    9: 8,
    10: 10,
    11: 11,
    12: 15,
    13: 14,
    14: 13,
    15: 12,
    b'\x05': b'\x00',
    b'\x06': b'\x07',
    b'\x07': b'\x06',
    b'\x08': b'\x09',
    b'\x09': b'\x08',
    b'\x10': b'\x10',
    b'\x11': b'\x11',
    b'\x12': b'\x15',
    b'\x13': b'\x14',
    b'\x14': b'\x13',
    b'\x15': b'\x12',
}

cdef dict _iupac_complement = {
    0b0001: 0b1000,  # A ←→ T
    0b0010: 0b0100,  # C ←→ G
    0b0100: 0b0010,  # G ←→ C
    0b1000: 0b0001,  # T ←→ A
    0b1111: 0b1111,  # N ←→ N
    #0b0000: 0b0001,  # U ←→ A  # reverse is A ←→ T
    0b0101: 0b1010,  # R ←→ Y
    0b1010: 0b0101,  # Y ←→ R
    0b0011: 0b1100,  # M ←→ K
    0b1100: 0b0011,  # K ←→ M
    0b1001: 0b1001,  # W ←→ W
    0b0110: 0b0110,  # S ←→ S
    0b1110: 0b0111,  # B ←→ V
    0b0111: 0b1110,  # V ←→ B
    0b1101: 0b1011,  # D ←→ H
    0b1011: 0b1101,  # H ←→ D
}

cdef dict linetype_as_str = {
    START: "start",
    NAME: "name",
    SEQUENCE: "sequence",
    PLUS: "plus",
    QUALITY_VALUES: "quality values",
}

cdef set valid_dtypes = {
    str,
    bytes,
    bytearray,
    basenumbers,
}

cdef class IUPACRandomReplacementDict(dict):
    @cython.embedsignature(False)
    def __init__(self, *args, **kwargs):
        """__init__(args, kwargs)

        Dictionary subclass, that returns the 2bit representation for a IUPAC character.
        If a IUPAC ambiguity code is encountered, a base satisfying the code
        is (uniformly) randomly chosen. 
        
        Example:
        
            >>> irrd = dinopy.definitions.IUPACRandomReplacementDict()
            >>> irrd["A"]
            0
            >>> irrd["C"]
            1
            >>> irrd["R"]   # R = A or G 
            0
            >>> irrd["R"]   # R = A or G 
            2
            >>> irrd["N"]   # N = A or C or G or T
            3
            >>> irrd["N"]   # N = A or C or G or T
            1
            >>> irrd["N"]   # N = A or C or G or T
            2
            >>> irrd["N"]   # N = A or C or G or T
            1

        """
        self.__dict__ = {}
        super(IUPACRandomReplacementDict, self).__init__(*args, **kwargs)
        # add in all non-ambiguous translations
        self.__dict__.update(_2bit_from_any)

    def __setitem__(self, key, item):
        self.__dict__[key] = item

    def __getitem__(self, key):
        """Return a 2bit representation for key.

        Arguments:
            key (str, bytes or int): A IUPAC codepoint.

        Returns:
            A base satisfying the entered IUPAC codepoint.
        """
        # check if the key is an ambiguous IUPAC symbol
        if key in _iupac_mapping:
            # uniformly randomly choose a base from all possible
            # bases for the code
            key = choice(_iupac_mapping[key])
        return self.__dict__[key]

    def __repr__(self):
        return repr(self.__dict__)

    def __len__(self):
        return 4  # A, C, G, T, every other iupac char gets mapped to one of those

    def __delitem__(self, key):
        del self.__dict__[key]

    def keys(self):
        return self.__dict__.keys() | _iupac_mapping.keys()

    def values(self):
        return self.__dict__.values()

    def __cmp__(self, dict):
        raise NotImplementedError

    def __contains__(self, item):
        return item in self.__dict__ or item in _iupac_mapping

    def add(self, key, value):
        self.__dict__[key] = value

    def __iter__(self):
        return chain(iter(self.__dict__), iter(_iupac_mapping))

    def __call__(self):
        return self.__dict__

cpdef IUPACRandomReplacementDict _2bit_from_any_with_iupac_replacement = IUPACRandomReplacementDict()
