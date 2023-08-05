README
======

Dinopy - DNA input and output for python
----------------------------------------

Dinopy's goal is to make files containing biological sequences easily
and efficiently accessible for python programmers, allowing them to
focus on their application instead of file-io.

::

    #!python

    import dinopy
    fq_reader = dinopy.FastqReader("reads.fastq")
    for sequence, name, quality in fq_reader.reads(quality_values=True):
        if some_function(quality):
            analyze(seq)

Features
~~~~~~~~

-  Easy to use reader and writer for FASTA- and FASTQ-files.
-  Specifiable data type and representation for return values (bytes,
   strings and integers see
   `dtype <https://dinopy.readthedocs.org/en/latest/encoding/>`__ for
   more information).
-  Works directly on gzipped files.
-  Iterators for q-grams of a sequence (also allowing shaped q-grams).
-  (Reverse) complement.
-  Chromosome selection from FASTA files.
-  Implemented in `Cython <http://cython.org/>`__ for additional
   speedup.

Getting Started
~~~~~~~~~~~~~~~

-  If you are new to dinopy you can get started by following the
   first-steps
   `tutorial <https://dinopy.readthedocs.org/en/latest/getting-started/introduction/>`__.
-  A full list of features, as well as the documentation, can be found
   `here <https://dinopy.readthedocs.org/en/latest/>`__.

Installation
~~~~~~~~~~~~

Dinopy can be installed with pip:

   ::

       $ pip install dinopy

or with conda:

   ::

       $ conda install -c HenningTimm dinopy

Additionally, dinopy can be downloaded from Bitbucket and compiled using its
setup.py:

1. Download source code from
   `bitbucket <https://bitbucket.org/HenningTimm/dinopy>`__.
2. Install globally:

   ::

       $ python setup.py install

   or only for the current user:

   ::

       $ python setup.py install --user

3. Use dinopy:

   ::

       $ python

       >>> import dinopy

System requirements
~~~~~~~~~~~~~~~~~~~

-  `python <https://www.python.org/>`__ >= 3.3
-  `cython <http://cython.org/>`__ >= 0.20
-  `numpy <http://www.numpy.org/>`__ >= 1.7

We recommend using
`anaconda <https://store.continuum.io/cshop/anaconda/>`__:

::

    $ conda create -n dinopy python cython numpy

Platform support
~~~~~~~~~~~~~~~~

Dinopy has been tested on Ubuntu, Arch Linux and OS X (Yosemite and El
Capitan).

We do not officially support Windows - dinopy will probably work, but
there might be problems due to different linebreak styles; we assume
``\n`` as separator but the probability to encounter files with ``\r\n``
as line-separator might be higher on Windows.

Planned features
~~~~~~~~~~~~~~~~

-  SAM-reader / -writer
-  quality-trimming for FASTQ-reader
-  GFF-reader

License
~~~~~~~

Dinopy is Open Source and licensed under the `MIT
License <http://opensource.org/licenses/MIT>`__.
