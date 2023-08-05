# -*- coding: utf-8 -*-
import os
import sys
from math import ceil
from .fai_io import read_fai, write_chromosomes_as_fai, fai_to_chromosome_info
from os import linesep

cimport cython

# [1] Oh, come on! Who needs bytearrays? (Brandon Rhodes) https://www.youtube.com/watch?v=z9Hmys8ojno

cdef class FastaReader:
    @cython.embedsignature(False)
    def __init__(self, source, write_fai=False):
        """__init__(source, write_fai=False)
        Reader for any FASTA-like input.

        Arguments:
            source (str, file, stdin, or list): FASTA input source, can be a
                path to a .fa / .fasta or .fa.gz / fasta.gz file (as str), an open file handle,
                the stdin stream (sys.stdin) or a list of bytes.

            write_fai (bool): If `True`, a fai (FASTA annotation information) file will be generated and stored
                at ``source + '.fai'`` / ``source.name + '.fai'`` automatically.
                fai files can speed up random access of FASTA file contents.
                Default: `False`.

        Works with zipped files, which are identified by '.gz' suffix.

        Supports different iterators, for different level of analysis:

            - :meth:`entries`: Yield all entries of the file and provide information
              about length and position in the genome for all entries.
            - :meth:`genome`: Concatenates and returns all data (i.e. all lines except name-lines)
              as a single sequence. Also return an annotation containing chromosome boundaries and
              lengths.
            - :meth:`reads`: Interpret the entries of the file as reads and yield
              them either as FastaRead named tuples or only as sequences.
            - :meth:`chromosomes`: Interpret the entries of the FASTA file as
              chromosomes. If only a subset of chromosomes is to be analyzed,
              those can be specified via the selected_chromosomes parameter.
              Chromosomes that have not been selected will be skipped.
            - :meth:`lines`: Yield all lines of the file without interpretation.

        Also supports array like access if a fai file is present::

            far = FastaReader("testgenome.fasta")  # or supply write_fai=True to create a fai file implicitly
            print(list(far['chromosome_II']))  # prints the entry with name 'chromosome_II'
            print(list(far[1]))  # same as the above iff 'chromosome_II' really is the second chromosome in the file

        You can even specify a list of items (in mixed mode!): :code:`fparser[[0, 'chromosome_III']]` will
        return the first chromosome in the file and the chromosome named 'chromosome_III'. Note the double brackets:
        this is because we actually expect a *list* of names/indices.

        Even better: random access using bracket style indexing is supported aswell! Just supply a tuple consisting
        of chromosome_name, start-index and end-index, i.e. :code:`fparser[('chromosome_I', 2, 36)]`.
        Since we can handle lists, you can also supply multiple tuples::

            sequences = fparser[[('chromosome_I', 2, 36), ('chromosome_II', 24, 26)]]

        Note:
            A FASTA annotation file (fai-file) can speed up the reading of a
            FASTA file. If a corresponding fai-file with the same filename /
            path and the suffix .fai is found it is automatically used.
            If not, such a file is created iff ``write_fai=True``.

        Note:
            If you use the array-like (bracket-style) access, dtype is fixed to `bytes`. If you wish to use a different
            dtype for the sequence, use :meth:`chromosomes` or :meth:`random_access` with the appropriate dtype
            instead (or use one of the conversion methods afterwards)

        Warning:
            This feature is still experimental.
        """
        self._source = source
        # check if an annotation file for the FASTA file can be found.
        try:
            if os.path.exists(str(source) + ".fai"):
                self._fai_path = str(source) + ".fai"
        except TypeError:
            if os.path.exists(str(source.name) + ".fai"):
                self._fai_path = str(source.name) + ".fai"
        if self._fai_path:
            self._fai = self._read_annotation_file()
        else:
            if write_fai:
                if os.path.exists(str(source)):
                    self._fai_path = str(source) + ".fai"
                elif os.path.exists(str(source.name) + ".fai"):
                    self._fai_path = str(source.name) + ".fai"
                line_bytes = self._guess_line_length()
                write_chromosomes_as_fai(self._fai_path, list(self._gather_chromosome_info()),
                                         line_length=line_bytes - 1)
                self._fai = self._read_annotation_file()

    def _read_annotation_file(self):
        """Open a fai file using the :func:`fai_io.read_fai` function.

        Looks for a file at the same path with an additional .fai suffix.

        Raises:
            FileNotFoundError: If the fai file could not be opened.

        Warning:
            This is not yet used anywhere in the code.
        """
        if self._fai_path:
            return read_fai(self._fai_path)
        else:
            raise FileNotFoundError("No such file: {0}".format(self._fai_path))

    def _guess_line_length(self):
        with InputOpener(self._source) as reader:
            for line in reader:
                if line[0] == GREATER_BYTE:
                    continue
                else:
                    return len(line)

    def _gather_chromosome_info(self):
        cdef:
            int line_length
            long offset = 0, start = 0
            list entry_info, entry_lengths, entry_intervals
            bytes line, name
            bint entry = False

        with InputOpener(self._source) as reader:
            for line in reader:
                line = line.rstrip()
                line_length = len(line)
                if line_length > 0:
                    head = line[0]
                else:
                    head = 0
                if head == GREATER_BYTE:
                    if entry:
                        yield (name.decode(), offset - start, (start, offset))
                    name = line[1:]
                    entry = False
                    start = offset
                else:
                    if line:
                        entry = True
                    offset += line_length
            yield (name.decode(), offset - start, (start, offset))

    def __getitem__(self, key):
        if not self._fai:
            raise ValueError("No fai file available → no 'random' access possible")
        if isinstance(key, (str, bytes)):  # select by chromosome name
            selection = None
            for entry in self._fai:
                chr_name, _, _, _, _ = entry
                if key in (chr_name, chr_name.decode()):
                    selection = entry
            return self.chromosomes(selected_chromosomes=selection)
        elif isinstance(key, int):  # select by chromosome number, i.e. key-th fai entry
            selection = self._fai[key]
            return self.chromosomes(selected_chromosomes=selection)
        elif isinstance(key, tuple):
            chromosome, start, end = key
            return self.random_access(chromosome, start, end)
        elif isinstance(key, list):
            return [self.__getitem__(k) for k in key]

    cpdef random_access(self, object selected_chromosome, int start, int end, dtype=bytes):
        """Provides random access of fasta files if a fai file is available.

        Arguments:
            selected_chromosome (str, bytes, int): either `str` or `bytes` giving a chromosome's name or an `int`
             referring to the number of the chromosome in the file.

            start (int): start-index in the chromosome (i.e. relative!). Inclusive.
            end (int): end-index in the chromosome (i.e. relative!). Exclusive.
            dtype (type): Desired type for the sequence(s) (see :ref:`dtype <dtype>`, default: bytes).

        Returns:
            the subsequence of `selected_chromosome` from `start` to `end` (with type `dtype`).

        Examples:
            Access a subsequence of length 33 of 'chromosome_II' starting from the third base:
            ::

                far = dinopy.FastaReader(filepath)
                far.random_access('chromosome_II', 2, 36)
        """
        cdef:
            list fai_entry
            int length
            bytes bytes_read

        if not self._fai:
            raise ValueError("No fai file available for random access. Please do either of the following:\n"
                             " - Create the FastaReader object with the optional argument `write_fai=True`"
                             " - Create a fai file using samtools: `samtools faidx foo.fasta`\n"
                             " - Create a fai file using dinopy.fai_io.write_chromosomes_as_fai manually.")

        if isinstance(selected_chromosome, int):
            fai_entry = self._fai[selected_chromosome]
        elif isinstance(selected_chromosome, (str, bytes)):
            chrom = selected_chromosome.encode() if isinstance(selected_chromosome, str) else selected_chromosome
            for entry in self._fai:
                if entry[0] == chrom:
                    fai_entry = entry
                    break

        fname, flength, fstart, fline_length, fline_bytes = fai_entry
        if start >= flength:
            raise IndexError("Index out of bounds: {} ≥ {}".format(str(start), str(flength)))
        if start < 0:
            raise IndexError("Index out of bounds: {} < 0".format(str(start)))
        if end >= flength:
            raise IndexError("Index out of bounds: {} ≥ {}".format(str(end), str(flength)))
        if end <= start:
            raise IndexError("End-index {} ≤ start-index {}".format(str(end), str(start)))
        length = end - start - 1  # inclusive start index, exclusive end index
        with InputOpener(self._source) as reader:
            reader.seek(fstart + start)
            bytes_read = reader.read(int(ceil((length / fline_length) * fline_bytes)))  # watch out for line-break bytes
            bytes_read = bytes_read.replace(b'\n', b'')  # careful: assuming '\n', never '\r\n'!
        return _change_dtype_bytes(bytes_read, dtype=dtype)

    def entries(self, dtype=bytes):
        """Iterate over each *entry* in a FASTA file.

        An entry is the combination of a name and a sequence.
        Typically entries represent chromosomes, but sometimes reads get stored in FASTA format, too.
        Please note that there are special methods to work with reads and
        chromosomes (:meth:`chromosomes` and :meth:`reads`), which cater to the specific needs of either
        format and allow for more intuitive code.

        Arguments:
            dtype (type): Desired type for the sequence(s) (see :ref:`dtype <dtype>`, default: bytes).

        Yields:
            named tuple: A named tuple per entry in the FASTA file, each containing:

                1. 'sequence': The actual sequence (without linebreaks)
                2. 'name': The chromosome's name
                3. 'length': The length of the sequence
                4. 'interval': A tuple `(start, end)` of start- and end-position of the chromosome in the **genome** (*not* in the file)
        """
        cdef:
            int line_length
            long offset = 0, start = 0
            list entry_info, entry_lengths, entry_intervals
            bytes line, name
            bytearray entry = bytearray()

        with InputOpener(self._source) as reader:
            for line in reader:
                line = line.rstrip()
                line_length = len(line)
                if line_length > 0:
                    head = line[0]
                else:
                    head = 0
                if head == GREATER_BYTE:
                    if len(entry) > 0:
                        yield FastaEntry(_change_dtype_bytearray(entry, dtype), name, offset - start, (start, offset))
                    name = line[1:]
                    entry = bytearray()
                    start = offset
                else:
                    entry += line  # use += instead of extend, as it is faster (see [1])
                    offset += line_length
            yield FastaEntry(_change_dtype_bytearray(entry, dtype), name, offset - start, (start, offset))

    cpdef genome(self, dtype=bytes):
        """Read in the complete genome sequence.

        This method returns the whole genome in a single data structure.
        Please be aware that this can consume a large amount of memory.

        Arguments:
            dtype (type): Desired type for the sequence(s) (see :ref:`dtype <dtype>`, default: bytes).

        Returns:
            FastaGenome: A named tuple containing the complete genome sequence
                encoded as the given dtype and a list of namedtuples (one for each chromosome):

                    - name: Name line of the chromosome
                    - length: Length of the chromosome
                    - interval: Begin and end index of the chromosome in the genome.
        """
        if dtype == str:
            return self._genome_str()

        cdef:
            int line_length, chr_length
            long offset = 0
            tuple interval
            dict entry
            list names = [], offsets = [0]
            bytes line, chr_name
            bytearray genome = bytearray()
        with InputOpener(self._source) as reader:
            for line in reader:
                line = line.rstrip()
                line_length = len(line)
                if line_length > 0:
                    head = line[0]
                else:
                    head = 0
                if head == GREATER_BYTE:
                    names.append(line[1:])
                    if len(genome) > 0:
                        offsets.append(offset)
                else:
                    genome += line  # use += instead of extend, as it is faster (see [1])
                    offset += line_length
        cdef long start, stop
        chromosome_intervals = list(zip(offsets, offsets[1:] + [len(genome)]))
        chromosome_lengths = [stop - start for (start, stop) in chromosome_intervals]
        chromosome_info = [FastaChromosomeInfo(name=chr_name, length=chr_length, interval=chr_interval) for
                           chr_name, chr_length, chr_interval in zip(names, chromosome_lengths, chromosome_intervals)]
        if dtype != bytearray:  # if chosen dtype is bytearray, we don't need to perform any conversion
            return FastaGenome(_change_dtype_bytearray(genome, dtype), chromosome_info)
        return FastaGenome(genome, chromosome_info)

    cdef _genome_str(self):
        """Same as genome(self, dtype=str) but with specific str code
        """
        cdef:
            int line_length, chr_length
            long offset = 0
            tuple interval
            dict entry
            list names = [], offsets = [0], lines = []
            bytes line, chr_name
            str genome
        with InputOpener(self._source) as reader:
            for line in reader:
                line = line.rstrip()
                line_length = len(line)
                if line_length > 0:
                    head = line[0]
                else:
                    head = 0
                if head == GREATER_BYTE:
                    names.append(line[1:])
                    if len(lines) > 0:
                        offsets.append(offset)
                else:
                    lines.append(line)
                    offset += line_length
        cdef long start, stop

        genome = (b''.join(lines)).decode()
        del lines

        chromosome_intervals = list(zip(offsets, offsets[1:] + [len(genome)]))
        chromosome_lengths = [stop - start for (start, stop) in chromosome_intervals]
        chromosome_info = [FastaChromosomeInfo(name=chr_name, length=chr_length, interval=chr_interval) for
                           chr_name, chr_length, chr_interval in zip(names, chromosome_lengths, chromosome_intervals)]
        return FastaGenome(genome, chromosome_info)

    def reads(self, read_names=False, dtype=bytes):
        """Yield all reads in the opened FASTA file as an iterator.

        Arguments:
            read_names(bool, optional): If `True`, returns (read_name, read)
                named tuples. Otherwise only plain reads will be returned.

            dtype (type): Desired type for the sequence(s) (see :ref:`dtype <dtype>`, default: bytes).

        Yields:
            dtype or named tuple: The sequence of the reads are yielded, encoded
                according to the given dtype. If `read_names` is set, a named tuple of *sequence* (dtype)
                and *name* (str) is yielded instead.

        Examples:
            Print all sequences of reads in the FASTA file:
            ::

                far = dinopy.FastaReader(filepath)
                for read in far.reads():
                    print(read)

            Iterate over all reads in the FASTA file. Print the names of the
            reads and do something magical with the read sequences.
            ::

                far = dinopy.FastaReader(filepath)
                for seq, name in far.reads(read_names=True):
                    print(name)
                    magic(seq)
        """
        cdef:
            int line_length
            bytearray read
            bytes line, read_name

        read = bytearray()
        with InputOpener(self._source) as reader:
            for line in reader:
                line = line.rstrip()
                line_length = len(line)
                if line_length > 0:
                    head = line[0]
                else:
                    head = 0
                if head == GREATER_BYTE:
                    if len(read) > 0:  # not true on first '>' encounter
                        encoded = _change_dtype_bytearray(read, dtype)
                        read = bytearray()
                        if read_names:
                            yield FastaRead(encoded, read_name)
                            read_name = line[1:]
                        else:
                            yield encoded
                    else:
                        if read_names:
                            read_name = line[1:]
                else:
                    read += line  # use += instead of extend, as it is faster (see [1])
            encoded = _change_dtype_bytearray(read, dtype)
            read = bytearray()
            if read_names:
                yield FastaRead(encoded, read_name)
            else:
                yield encoded

    def chromosomes(self, object selected_chromosomes=None, dtype=bytes):
        """Yield the selected chromosomes from the FASTA file.

        This iterator is intended to extract a subset of chromosomes from the
        genome. If all chromosomes are needed, please use :meth:`entries` instead.

        Arguments:
            selected_chromosomes (obj): Names or indices of the chromosomes
                that should be returned. These can either come as a list of
                integers, giving the positions of chromosomes that are to be
                read, or a single integer if only one chromosome should be read.
                Also accepts chromosome_names (of type str or bytes),
                or None (to return all chromosomes). (Default: None)

            dtype (type): Desired type for the sequence(s) (see :ref:`dtype <dtype>`, default: bytes).

        Yields:
            named tuple: A named tuple per entry in the FASTA file, each containing:

                1. 'sequence': The actual sequence (without linebreaks)
                2. 'name': The chromosome's name
                3. 'length': The length of the sequence
                4. 'interval': A tuple `(start, end)` of start- and end-position of the chromosome in the **genome** (zero based).


        Note:
            All chromosome indexes are zero-based. To get the first and third genome
            of a genome you have to pass selected_chromosomes=[0,2].
        """
        cdef bint by_position = True
        cdef bint return_all = False

        if selected_chromosomes is None:
            return_all = True
        elif isinstance(selected_chromosomes, int):
            selected_chromosomes = [selected_chromosomes]
        elif isinstance(selected_chromosomes, bytes):
            selected_chromosomes = [selected_chromosomes]
            by_position = False
        elif isinstance(selected_chromosomes, str):
            selected_chromosomes = [selected_chromosomes.encode()]
            by_position = False
        elif isinstance(selected_chromosomes[0], (str, bytes)):
            # convert all str names to bytes. keep all byte names as they are
            selected_chromosomes = [chrom.encode() if isinstance(chrom, str) else chrom for chrom in
                                    selected_chromosomes]
            by_position = False

        if return_all:
            yield from self.entries(dtype=dtype)
        elif by_position:
            if self._fai:
                fai_entries = [self._fai[i] for i in selected_chromosomes]
                with InputOpener(self._source) as reader:
                    for name, length, start, line_length, line_bytes in fai_entries:
                        reader.seek(start)
                        bytes_read = reader.read(int(ceil((length / line_length) * line_bytes)))  # We know the chromosome's length from the fai file but we still have to incorporate the number of line-break bytes
                        bytes_read = bytes_read.replace(b'\n', b'')  # careful: assuming '\n', never '\r\n'!
                        yield FastaChromosome(_change_dtype_bytes(bytes_read, dtype=dtype), name, length)
            else:
                for i, entry in enumerate(self.entries(dtype=dtype)):
                    if i in selected_chromosomes:
                        yield entry
                        # remove found chromosome.
                        # stop iteration, if all selected chromosomes have been found.
                        selected_chromosomes.remove(i)
                        if not selected_chromosomes:
                            break
        else:
            if self._fai:
                fai_entries = list(filter(lambda e: e[0] in selected_chromosomes, self._fai))
                with InputOpener(self._source) as reader:
                    for name, length, start, line_length, line_bytes in fai_entries:
                        reader.seek(start)
                        bytes_read = reader.read(int(ceil((length / line_length) * line_bytes)))  # We know the chromosome's length from the fai file but we still have to incorporate the number of line-break bytes
                        bytes_read = bytes_read.replace(b'\n', b'')  # careful: assuming '\n', never '\r\n'!
                        yield FastaChromosome(_change_dtype_bytes(bytes_read, dtype=dtype), name, length)
            else:
                for entry in self.entries(dtype=dtype):
                    if entry.name in selected_chromosomes:
                        yield entry
                        # remove found chromosome.
                        # stop iteration, if all selected chromosomes have been found.
                        selected_chromosomes.remove(entry.name)
                        if not selected_chromosomes:
                            break

    def lines(self, skip_name_lines=False, dtype=bytes):
        """Iterate over all lines in the given FASTA file.

        Arguments:
            skip_name_lines (boolean): If `True`, name lines will not be
                returned. (Default: False)

            dtype (type): Desired type for the sequence(s) (see :ref:`dtype <dtype>`, default: bytes).

        Yields:
            dtype: A line from the FASTA file. Sequence lines are encoded as
            dtype. Name lines (if skip_name_lines=False) are always returned as bytes.

        Examples:
            Print the content of the FASTA file:
            ::

                far = dinopy.FastaReader(filepath)
                for line in far.lines():
                    print(line)

            Print only the sequences from the FASTA file:
            ::

                far = dinopy.FastaReader(filepath)
                for line in far.lines(skip_name_lines=True):
                    print(line)
        """
        cdef int line_length
        cdef bytes byte_line

        with InputOpener(self._source) as reader:
            for line in reader:
                line = line.rstrip()
                line_length = len(line)
                if line_length > 0:
                    head = line[0]
                else:
                    head = 0
                if head == GREATER_BYTE:
                    if skip_name_lines:
                        continue
                    else:
                        yield line
                else:
                    yield (_change_dtype_bytes(line, dtype))
