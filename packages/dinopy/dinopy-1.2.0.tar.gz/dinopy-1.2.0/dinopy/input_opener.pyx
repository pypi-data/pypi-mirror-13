# -*- coding: utf-8 -*-
import sys
import os
import io
import gzip

cimport cython
from dinopy.creader cimport CReader

cdef class InputOpener:
    @cython.embedsignature(False)
    def __init__(self, source, native_io=True):
        """__init__(source, native_io=False)

        Open the input as an iterable over byte lines.

        General opener for all input sources supported by dinopy.
        Assures that an iterable over the input is present as
        an Iterable over bytes objects (lines).

        Arguments:
            source: sys.stdin, file_object (io.BufferedReader),
                    list (of strings) or filepath (gzipped or plain file)

            native_io (bool): Use native, low level c calls where possible. Defaults to `True`. Only supports plain files at the moment.

        Examples:

            Opening a file::

                with InputOpener("filepath/file.fastq") as input_iter:
                    for line in input_iter:
                        magic(line)

            Reading from stdin::

                with InputOpener(sys.stdin) as input_iter:
                    for line in input_iter:
                        magic(line)
        """
        self.source = source
        self.native_io = native_io
        self.input_iterable = None

    cpdef object __enter__(self):
        """Open the input as an iterable over byte lines.

        The following sources are supported:
            sys.stdin
            file_objects (io.BufferedReader)
            list (of strings) Use this only for debug reasons.
            filepath (to a gzipped or plain text file.)
            any iterable source inheriting from IOBase (i.e. io.StringIO)

        Returns:
            Iterable of byte lines. If possible as io.BufferedReader.

        Raises:
            FileNotFoundError: If the given file does not exist.
            TypeError: If the input source is of an unsupported type.
        """
        cdef:
            str filepath
            object input_file
        if self.source == sys.stdin:
            # check if the input comes from stdin
            self.input_iterable = self.source.buffer
            self.input_closable = False
        elif isinstance(self.source, io.IOBase):
            # check if the input is an already opened io handle
            self.input_iterable = self.source
            self.input_closable = False
        elif isinstance(self.source, list):
            # Force utf-8 dtype similar to stdin.buffer.
            self.input_iterable = [l.encode('utf-8') for l in self.source]
            self.input_closable = False
        elif isinstance(self.source, str):
            # Check if file exists, then check if it is zipped.
            filepath = self.source
            if os.path.exists(filepath):
                if filepath[-3:] == ".gz":
                    # Handle zipped file.
                    input_file = gzip.GzipFile(filepath, 'rb')
                    self.input_iterable = io.BufferedReader(input_file, buffer_size=64 * io.DEFAULT_BUFFER_SIZE)
                    self.input_closable = True
                else:
                    # Handle plain file.
                    if self.native_io:
                        self.input_iterable = CReader(filepath)
                        self.input_closable = True
                    else:
                        input_file = open(filepath, 'rb')
                        self.input_iterable = io.BufferedReader(input_file, buffer_size=64 * io.DEFAULT_BUFFER_SIZE)
                        self.input_closable = True
            else:
                raise FileNotFoundError("No such file or directory: " + filepath)
        else:
            raise TypeError("Unsupported input source type: {}".format(str(type(self.source))))
        return self.input_iterable

    cpdef __exit__(self, object ttype, object value, object traceback):
        """Close the file (if possible).

        If something strange happens, (i.e.) an exception is raised, re-raise it."""
        if self.input_closable:
            # Close the file if necessary
            self.input_iterable.close()
        # maybe catch some exceptions here?
        # raised exceptions are stored in the value variable.
        if value is not None:
            raise value
