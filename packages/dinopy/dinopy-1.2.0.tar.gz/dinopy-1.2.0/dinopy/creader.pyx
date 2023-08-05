# -*- coding: utf-8 -*-
import os

cimport cython

cdef class CReader:
    @cython.embedsignature(False)
    def __init__(self, str source):
        """__init__(source)
        A cython extension class acting as a 'low level' reader for plain files.
        Implements the IOBase 'interface', i.e. supports all operations that any IOBase instance is to support.
        Also supports the 'with' statement/environment.
        If you plan to read a whole file at once, please use the :meth:`readlines` method.

        Arguments:
            source(str): Path of the file that is to be read.

        Example 1::

            with CReader("foo.txt") as bar:
                for line in bar:
                    print(line)
        """
        self.source = source
        self.cfile = NULL
        self.open(self.source)

    def __iter__(self):
        if self.cfile == NULL:
            self.open(self.source)
        return self._iterate_file()

    def __enter__(self):
        cdef str filepath = self.source
        if os.path.exists(filepath):
            if self.cfile == NULL:
                self.open(self.source)
            return self

    def __exit__(self, type, value, traceback):
        self.close()

    cpdef close(self):
        """Flush and close this stream. This method has no effect if the file is already closed.
        Once the file is closed, any operation on the file (e.g. reading or writing) will raise an Error.
        As a convenience, it is allowed to call this method more than once; only the first call, however, will have an effect.

        Raises:
            IOError: If a non-zero error code has been returned by fclose.
        """
        cdef int errno
        if self.closed:
            return
        errno = fclose(self.cfile)
        if errno != 0:
            raise IOError("fclose return value {} != 0".format(str(errno)))
        else:
            self.closed = True

    cpdef int fileno(self):
        """Return the underlying file descriptor (an integer) of the stream if it exists.

        Raises:
            OSError: If the underlying object does not use a file descriptor.
        """
        if self.cfile != NULL:
            return fileno(self.cfile)
        else:
            raise OSError("No file handle for {}".format(str(self.source)))

    cpdef flush(self):
        """Will not do anything, as this is a read only stream."""
        return

    cpdef bool isatty(self):
        """Returns false, as this is not a tty.

        Returns:
            `False`
        """
        return False

    cpdef bool readable(self):
        """Return `True` if the stream can be read from. If `False`, read() will raise OSError."""
        return self.cfile != NULL and not self.closed

    cpdef long seek(self, long offset, int whence=SEEK_SET):
        """Change the stream position to the given byte offset.

        Arguments:
            offset(long): Target stream position as an offset 
            whence (int): One of io.SEEK_SET (0), io.SEEK_CUR (1) or io.SEEK_END (2).

        Returns:
            long: The new absolute position.

        Note:
            The offset is interpreted relative to the position indicated by whence. 
            Values for `whence` are::

                SEEK_SET or 0 – start of the stream (the default); offset should be zero or positive
                SEEK_CUR or 1 – current stream position; offset may be negative
                SEEK_END or 2 – end of the stream; offset is usually negative

            These constants are also defined in the python io package.
        """
        return fseek(self.cfile, offset, whence)

    cpdef bool seekable(self):
        """Always returns `True`

        Returns:
            `True`
        """
        return True

    cpdef long tell(self):
        """

        Returns:
            The current stream position.
        """
        return ftell(self.cfile)

    cpdef truncate(self, int size=-1):
        """Not implemented.
        Resize the stream to the given size in bytes (or the current position if size is not specified).
        The current stream position isn’t changed. This resizing can extend or reduce the current file size.
        In case of extension, the contents of the new file area depend on the platform (on most systems,
        additional bytes are zero-filled, on Windows they’re undetermined).

        Args:
            size (int):

        Returns:
            the new file size

        Raises:
            NotImplementedError
        """
        raise NotImplementedError

    cpdef bool writable(self):
        """Always returns false.

        Returns:
            `False`
        """
        return False

    cpdef writelines(self, list lines):
        """Not implemented.

        Raises:
            NotImplementedError
        """
        raise NotImplementedError

    def __del__(self):
        self.close()

    cpdef CReader open(self, str filename):
        """Open the file described by the given filename.

        Arguments:
            filename(str): Path to an existing file that will be opened.

        Returns:
            A CReader object on the opened file.

        Raises:
            FileNotFoundError: If no file with the given path exists.
        """
        cdef char *fname
        filename_bytestring = filename.encode("UTF-8")
        fname = filename_bytestring
        self.cfile = fopen(fname, "rb")
        if self.cfile == NULL:
            raise FileNotFoundError(2, "No such file or directory: '%s'" % filename)
        return self

    cpdef bytes read(self, int num_bytes):
        """Tries reading `num_bytes` bytes from the underlying stream.
        If that is not possible, which is the case when we're at the end of the underlying stream, will return :code:`None`.

        Args:
            num_bytes (int): The number of bytes to be read from the stream.

        Raises:
            IOError: if `fread` returns -1

        Returns:
            a the bytes read (of type `bytes`)
        """
        cdef size_t l = 1
        cdef size_t num_bytes_t = num_bytes
        cdef ssize_t read
        cdef bytes target
        cdef char*target_ptr

        # here a bytes-object of size num_bytes is needed.
        # bytes cannot be (easily) created directly
        target = bytes(bytearray(num_bytes))

        target_ptr = <char*> target  # pointer to the address of target

        # read in num_bytes bytes l times (normally 1 time) from cfile to target_ptr
        read = fread(<void*> target_ptr, num_bytes_t, l, self.cfile)

        if read == -1:
            raise IOError("num_read == -1")
        if read == 0:
            return None
        return target

    cpdef bytes readline(self, int limit=-1):
        """Reads a line from the stream.
         If limit is not -1, will only read up to `limit` bytes of the line.

        Arguments:
            limit (int): read only up to `limit` bytes of the line. Defaults to -1 (disabled).

        Returns:
            One line from the stream.
        """
        cdef char *line = NULL
        cdef size_t l = 0
        cdef ssize_t read

        read = getline(&line, &l, self.cfile)
        if read == -1:
            return None
        return line

    cpdef list readlines(self, int hint=-1):
        """Reads *all* lines from the stream and stores them in a list.
        If hint is not -1, will only read up to `hint` bytes altogether.

        Arguments:
            hint (int): read only up to `hint` bytes altogether. Defaults to -1 (disabled).

        Returns:
            All lines of the underlying stream in a list.
        """
        cdef char *line = NULL
        cdef size_t l = 0
        cdef ssize_t read
        cdef list lines = []
        cdef long num_bytes_read = 0

        while True:
            read = getline(&line, &l, self.cfile)
            if read == -1: break
            num_bytes_read += read
            if hint != -1 and num_bytes_read >= hint:
                return lines
            lines.append(line)

        return lines

    cpdef int readinto(self, object b):
        """Read up to len(b) bytes into bytearray b and return the number of bytes read.
        If the object is in non-blocking mode and no bytes are available, None is returned.
        """
        raise NotImplementedError

    def _iterate_file(self):
        """Iterate through the file line-by-line.

        Do not call directly, use with statement (see class docstring) or `for line in CReader(filepath)` instead.

        Returns:
            An iterator over the lines in the underlying stream.
        """
        cdef char *line = NULL
        cdef size_t l = 0
        cdef ssize_t read

        while True:
            read = getline(&line, &l, self.cfile)
            if read == -1:
                raise StopIteration
            yield line
