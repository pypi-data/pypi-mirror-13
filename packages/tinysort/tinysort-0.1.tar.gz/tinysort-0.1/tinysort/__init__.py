"""
tinysort
========

Sort stuff.  Big stuff, little stuff, any stuff!


Scope
-----

This package aims to provide the tools necessary for quickly and easily sorting
large amounts of arbitrary Python objects, where "large" is an amount of data
that is larger than available RAM but smaller than available disk.  The
defaults expect at least hundreds of thousands of things and work well into
millions of things, but further optimizations are possible.  A SSD is
recommended as large streams of data will incur a merge sort across a very large
number of intermediary temp files.


How does it work?
-----------------

`tinysort` sorts arbitrarily large streams of data by breaking off small pieces,
sorting them in memory, and serializing them to intermediary tempfiles.  These
files are then merge sorted together with `heapq.merge()`.


Optimizations
-------------

Aside from sorting in parallel, the primary paths for optimization are tweaking
the `chunksize`, and the data serialization formats.  The `chunksize` is the
maximum number of objects that are read into memory and sorted for each job, and
is the maximum number of objects that are written to each tempfile.  It is very
advantageous to make this value as large as possible to limit both the number of
tempfiles arriving at the merge sort phase and the number of `pickle` operations
associated with `multiprocessing`.  Larger chunks means fewer jobs.

Custom data serialization formats can provide a boost because they know more
about the data they are responsible for handling.  For instance, if the user
knows they are dealing with data that contains a `datetime.datetime()` object,
they may be able to beat `pickle` by writing their own serializer that writes
the `datetime.datetime()` object as a unix timestamp, which is about twice as
fast as `pickle` according to some back-of-the-envelope calculations using
`timeit.

Emulate a writing a `datetime.datetime()` object as a unix timestamp cast to
a string on disk and then cast to a float on read.

    $ python -m timeit \
        -s "import datetime" \
        -s "ts = (datetime.datetime.now() - datetime.datetime(1970, 1, 1)).total_seconds()" \
        "datetime.datetime.fromtimestamp(float(str(ts)))"
    100000 loops, best of 3: 2.62 usec per loop

Emulate writing and reading with `pickle`:

    $ python -m timeit \
        -s "import pickle" \
        -s "import datetime" \
        -s "ts = datetime.datetime.now()" \
        "pickle.loads(pickle.dumps(ts))"
    100000 loops, best of 3: 5.48 usec per loop


Limitations
-----------

Aside from disk size limitations, the primary hurdle is serializing the data to
disk in intermediary tempfiles.  By default `pickle` is used as it provides a
method for serializing _most_ objects, but in some cases performance can be
improved by picking a different format or writing a custom format. The same
rules apply for `reader` and `writer` parameters.

This library relies on the builtin `sorted()` function, which is reliable, but
not necessarily the the fastest algorithm depending on the data's structure.
tinysort could allow for access to different algorithms in the future.


Python 3 vs. 2
--------------

This module uses `heapq.merge()` extensively, which normally does not accept
a `key` argument when running in Python 2.  This package includes a copy of the
Python 3 `heapq` source code, with some slight modifications for compatibility
with Python 2, and can be found in `tinysort._backport_heapq`.  This code
retains its original license.

In Python 2 the builtin `sorted()` function is much more forgiving of
unorderable types than Python 3 at the expensive of a degree of ambiguity in the
output.  This package does not attempt to match Python 3's exception in Python
2, but the `tinysort.tools.OrderableNone` and `tinysort.tools.Orderable()` may
help bridge the gap.
"""


from tinysort._sort import *

import logging
logging.basicConfig()


__all__ = [
    'file2file', 'file2stream', 'files2stream', 'stream2file', 'stream2stream']


__version__ = '0.1'
__author__ = 'Kevin Wurster'
__email__ = 'wursterk@gmail.com'
__source__ = 'https://github.com/geowurster/tinysort'
__license__ = '''
Copyright (c) 2016, Kevin Wurster
All rights reserved.

Redistribution and use in source and binary forms, with or without
modification, are permitted provided that the following conditions are met:

* Redistributions of source code must retain the above copyright notice, this
  list of conditions and the following disclaimer.

* Redistributions in binary form must reproduce the above copyright notice,
  this list of conditions and the following disclaimer in the documentation
  and/or other materials provided with the distribution.

* Neither the name of tinysort nor the names of its
  contributors may be used to endorse or promote products derived from
  this software without specific prior written permission.

THIS SOFTWARE IS PROVIDED BY THE COPYRIGHT HOLDERS AND CONTRIBUTORS "AS IS"
AND ANY EXPRESS OR IMPLIED WARRANTIES, INCLUDING, BUT NOT LIMITED TO, THE
IMPLIED WARRANTIES OF MERCHANTABILITY AND FITNESS FOR A PARTICULAR PURPOSE ARE
DISCLAIMED. IN NO EVENT SHALL THE COPYRIGHT HOLDER OR CONTRIBUTORS BE LIABLE
FOR ANY DIRECT, INDIRECT, INCIDENTAL, SPECIAL, EXEMPLARY, OR CONSEQUENTIAL
DAMAGES (INCLUDING, BUT NOT LIMITED TO, PROCUREMENT OF SUBSTITUTE GOODS OR
SERVICES; LOSS OF USE, DATA, OR PROFITS; OR BUSINESS INTERRUPTION) HOWEVER
CAUSED AND ON ANY THEORY OF LIABILITY, WHETHER IN CONTRACT, STRICT LIABILITY,
OR TORT (INCLUDING NEGLIGENCE OR OTHERWISE) ARISING IN ANY WAY OUT OF THE USE
OF THIS SOFTWARE, EVEN IF ADVISED OF THE POSSIBILITY OF SUCH DAMAGE.
'''
