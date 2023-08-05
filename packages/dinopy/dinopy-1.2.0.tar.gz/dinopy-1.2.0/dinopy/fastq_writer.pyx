# -*- coding: utf-8 -*-
#cython: wraparound=False
import gzip
import os
import sys
from io import IOBase, BufferedWriter, DEFAULT_BUFFER_SIZE
from .exceptions import InvalidDtypeError
from .output_opener cimport OutputOpener

cimport cython

cdef class FastqWriter(OutputOpener):
    @cython.embedsignature(False)
    def __init__(self, target, force_overwrite=False, append=False):
        """__init__(target, force_overwrite=False, append=False)

        Create a new FastqWriter for writing reads to disk in fastq format.

        Manages opening and closing of files. This works best when using a with
        environment (see Examples), but the open and clode methods of the
        writer can also be called directly. This can be useful, when the
        number of files to be opened is depending on the input data.

        Arguments:
            target (str, bytes, file or sys.stdout): Path where the file will be written to.
                If the path ends with the suffix .gz a gzipped file will be created.
            force_overwrite (bool): If set to True, an existing file will be overwritten.
                (Default: False)
            append (bool): If set to True, existing file will not be overwritten.
                Reads will be appended at the end of the file. (Default: False)

        Raises:
            ValueError: If the filename is invalid.
            ValueError: If contradicting parameters are passed (overwrite=True and append=True).
            TypeError: If target is neither a file, nor a path nor stdout.
            IOError: If target is a file opened in the wrong mode.
            IOError: If target file already exists and neither overwrite nor append are specified.

        Methods intended for public use are:

          - :meth:`write`: Write one read to the opened file.

          - :meth:`write_reads`: Writes given reads to file, where reads must
            be an Iterable over either `(sequence, sequence_id, quality_values)`
            or `(sequence, sequence_id)` tuples.

        Examples:

            Writing reads from a list::

                reads = [("TTTTTTTTGGANNNNN", b"sequence_id", b"#+++3#+/-.1/1/.<")]
                with dinopy.FastqWriter("somefile.fastq") as fqw:
                    fqw.write_reads(reads, dtype=str)

            Results in:

            | @sequence_id
            | TTTTTTTTGGANNNNN
            | +
            | #+++3#+/-.1/1/.<
            |
            |

            Writing a single read::

                with dinopy.FastqWriter("somefile.fastq.gz") as fqw:
                    fqw.write(b"TTTTTTTTGGANNNNN", b"sequence_id", b"#+++3#+/-.1/1/.<")

            Results in:

            | @sequence_id
            | TTTTTTTTGGANNNNN
            | +
            | #+++3#+/-.1/1/.<
            |
            |

            Using a FastqWriter without the with-environment.
            Make sure the file is closed after you finished writing.::

                fqw = dinopy.FastqWriter("somefile.fastq")
                fqw.open()
                fqw.write(b"TTTTTTTTGGANNNNN", b"sequence_id", None, dtype=bytes)
                fqw.close()

            Results in:

            | @sequence_id
            | TTTTTTTTGGANNNNN
            |
            |

            Using a variable number of writers.::

                # create a dict of writers
                writers = {name: dinopy.FastqWriter(path) for name, path in zip(specimen, input_filepaths)}
                # open all writers
                for writer in writers:
                    writer.open()

                for read in reads:
                    # pick a writer / output file according to some properties of the read
                    # and write the read using the picked writer.
                    picked_writer = pick(read, writers)
                    picked_writer.write(read)

                # close all writers
                for writer in writers:
                    writer.close()

        """
        # set desired write mode and save append / overwrite policy
        super().__init__(target, 'b' + 'a' if append else ('f' if force_overwrite else ''))

    cpdef write_reads(self, object reads, bool quality_values=True, type dtype=bytes):
        """Write multiple reads to file.

        Arguments:
            reads (Iterable): Containing reads, i.e. tuples of sequence, name
                and (optionally) quality values
            quality_values(bool): If set to True (Default) quality values are written to file.
            dtype(type): Type of the sequence(s) (See :ref:`dtype <dtype>`; Default: bytes)

        Raises:
            IOError: If no file has been opened, i.e. the writer has neither
                been opened using a with environment nor the open method has been
                called explicitly.

        Example:

            Write a list of reads to file::

                reads = [("TTTTTTTTGGANNNNN", b"sequence_id", b"#+++3#+/-.1/1/.<")]
                with dinopy.FastqWriter("somefile.fastq") as fqw:
                    fqw.write_reads(reads, dtype=str)

        """
        try:
            if self.is_open():
                if dtype in (bytes, bytearray):
                    if quality_values:
                        for (seq, seq_id, qvs) in reads:
                            self._write_bytes(seq, seq_id, qvs)
                    else:
                        # catch (and ignore) quality values
                        for (seq, seq_id, *_) in reads:
                            self._write_bytes(seq, seq_id, None)
                elif dtype == str:
                    if quality_values:
                        for (seq, seq_id, qvs) in reads:
                            self._write_bytes(string_to_bytes(seq), seq_id, qvs)
                    else:
                        # catch (and ignore) quality values
                        for (seq, seq_id, *_) in reads:
                            self._write_bytes(string_to_bytes(seq), seq_id, None)
                elif dtype == basenumbers:
                    if quality_values:
                        for (seq, seq_id, qvs) in reads:
                            self._write_bytes(basenumbers_to_bytes(seq), seq_id, qvs)
                    else:
                        # catch (and ignore) quality values
                        for (seq, seq_id, *_) in reads:
                            self._write_bytes(basenumbers_to_bytes(seq), seq_id, None)
                else:
                    raise InvalidDtypeError("Unrecognized dtype {}".format(dtype))
            else:
                raise IOError(
                    "No file openend. Use a with environment like:\nwith FastqWriter(target) as fqw:\n  fqw.write_reads(...)")
        except TypeError as te:
            raise

    cpdef write(self, object seq, bytes name, bytes quality_values=None, type dtype=bytes):
        """Write a single read to file.

        Arguments:
            seq (dtype): Sequence of the read
            name (bytes): Name line for the read
            quality_values (bytes): Quality values of the read.
            dtype(type): Type of the sequence(s) (See :ref:`dtype <dtype>`; Default: bytes)

        Raises:
            IOError: If FastqWriter was not used in an environment. → No file has been opened.
            InvalidDtypeError: If an invalid encoding for the sequence has been given.

        Example:
            Write a single read to file::

                with dinopy.FastqWriter("somefile.fastq") as fqw:
                    fqw.write(b"TTTTTTTTGGANNNNN", b"sequence_id", b"#+++3#+/-.1/1/.<")
        """
        try:
            if self.is_open():
                if dtype in (bytes, bytearray):
                    self._write_bytes(seq, name, quality_values)
                elif dtype == str:
                    self._write_bytes(string_to_bytes(seq), name, quality_values)
                elif dtype == basenumbers:
                    try:
                        self._write_bytes(basenumbers_to_bytes(seq), name, quality_values)
                    except KeyError:
                        raise InvalidDtypeError("Error treating sequence {} as basenumbers for conversion.".format(seq))
                elif dtype in (two_bit, four_bit):
                    raise InvalidDtypeError("two_bit or four_bit encoding not permitted here.")
            else:
                raise IOError("No file openend. Use with FastqWriter(target) as fqw:\ fqw.write(...)")
        except TypeError as te:
            raise

    cdef _write_bytes(self, bytes seq, bytes name, bytes quality_values):
        """Write a given read to the file.

        The plus-line stays empty, to save disk space.

        Arguments:
            seq (bytes): Sequence of the read
            name (bytes): Nameline of the read without leading @
            quality_values (bytes): Quality values for the read. If this is
                 None, no quality values and no plus-line are written.
        """
        cdef bytes line
        line = b'@' + name + b'\n' + seq + b'\n'
        if quality_values is not None:
            line += b'+\n' + quality_values + b'\n'
        self.writer.write(line)

    cpdef __enter__(self):
        """Open the file for writing when the environment is entered."""
        OutputOpener.__enter__(self)
        return self
