# -*- coding: utf-8 -*-
import gzip
import os
import sys
from io import IOBase, BufferedWriter, DEFAULT_BUFFER_SIZE, FileIO, BufferedIOBase, TextIOWrapper
import _io
from .definitions cimport FastaGenome
from .fai_io import is_valid_fai, write_fai, fai_to_chromosome_info, chromosome_info_to_fai
from .exceptions import ChromosomeFormatError, InvalidDtypeError
from .output_opener cimport OutputOpener

cimport cython

cdef class FastaWriter(OutputOpener):
    @cython.embedsignature(False)
    def __init__(self, target, write_fai=False, force_overwrite=False, append=False, line_width=80):
        """__init__(target, write_fai=False, force_overwrite=False, append=False)

        FastaWriter for writing genomes (or reads) to disk in FASTA format.

        Arguments:
            target (str, bytes, file or sys.stdout): Path where the file will
                be written to. If the path ends with the suffix .gz, a gzipped
                file will be created.
            force_overwrite (bool): If set to `True` overwrites existing FASTA
                files with the same name. (Default: False)
            append (bool): If set to `True`, existing files will not be
                overwritten. Reads will be appended to the end of the file.
                (Default: False)
            write_fai (bool, bytes or string): If `write_fai` denotes a path,
                write FASTA annotation information file to the specified path.
                If `write_fai` is `True` (and does not resemble a path, i.e. is
                not an instance of `str` or `bytes`) annotation information will
                be written to `filepath + '.fai'`, which is the default behaviour.
                Note that `force_overwrite` and `append` apply to fai-files aswell.
                (Default: False)
            line_width (int): The maximum number of characters per line, excluding newlines.
                (Default: 80)

        Raises:
            ValueError: If the filename is invalid.
            ValueError: If contradicting parameters are passed (overwrite=True and append=True).
            TypeError: If target is neither a file, nor a path nor stdout.
            IOError: If target is a file opened in the wrong mode.
            FileExistsError: If target file (FASTA or fai) already exists and neither overwrite nor append have been specified.

        Methods intended for public use are:

          - :meth:`write_genome`: Write a whole genome to file. 

          - :meth:`write_entries`: Writes a list of tuples containing entry
            names and entry sequences. The tuples have to be in the format:
            ``(entry_sequence, entry_name)``
        
            An entry can be a chromosome or a read.

          - :meth:`write_entry`: Write a single entry to the openend file.

          - :meth:`write_chromosomes`: Writes a list of chromosomes to file.
            Each chromosome must consist of a tuple containing:
            ``(chromosome_sequence, chromosome_name)``

          - :meth:`write_chromosome`: Writes a single chromosome to file.

        Examples:

            Write a genome of three chromosomes from a single sequence::

                seq = b"ACGTAACCGGTTAAACCCGGGTTT"
                chr_info = [
                    (b"single", 4, (0,4)),
                    (b"double", 8, (4,12)),
                    (b"triple", 12, (12,24)),
                ]
                with dinopy.FastaWriter('somefile.fasta') as faw:
                    faw.write_genome(seq, chr_info)


            Write a genome of three chromosomes from separate chromosomes::

                chromosomes = [
                    ('ACGTACGT', b'chr1'),
                    ('GCGTAGGATGGGCCTATCGA', b'chr2'),
                    ('CCATAGGATAGACCANNACAGATCAN', b'chr3'),
                ]
                with dinopy.FastaWriter('somefile.fasta') as faw:
                    faw.write_chromosomes(chromosomes, dtype=str)
        """
        # set desired write mode and save append / overwrite policy
        if append and force_overwrite:
            raise ValueError(
                "Please specify EITHER force_overwrite (to overwrite an existing file) OR append (to append to an existing file).")
        super().__init__(target, 'b' + 'a' if append else ('f' if force_overwrite else ''))
        self._line_width = line_width
        try:  # TODO do not use try except for code flow
            self._filepath = os.path.abspath(os.path.expanduser(target))
        except:
            try:
                self._filepath = target.name if hasattr(target, "name") else None
            except:
                pass

        # set target for fai file.
        if write_fai is True:
            # Check for True -> autodetect path
            self._write_fai = True
            if self._filepath is not None:
                # write fai file next to fasta file with .fai suffix
                self._fai_path = self._filepath + ".fai"
            else:
                # Target is a stream. Write fai file as genome.fai in
                # the current working dir
                self._fai_path = "genome.fai"
        elif write_fai:
            # Check for path
            if isinstance(write_fai, bytes):
                write_fai = write_fai.decode("utf-8")
            if not isinstance(write_fai, str):
                raise TypeError("write_fai has to be either True, False or a path as bytes or str.")
            self._write_fai = True
            self._fai_path = write_fai
        else:
            # Do not write a .fai-file
            self._write_fai = False
            self._fai_path = None

    cpdef write_genome(
            self,
            object genome,
            object chromosome_info=None,
            type dtype=bytes,
    ):
        """Write a genome to the specified filepath.

        Arguments:
            genome(dtype): Genome sequence to be written to file as a
                single iterable of dtype.
            chr_info (tuple, str or bytes): Chromosome names and borders in the
                format: `(chr_name[str], length[int], chr_interval[tuple of two ints])`
                or a single (byte)string. If a single (byte)string is encountered,
                it will be used as a genome name and the whole genome sequence
                will be written as a "single chromosome".
            dtype (type): Type of the sequence. (See :ref:`dtype <dtype>`; Default: bytes)

        Raises:
            IOError: If no output FASTA file has been opened.

        Note:
            The separation of the genome is handled according to the given
            chromosome info. If the sequences is already split up into
            chromosomes please use write_chromosome / write_entry which
            do not need chromosome info to be specified.

            If ``chromosome_info`` is a string or bytes, the genome is treated
            as a single chromosome with the string as name.
            If multiple chromosomes are to be written ``chromosome_info``
            has to be a list of tuples in the format:
            ``(chr_name[str], length[int], chr_interval[tuple of two ints])``
        """
        cdef:
            long genome_length
            long length, start, stop
            bytes chr_name
            tuple chr_interval
            list fai
            object seq = genome
        #check if a file is open
        if self.is_open():

            if chromosome_info is None:
                if isinstance(genome, FastaGenome):
                    chromosome_info = genome.info
                    seq = genome.sequence
                else:
                    raise ValueError("Chromosome info must not be None if genome is a primitive sequence.")

            genome_length = len(seq)
            # validate the chromosome info
            chromosome_info = self._normalize_chromosome_info(chromosome_info, genome_length)
            # write chromosomes to file
            for chr_name, length, chr_interval in chromosome_info:
                start, stop = chr_interval
                self._write_entry(seq[start:stop], chr_name, dtype=dtype)
            if self._write_fai:
                fai = chromosome_info_to_fai(chromosome_info, line_length=self._line_width)
                write_fai(self._filepath + ".fai", fai)
        else:
            raise IOError("No file openend. Use with FastaWriter(target) as faw:\ faw.write_genome(...)")

    cpdef write_chromosomes(
            self,
            object chromosomes,
            type dtype=bytes,
    ):
        """Write chromosomes to the specified filepath.

        Note: Alias for `write_entries(entry, dtype).`

        Arguments:
            chromosomes (iterable): Iterable of (sequence, name) tuples,
                where seq is the sequence of the chromosome (as dtype) and name
                is the chromosome name as bytes.
            dtype (type): Type of the sequence. (See :ref:`dtype <dtype>`; Default: bytes)

        Raises:
            IOError: If no output FASTA file has been opened.

        Note:
            This method is used to write a list of separate chromosomes to file.
            To split up a long sequence into chromosomes please use
            ``write_genome(genome, chr_info, ...)``, where ``chr_info`` is a list of
            tuples that contain name, length (start, stop) for each chromosome,
            or just a name (as str/bytes) if the organism only has one
            chromosome.
        """
        self.write_entries(chromosomes, dtype)

    cpdef write_entries(
            self,
            object entries,
            type dtype=bytes,
    ):
        """Write entries to the specified filepath.

        Arguments:
            entries (iterable): Iterable of (seq, name) tuples,
                where seq is the sequence of the entry (as dtype) and name
                is the entry's name as bytes.
            dtype (type): Type of the sequence. (See :ref:`dtype <dtype>`; Default: bytes)

        Raises:
            IOError: If no output FASTA file has been opened.

        Note:
            This method is used to write a list of separate entries to file.
            To split up a long sequence into chromosomes please use
            ``write_genome(genome, chr_info, ...)``, where ``chr_info`` is a list of
            tuples that contain name, length (start, stop) for each chromosome,
            or just a name (as str/bytes) if the organism only has one
            chromosome.
        """
        if self.is_open():
            self._write_entry_iterable(entries, dtype=dtype)
        else:
            raise IOError("No file openend. Use with FastaWriter(target) as faw:\ faw.write_genome(...)")

    cpdef write_chromosome(
            self,
            object chromosome,
            type dtype=bytes,
    ):
        """Write a single chromosome to the opened FASTA file.

        Note: Alias for `write_entry()`.

        Arguments:
            chromosome (tuple): Containing chromosome sequence (as dtype) and chromosome name (bytes).
            dtype (type): Type of the sequence. (See :ref:`dtype <dtype>`; Default: bytes)
        """
        self.write_entry(chromosome, dtype)

    cpdef write_entry(
            self,
            object entry,
            type dtype=bytes,
    ):
        """Write a single entry to the opened FASTA file.

        Arguments:
            entry (tuple): Containing entry sequence (as dtype) and entry name (bytes).
            dtype (type): Type of the sequence. (See :ref:`dtype <dtype>`; Default: bytes)
        
        Raises:
            IOError: If no output FASTA file has been opened.
        """
        cdef:
            bytes name
            object sequence
        if self.is_open():
            sequence, name, *_ = entry
            self._write_entry(sequence, name, dtype=dtype)
        else:
            raise IOError("No file openend. Use with FastaWriter(target) as faw:\n   faw.write_genome(...)")

    cpdef _write_entry_iterable(
            self,
            object entries,
            type dtype=bytes,
    ):
        """Write a list of entries to the FASTA file using _write_entry.

        Arguments:
            entries (list of tuples): Containing entries as tuples of sequence (as dtype), name (as bytes).
            dtype (type): Type of the sequence. (See :ref:`dtype <dtype>`; Default: bytes)
        
        Raises:
            IOError: If no output FASTA file has been opened.
        """
        cdef:
            bytes name
            object sequence
        if self.is_open():
            for (sequence, name, *_) in entries:
                self._write_entry(sequence, name, dtype=dtype)
        else:
            raise IOError("No file openend. Use with FastaWriter(target) as faw:\ faw.write_genome(...)")

    cpdef _write_entry(
            self,
            object sequence,
            bytes name,
            type dtype=bytes,
    ):
        """Write a single entry to the opened FASTA file.

        Arguments:
            sequence (dtype): Sequence of the entry (as dtype).
            name (bytes): Name of the entry that will be written to the file.
            dtype (type): Type of the sequence. (See :ref:`dtype <dtype>`; Default: bytes)

        Raises:
            InvalidDtypeError: If the dtype of the sequence wasn't recognized.
        """
        cdef:
            bytes name_line
            long length, start, stop
            list linebreak_points, intervals

        # write the name line
        name_line = b">" + name + b"\n"
        self.writer.write(name_line)

        # compute chromosome borders and points to insert linebreaks
        length = len(sequence)
        linebreak_points = list(range(0, length, self._line_width))
        intervals = list(zip(linebreak_points, linebreak_points[1:] + [length]))
        # convert sequence according to dtype
        if dtype == basenumbers:
            for start, stop in intervals:
                self.writer.write(basenumbers_to_bytes(sequence[start:stop]) + b"\n")
        elif dtype == bytearray:
            for start, stop in intervals:
                self.writer.write(sequence[start:stop] + b"\n")
        elif dtype == bytes:
            for start, stop in intervals:
                self.writer.write(sequence[start:stop] + b"\n")
        elif dtype == str:
            for start, stop in intervals:
                self.writer.write(string_to_bytes(sequence[start:stop]) + b"\n")
        else:
            raise InvalidDtypeError(
                "Invalid dtype '{}', dtype has to be bytes, bytearray, str or dinopy.basenumbers".format(dtype))

    cpdef list _normalize_chromosome_info(
            self,
            object chr_info,
            int genome_length,
    ):
        """Try to generate a valid chr_info list from the input.

        Note:
            A chr_info list is valid if it consists of a number of tuples
            of the form (name, length, (start, stop)).

        Note:
            A fai entry is 5-tuple of name (str), length (int), start index (int)
            line length in characters (int) and line length in bytes (int).

        Arguments:
            chr_info (bytes or list of tuples): Object to be checked for valid
                chromosome info. This can be a list of chromosome_infos triples,
                a list of fai entries, or a genome name (as str or bytes).
            genome_length (int): Total length of the genome chr_info referring to.

        Returns:
            A validated and normalized version of chr_info as a list containing
            valid triples (see above).
        """
        cdef:
            object item
            object chr_name
            int chr_length, chr_start, chr_stop
            list normalized_chr_info = []
        # check if the chr_info is just the genomes name (str or bytes)
        if isinstance(chr_info, str):
            item = (chr_info.encode(), genome_length, (0, genome_length))
            return [item]
        elif isinstance(chr_info, bytes):
            item = (chr_info, genome_length, (0, genome_length))
            return [item]
        else:
            # check if chr_info is a valid fai-list
            # see fai_io.py for details
            if is_valid_fai(chr_info):
                # translate fai entries to chr_info format
                chr_info = fai_to_chromosome_info(chr_info)
            try:
                for item in chr_info:
                    try:
                        chr_name, chr_length, (chr_start, chr_stop) = item
                        if chr_start < 0:
                            raise IndexError("Chromosome start < 0 ({})".format(chr_start))
                        if chr_start > genome_length:
                            raise IndexError(
                                "Chromosome start > genome length ({} > {})".format(chr_start, genome_length))
                        if chr_stop > genome_length:
                            raise IndexError(
                                "Chromosome stop > genome length ({} > {})".format(chr_stop, genome_length))
                        if chr_start > chr_stop:
                            raise IndexError("Chromosome start > chromosome stop ({} > {})".format(chr_start, chr_stop))
                        if chr_stop - chr_start > chr_length:
                            raise IndexError(
                                "Chosen range (from {} to {}) is longer than actual chromosome length {}".format(
                                    chr_start, chr_stop, chr_length))
                        if chr_stop - chr_start < chr_length:
                            raise IndexError(
                                "Chosen range (from {} to {}) is shorter than actual chromosome length {}".format(
                                    chr_start, chr_stop, chr_length))
                        if isinstance(chr_name, str):
                            normalized_chr_info.append((chr_name.encode(), chr_length, (chr_start, chr_stop)))
                        elif isinstance(chr_name, bytes):
                            normalized_chr_info.append(item)
                        else:
                            raise TypeError("Chromosome name has to be str nor bytes, not {}.".format(type(chr_name)))
                    except TypeError:
                        raise ChromosomeFormatError(
                            "Encountered Error while splitting the item {} into chr_name, chr_length, (chr_start, chr_stop).\nChromosome Info has to be of type bytes (a name) or list (of triples name, length, (start, stop))".format(
                                item))
                    except ValueError:
                        raise ChromosomeFormatError(
                            "Encountered Error while splitting the item {} into chr_name, chr_length, (chr_start, chr_stop).\nChromosome Info has to be of type bytes (a name) or list (of triples name, length, (start, stop))".format(
                                item))
            except TypeError:
                raise ChromosomeFormatError(
                    "Encountered Error while iterating over {}\nChromosome Info has to be of type bytes (a name) or list (of triples name, length, (start, stop))".format(
                        chr_info))
        return normalized_chr_info

    cpdef __enter__(self):
        OutputOpener.__enter__(self)
        return self

    cpdef close(self):
        """Close the file (after writing).

        Note:
            This should only be used if the exact number of files is not known
            at develpoment time. Otherwise the use of the environment is
            encouraged, as it is much harder to 'forget' closing an opened file.
        """
        OutputOpener.close(self)
