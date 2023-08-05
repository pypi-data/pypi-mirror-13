# -*- coding: utf-8 -*-
import sys
import os
import io
import gzip
from io import BufferedWriter, IOBase

cimport cython

cdef class OutputOpener:
    @cython.embedsignature(False)
    def __init__(self, sink, mode='b'):
        """__init__(sink)

        Open the output as an iterable over byte lines.

        General opener for all output sinks supported by dinopy.
        Assures that an iterable over the output is present as
        an Iterable over bytes objects (lines).

        Arguments:
            sink: sys.stdout, file_object (BufferedWriter),
                    filepath (gzipped or plain file)
            mode: a combination of

                    - 'b' / 't' for binary / text and

                    - 'a' / 'f' / '' for append / force overwrite / raise Error if file exists.

                    Defaults to 'b'.

        Examples:

            Writing to a file::

                with OutputOpener("filepath/file.fastq") as writer:
                    writer.write(stuff)

            Writing to stdout::

                with OutputOpener(sys.stdout) as writer:
                    writer.write(stuff)
        """
        # check if the `sink` argument is valid
        if sink is None:
            raise TypeError("Sink must not be None.")
        if isinstance(sink, str) and not sink.strip():
            raise ValueError("Sink must be either a path to a file or a filehandle/stream, not {}.".format(sink))
        if not (isinstance(sink, (str, bytes, IOBase)) or sink == sys.stdout or sink==sys.stdout.buffer):
            raise TypeError("Sink must be either a path to a file or a filehandle/stream, not {} ({}).".format(sink, type(sink)))

        self.sink = sink
        self.output_closable = True

        if 't' in mode and 'b' in mode:
            raise ValueError("Text mode 't' and binary mode 'b' are mutually exclusive.")
        self.output_type = 't' if 't' in mode else 'b'

        if self.output_type is 't' and isinstance(sink, str) and sink[-3:] == ".gz":
            raise ValueError("GZip output does not support textmode. Use 'b' instead.") # TODO automatically encode instead? Same for sys.stdout

        if 'w' in mode and 'a' in mode:
            raise ValueError("Write mode 'w' and append mode 'a' are mutually exclusive.")

        if not set(mode).issubset(set(['w', 'a', 't', 'b', 'f'])):
            raise ValueError("Unsupported mode '{}'".format(mode))

        if isinstance(sink, IOBase):
            if not sink.writable():
                raise OSError("{} is not writable".format(str(sink)))

        self.append = 'a' in mode
        self.force_overwrite = 'f' in mode
        self.mode = ('a' if self.append else 'w') + self.output_type

    cpdef bool is_open(self):
        return self.opened

    cpdef object __enter__(self):
        """Open the output as an iterable over byte lines.

        The following sinks are supported:
            sys.stdout
            file_objects (BufferedWriter, io.RawIOBase)
            filepath (to a gzipped or plain text file.)
            any iterable sink inheriting from IOBase (i.e. io.StringIO)

        Returns:
            An OutputOpener instance capable of writing to the specified sink.

        Raises:
            FileNotFoundError: If the given file does not exist.
            TypeError: If the output sink is of an unsupported type.
        """
        cdef:
            str filepath
            object output_file

        self.opened = True  # assuming we don't fail opening sth → in that case, set to False

        # convert bytes paths to str paths
        if isinstance(self.sink, bytes):
            self.sink = self.sink.decode("utf-8")

        if self.sink == sys.stdout:
            # check if the output comes from stdout
            self.writer = self.sink.buffer
            self.output_closable = False
        elif self.sink == sys.stdout.buffer:
            # check if the output comes from stdout
            self.writer = self.sink
            self.output_closable = False
        elif isinstance(self.sink, io.IOBase):
            # check if the output is an already opened io handle. We don't need to do anything here.
                self.writer = self.sink
        elif isinstance(self.sink, str):
            # Check if file is zipped, check if file exists
            filepath = self.sink
            if filepath[-3:] == ".gz":
                # Handle zipped file.
                if not os.path.exists(filepath) or self.force_overwrite:
                    output_file = gzip.GzipFile(filepath, self.mode)
                elif self.append:
                    output_file = gzip.open(filepath, self.mode)
                else:
                    self.opened = False
                    raise FileExistsError("File exists: " + filepath)
                self.writer = BufferedWriter(output_file, buffer_size=64 * io.DEFAULT_BUFFER_SIZE)
            else:  # a regular (not compressed) file
                if os.path.exists(filepath) and not (self.force_overwrite or self.append):
                    self.opened = False
                    raise FileExistsError("File exists: " + filepath)
#                path, filename = os.path.split(filepath)
#                if not os.path.exists(path):
#                    os.makedirs(path)
                output_file = open(filepath, self.mode)
                if 't' in self.mode:
                    self.writer = output_file
                else:
                    self.writer = BufferedWriter(output_file, buffer_size=64 * io.DEFAULT_BUFFER_SIZE)
        else:
            raise TypeError("Unsupported output sink type: {}".format(str(type(self.sink))))
        return self.writer

    cpdef close(self):
        """Close the OutputOpener manually.
        Note: We recommend using the with environment instead"""
        if self.opened and self.output_closable:
            # Close the file if necessary
            self.writer.close()
        self.opened = False

    cpdef __exit__(self, object ttype, object value, object traceback):
        """Close the file (if possible).

        If something strange happens, (i.e.) an exception is raised, re-raise it."""
        self.close()
        # maybe catch some exceptions here?
        # raised exceptions are stored in the value variable.
        if value is not None:
            raise value
