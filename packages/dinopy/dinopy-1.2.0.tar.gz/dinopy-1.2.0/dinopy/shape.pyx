# -*- coding: utf-8 -*-
import numpy as np
from collections import Iterable
from .exceptions import InvalidStartingCharacterError, TooManyCharactersError, UnknownCharactersError

cimport cython

cdef class Shape:
    @cython.embedsignature(False)
    def __init__(self, object shape):
        """__init__(object shape)
        The Shape class represents a shape that can be applied to qgrams.

        Arguments:
            shape(object): Any descriptor for a shape. For a list of possible descriptors, see below.

        Representations that can be parsed include:
    
            * Strings consisting of '#' (*care*) and '_'/'-' (*don't care*) characters, e.g. ``"#__##"`` or ``"#--##"``
            * A single integer: for example, specifying ``5`` is equivalent to ``"#####"``
            * Any iterable which consists of exactly two different items,
              e.g. ``["care", "don't care", "care", "care"]`` is the same as ``"#_##"``.

              .. note::

                As valid shapes must always start with a *care* character, we assume that the first item encountered
                is indeed a care character. This can lead to counterintuitive behaviour, i.e. ``["no", "yes", "yes", "no"]``
                is equivalent to ``"#__#"``.
            * Any iterable which consists of exactly one unique item,
              e.g. ``[1, 1, 1, 1]`` is the same as ``"####"``. Note that there's no special case for bitlike lists,
              i.e. ``[0, 0, 0, 0]`` is the same as ``"####"``!

        Upon creation, some information about the shape is gathered:
    
            * shape length: can be accessed via len(shape) or the shape.length attribute.
            * solidity: a shape is called *solid* iff it solely consists of *care* characters. Can be checked for via :meth:`dinopy.shape.is_solid`.
    
        In addition to the above information, we also generate four different shape
        representations, because they may prove useful for certain applications.
        They can be accessed by:
    
            * :code:`shape.bool_shape`: A boolean numpy array with ``True`` (*care*)
              and ``False`` (*don't care*), e.g. ``"#_##"`` → ``array([True, False, True, True], dtype=bool)``
            * :code:`shape.index_shape_care`: A list containing only those indices which correspond to
              a *care* character, e.g. ``"#_##"`` → ``[0, 2, 3]``.
              This is especially useful for shapes with lots of *don't cares* (or *gaps*).
            * :code:`shape.index_shape_dont_care`: A list containing only those indices which correspond to
              a *don't care* character, e.g. ``"#_##"`` → ``[1]``.
              This is especially useful for shapes with lots of *cares*.

        Attributes:
            bool_shape (np.ndarray): Numpy array of booleans containing the shape encoded as True (care position) and False (don't-care position).
            index_shape_care (list, readonly): List containing the indices of all care positions.
            index_shape_dont_care (list, readonly): List containing the indices of all don't care positions.
            length (int, readonly): Total length of the shape (care + don't-care positions).
            num_care (int, readonly): Number of care positions in the shape.
            num_dont_care (int, readonly): Number of don't care positions in the shape.
        """
        self.bool_shape = self._parse_bool_shape(shape)
        self.index_shape_care = []
        self.index_shape_dont_care = []
        self.representation = ""
        self.solid = True
        self.length = len(self.bool_shape)
        self.num_care = 0
        self.num_dont_care = 0
        for index, item in enumerate(self.bool_shape):
            self.representation += "#" if item else "_"
            if item:
                self.index_shape_care.append(index)
                self.num_care += 1
            else:
                self.solid = False
                self.index_shape_dont_care.append(index)
                self.num_dont_care += 1
        if self.num_care + self.num_dont_care != self.length:
            raise ValueError(
                "The number of care positions and don't care positions don't sum up to the total length. {} + {} ≠ {}".format(
                    self.num_care, self.num_dont_care, self.length))

    def __str__(self):
        return self.representation

    def __repr__(self):
        return self.bool_shape.__repr__()

    def __len__(self):
        return self.length

    def __iter__(self):
        return self.bool_shape.__iter__()

    def __getitem__(self, key):
        return self.bool_shape[key]

    cpdef bool is_solid(self):
        """Return True if the Shape does not have any don't care positions."""
        return self.solid

    @cython.wraparound(False)
    cdef np.ndarray _parse_bool_shape(self, object shp):
        """Tries parsing the given shape object to a boolean shape array. Raises ValueError when parsing fails.
        If the shape already is of type `numpy.ndarray`, we assume that it is a valid boolean shape array without
        any validation.

        Arguments:
            shape: may either be a string solely consisting of the usual care '#' and don't care '_' characters,
                or any other iterable (and indexable) in which exactly two different symbols occur.
                In the latter case, the first item (i.e. `shape[0]`) is considered the care symbol,
                and the only other item is considered as don't care symbol.
                If `shape` is of type `numpy.ndarray`, we simply return `shape`.

                Note that no matter which type shape is of, its first and last symbols must always be care symbols.

        Returns:
            a `numpy.ndarray` of type `numpy.uint8` consisting solely of `0` and `1`.
            This boolean shape is used in all `apply_shape` variants.

        Raises:
            ValueError: If the shape could not be parsed, because it isn't iterable.
        """
        cdef int shp_length
        cdef char index
        cdef set chars
        if isinstance(shp, int):
            shp_length = shp
        else:
            shp_length = len(shp)
        cdef np.ndarray bshape = np.empty(shp_length, dtype=np.bool)

        if isinstance(shp, Shape):
            return shp.bool_shape
        if isinstance(shp, np.ndarray):
            if shp.dtype == np.bool:
                return shp
            else:
                return np.array(list(shp), dtype=np.bool)
        if isinstance(shp, int):
            shp = "#" * shp
        if isinstance(shp, Iterable):
            if isinstance(shp, str) or isinstance(shp, unicode):
                try:
                    self._bshape_from_str(bshape, shp)
                except UnknownCharactersError:
                    self._bshape_from_list(bshape, list(shp))
            elif isinstance(shp, bytes):
                try:
                    self._bshape_from_bytes(bshape, shp)
                except TooManyCharactersError:
                    self._bshape_from_list(bshape, list(shp))
            else:  # e.g. ['yes', 'no', 'no', 'yes'] → [1, 0, 0, 1]
                self._bshape_from_list(bshape, shp)
        else:
            raise ValueError(
                "Cannot parse shape {0}: Unsupported type {1}. Shape has to be iterable.".format(shp, type(shp)))
        return bshape

    cdef _bshape_from_str(self, np.ndarray bshape, str shape):
        """Create a bshape from a string of # (care) and  _ or - (don't care)"""
        if set(shape) not in ({"#"}, {"#", "_"}, {"#", "-"}):
            raise UnknownCharactersError("qgram-shapes must consist solely of '#' and '_'/'-' characters. " + shape)
        if shape[0] != u'#' or shape[len(shape) - 1] != u'#':
            raise InvalidStartingCharacterError(
                "qgram-shapes must not start or end with '_' / '-'. Choose a smaller shape instead. " + shape)
        for index, item in enumerate(shape):
            bshape[index] = item == '#'

    cdef _bshape_from_bytes(self, np.ndarray bshape, bytes shape):
        """Create a bshape from a bytes string of # (care) and  _ or - (don't care)"""
        if set(shape) not in ({b"#"}, {b"#", b"_"}, {b"#", b"-"}):
            raise TooManyCharactersError("qgram-shapes must consist solely of '#' and '_'/'-' characters. " + shape)
        if shape[0] != b'#' or shape[len(shape) - 1] != b'#':
            raise InvalidStartingCharacterError(
                "qgram-shapes must not start or end with b'_'. Choose a smaller shape instead. " + shape)
        for index, item in enumerate(shape):
            bshape[index] = item == b'#'

    cdef _bshape_from_list(self, np.ndarray bshape, list items):
        """Create a bshape from any list of two different items."""
        care = items[0]  # Every shape has to start with a care item.
        if items[len(items) - 1] != care:
            raise InvalidStartingCharacterError(
                "Any given shape is only valid if it starts and ends with the same care character. " + str(items))
        chars = set(items)
        if len(chars) == 2:
            for index, item in enumerate(items):
                bshape[index] = item == care
        elif len(chars) == 1:
            bshape = np.ones(len(items), dtype=np.bool)
        else:
            raise TooManyCharactersError("More than two different characters ({0}) used in shape '{1}'".format(chars, items))

