# -*- coding: utf-8 -*-
import sys
import math
from collections import Counter
from .exceptions import InvalidLinetypeError

cimport cython

cdef class FastqReader:
    @cython.embedsignature(False)
    def __init__(self, source):
        """__init__(source)
        Reader for FASTQ files.

        Arguments:
            source (str, file, stdin, or list): FASTQ input source, can be a
                path .fastq or fastq.gz file (as str), an open file handle,
                the stdin stream (sys.stdin) or a list of bytes.

        Works with gzipped files which are identified by the usual '.gz' suffix.

        The data type of the sequence can be specified as one of bytes, bytearray,
        str, or basenumbers. See :ref:`dtype` for more information.

        The name and plus lines, as well as the quality values are returned as
        bytes (without @ or +).

        The specified source from which the FASTQ file is read
        can either be a filepath to a .fastq or fastq.gz file
        (zipped files are identified by the .gz suffix) or sys.stdin
        or a file/IOBase object.

        Supports two iterators, for different level of analysis:

        - :meth:`lines`: Return an iterator over all lines in the FASTQ file.
          Lines are classified and returned as a named tuple ``(type, value)``
          where ``type`` can be 'name', 'sequence', 'plus', 'quality values'
          and value is of type `bytes` for 'name', 'plus' and 'quality values'
          and `dtype` for 'sequence' (Default: bytes).

        - :meth:`reads`: Return an iterator over all reads in the FASTQ file.
          Reads are returned as a named tuple containing:

            - sequence (dtype): Read sequence (always).
            - name (bytes): Name line (only if `names=True`).
            - quality (bytes): Quality values (only if `quality_values=True`).

          or just as a sequence, if both the `names` and the `quality_values`
          parameter are set to `False`.

        Example:
            Iterate over all reads in the file *path/to/fastq_file.fastq* and pass
            all reads that match a certain condition (depending on the read name)
            to a computation function::

                import dinopy
                fqr = dinopy.FastqReader("path/to/fastq_file.fastq")
                for seq, name in fqr.reads():
                    if some_condition(name):
                        computation(seq)

        """
        self._last_state = START
        self._quality_tally = Counter()
        self._valid_states_before_name = (START, SEQUENCE, QUALITY_VALUES)
        self._quality_tally_ready = False
        self._source = source

    def lines(self, type dtype=bytes):
        """Returns an iterator over all lines in the FASTQ file.

        Arguments:
            dtype (type): Desired type for the sequences. (see :ref:`dtype <dtype>`; Default: bytes)
                Note that name, plus and quality values lines are always returned as bytes.

        Yields:
            (str, bytes or dtype)-tuples: An iterator over all lines in the FASTQ file.
            Lines are classified and returned as a named tuple containing
            type and value of the line, where type can be:

                1. 'name'
                2. 'sequence'
                3. 'plus'
                4. 'quality values'

            and value contains the content of the respective line.

        Raises:
            FileNotFoundError: If the FASTQ source is a filepath that does not
                point to a valid input file.

            ValueError: If the input source does not specify a valid source type.
        """
        cdef:
            bytes byte_line
            int line_type
            object line_value
        with InputOpener(self._source) as input_iterable:
            for byte_line in input_iterable:
                line_type, line_value = self._classify_line(byte_line, dtype)
                yield FastqLine(linetype_as_str[line_type], line_value)

    def reads(
            self,
            bool names=True,
            bool quality_values=True,
            bool quality_tally=False,
            type dtype=bytes,
    ):
        """Returns an iterator over all reads in the file.

        Arguments:
            names (bool): Return the name line with each read. (Default: True)

            quality_values (bool): Return the quality values with each read. (Default: True)

            quality_tally (bool): Tally up quality values of the whole file. (Default: False)

            dtype (type): Desired type for the sequences. (see :ref:`dtype <dtype>`; Default: bytes)
                Note that name, plus and quality values lines are always returned as bytes.

        Yields:
            named tuple or dtype: An iterator over all reads in the FASTQ file.
            The type of the items relies on the input parameter. If both `names`
            and `quality_values` are set to `False` only the sequence will be
            yielded encoded with the givend dtype.
            Otherwise a named tuple will be yielded that contains the following
            entries:

            +-------+----------------+-------------------------------------------------------------------+
            | names | quality_values | return type                                                       |
            +=======+================+===================================================================+
            | False | False          | sequence                                                          |
            +-------+----------------+-------------------------------------------------------------------+
            | True  | False          | NamedTuple(sequence, name)                                        |
            +-------+----------------+-------------------------------------------------------------------+
            | False | True           | NamedTuple(sequence, quality values)                              |
            +-------+----------------+-------------------------------------------------------------------+
            | True  | True           | NamedTuple(sequence, name, quality values)                        |
            +-------+----------------+-------------------------------------------------------------------+

            The type of `sequence` depends on the dtype parameter,
            `name` and `quality_values` are always returned as bytes.

        Raises:
            FileNotFoundError: If the source is an invalid filepath.

        """
        cdef:
            bytes byte_line, name
            int line_type
            object input_iterable
            object sequence

        if quality_tally:
            self._quality_tally_ready = True

        with InputOpener(self._source) as input_iterable:
            for byte_line in input_iterable:
                line_type, line_value = self._classify_line(byte_line, dtype)

                # Only keep name, sequence (and quality values).
                # Update quality tally if quality_tally has been set
                if line_type == NAME:
                    name = line_value
                if line_type == SEQUENCE:
                    if quality_values:
                        sequence = line_value
                    else:
                        if names:
                            yield FastqReadWithoutQV(line_value, name)
                        else:
                            yield line_value
                if line_type == QUALITY_VALUES:
                    if quality_tally:
                        self._quality_tally.update(line_value)
                    if quality_values:
                        if names:
                            yield FastqRead(sequence, name, line_value)
                        else:
                            yield FastqReadWithoutName(sequence, line_value)

    @cython.wraparound(False)
    cpdef tuple _classify_line(self, bytes line, type dtype):
        """Classify line and trim and encode it accordingly.

        Check if the line is `name`, `sequence`, `plus`, or `quality values`
        and return the line trimmed of special characters. The sequence line
        is encoded in the specified dtype. The other ones are returned as
        bytes.

        Remove trailing '\\n' and leading '@'/'+' before name/plus lines.

        Arguments:
            line (bytes): The line to classify
            dtype (type): Desired type for the sequences. (see :ref:`dtype <dtype>`; Default: bytes)
                Note that name, plus and quality values lines are always returned as bytes.

        Returns:
            tuple (int, dtype or bytes): A tuple containing the linetype encoded
                as int (START = 0, NAME = 1, SEQUENCE = 2, PLUS = 3, QUALITY_VALUES = 4,
                see FASTQ_PARSER_STATE in definitionx.pxd for deatils.)

        Raises:
            InvalidLinetypeError: If the last state was anything but 0, 1, 2, 3, 4
                i.e. START, NAME, SEQUENCE, PLUS, QUALITY_VALUES.
        """
        cdef:
            int line_type
            int line_length = len(line)
            char head = line[0]

        # Set index to clip off newline at the end of the line.
        line = line.rstrip()

        # If line begins with '@' and the last line was either
        # a read or quality values classify this line as 'name'
        if head == AT_BYTE and self._last_state in self._valid_states_before_name:
            self._last_state = NAME
            return NAME, line[1:]

        # If the last line was a read and this line starts with '+'
        # this line is plus (with optional name)
        elif head == PLUS_BYTE and self._last_state == SEQUENCE:
            self._last_state = PLUS
            return PLUS, line[1:]

        # If the last line was the name, this line is definately a read.
        # Encode the sequence in the given dtype.
        elif self._last_state == NAME:
            self._last_state = SEQUENCE
            return SEQUENCE, _change_dtype_bytes(line, dtype)

        # If the last line was 'plus' this line contains the
        # quality values for the last read
        elif self._last_state == PLUS:
            self._last_state = QUALITY_VALUES
            return QUALITY_VALUES, line

        else:  # if this happens, we have got a problem
            state_as_str = {
                0: "Start",
                1: "Name",
                2: "Sequence",
                3: "Plus",
                4: "Quality Values",
                }
            next_possible_linetype = {
                0: ["Name"], # after start, only name is valid
                1: ["Sequence"], # after name line, only sequence is valid
                2: ["Name", "Plus"], # after a sequence a new name line or a plus line are valid
                3: ["Quality Values"], # after a plus line only quality values are valid
                4: ["Name"], # after quality values only a name line is valid
                }
            
            last_state = self._last_state
            if last_state not in range(5):
                raise InvalidLinetypeError("This should never happen. Linetype has to be from {{0, 1, 2, 3, 4}}, not {}".format(last_state))
            else:
                expected_state = next_possible_linetype[last_state]
                raise InvalidLinetypeError(
                    "Error parsing FASTQ-file.\nlast state was: {}\nexpected linetype(s): {}\nfound line: {}".format(
                        state_as_str[last_state], " or ".join(expected_state), line
                        )
                    )

    cpdef int _ordering(self, str key):
        """Map a str (containing the name of a quality format) to an int.

        Helper function to sort quality value formats.
        This is neccesary, because for some reason a lambda function
        is not supported in guess_quality_format.

        Arguments:
            key (str): Name of a quality value format.
        """
        cdef dict order = {
            "Sanger": 1,
            "Illumina 1.8+": 0,
            "Solexa, Illumina <=1.2+": 2,
            "Illumina 1.3+": 3,
            "Illumina 1.5+": 4,
        }
        return order[key]

    cpdef tuple guess_quality_format(self, int max_reads=10000):
        """Guess which format was used to encode the quality values.

        The quality values are defined `as described here <https://en.wikipedia.org/w/index.php?title=FASTQ_format&oldid=651348382>`_.

        Arguments:
            max_lines(int): Number of reads after which the scan is terminated.
                (Default: 10000)

        Raises:
            ValueError: for quality values lower than 33 or bigger than 104.
                These values are not part of any standard quality value format.

        Returns:
            tuple: A tuple containing the most probable format for the quality values
            as a string and a list of all possible formats fo the observed
            quality values.

            Possible formats are:

                - 'Sanger'                   (ASCII 33-73)  PHRED   0-40
                - 'Solexa, Illumina <=1.2'   (ASCII 59-104) Solexa -5-40
                - 'Illumina 1.3+'            (ASCII 64-104) PHRED   0-40
                - 'Illumina 1.5+'            (ASCII 66-104) PHRED   3-40
                - 'Illumina 1.8+'            (ASCII 33-74)  PHRED   0-41

            If several formats could explain the observed values, the most
            conservative guess is returned.
        """
        cdef:
            object tally = Counter()
            object input_iterable
            bytes byte_line
            bytes line_value
            int line_type
            int max_lines = max_reads * 4
        # iterate the first max_lines of the file and tally up quality values
        with InputOpener(self._source) as input_iterable:
            for _, byte_line in zip(range(max_lines), input_iterable):
                line_type, line_value = self._classify_line(byte_line, bytes)
                if line_type == QUALITY_VALUES:
                    tally.update(line_value)

        cdef:
            int lowest, highest
            set possible_formats_low, possible_formats_high
        # compute highest and lowest value found in the file
        lowest, *_, highest = sorted(tally.keys())

        # collect possible formats for lowest found value
        if 33 <= lowest <= 58:
            possible_formats_low = {"Sanger", "Illumina 1.8+"}
        elif 59 <= lowest <= 63:
            possible_formats_low = {"Sanger", "Illumina 1.8+", "Solexa, Illumina <=1.2+"}
        elif 64 <= lowest <= 65:
            possible_formats_low = {"Sanger", "Illumina 1.8+", "Solexa, Illumina <=1.2+", "Illumina 1.3+"}
        elif 66 <= lowest:
            possible_formats_low = {"Sanger", "Illumina 1.8+", "Solexa, Illumina <=1.2+", "Illumina 1.3+",
                                    "Illumina 1.5+"}
        else:
            raise ValueError(
                "Invalid quality value (space or unprintable character) with ASCII value '{}' detected,".format(lowest))
        # collect possible formats for highest found value
        if 104 >= highest >= 75:
            possible_formats_high = {"Solexa, Illumina <=1.2+", "Illumina 1.3+", "Illumina 1.5+"}
        elif 74 == highest:
            possible_formats_high = {"Illumina 1.8+", "Solexa, Illumina <=1.2+", "Illumina 1.3+", "Illumina 1.5+"}
        elif 73 >= highest:
            possible_formats_high = {"Sanger", "Illumina 1.8+", "Solexa, Illumina <=1.2+", "Illumina 1.3+",
                                     "Illumina 1.5+"}
        else:
            raise ValueError("Invalid quality value (beyond 'h') with ASCII value '{}' detected,".format(lowest))
        # compute all possible formats by intersecting the two sets
        # of possible formats
        cdef list possible_formats = list(possible_formats_high & possible_formats_low)
        # return the least restrictive format and all possible formats for
        # the observed values
        return min(possible_formats, key=self._ordering), possible_formats

    property quality_tally:
        """Return a tally of the quality values, if there is any.

        Returns:
            Counter or None: A collections.Counter containing all encountered quality values.
            If no quality tally has been created, return None.
        """
        def __get__(self):
            if self._quality_tally_ready:
                return self._quality_tally
            else:
                return None

    cpdef print_quality_tally(self, file=sys.stdout):
        """Print a crude ASCII histogram of the quality values if there are any.

        Note:
            To use this the reads method has to be called with the quality_tally parameter
            set to True. Creating a tally by using the lines method is not yet supported.

        Arguments:
            file (filelike): Where the histogram will be printed to. (Default: sys.stdout)

        Raises:
            ValueError: If no data for a quality tally has been found. This can either be due
            to the quality_tally parameter of the reads method was set to False (i.e. no tally
            was created) or because no file has been parsed yet.
        """
        if not self._quality_tally_ready:
            raise ValueError("Quality values are not ready! The quality tally is only \
                  processed if reads has been called with the quality_tally \
                  parameter set to True.")
        else:
            total = sum(self._quality_tally.values())  # total number of values counted
            last_zero = False
            for value, count in sorted(self._quality_tally.items()):
                print(
                    "i:{:>3} ({}) {:>10} |{:<70}|".format(
                        value,
                        chr(value),
                        count,
                        (math.floor((count / total) * 70)) * "X"),
                    file=file,
                )
            print("\n", file=file)  # print empty lines to better separate subsequently printed tallies
