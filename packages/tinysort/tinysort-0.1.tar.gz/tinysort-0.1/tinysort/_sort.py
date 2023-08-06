"""
Sorters
=======

Each of the functions contained in this module take something that is unsorted
and sort it.  In some cases the sort happens entirely in-memory, but in most
cases the sort happens by by chunking the input stream into small pieces,
sorting each piece into its own file, and then doing a final merge sort.

With a reasonable `chunksize` the limitations to the amount of data that can be
sorted is available disk space for incidental I/O, and the amount of time the
caller is willing to wait.


**kwargs
--------

Some functions take a generic, undocumented `**kwargs`.  When not documented
this is `chunksize`, `jobs`, `key`, and `reverse`.
"""


import functools
import itertools as it
import logging
import tempfile

from tinysort import tools
import tinysort.io

from tinysort._backport_heapq import merge as heapq_merge


__all__ = [
    'file2file', 'file2stream', 'files2stream', 'stream2file', 'stream2stream']


logger = logging.getLogger('tinysort')


CHUNKSIZE = 100000
_PICKLE_IO = tinysort.io.Pickle()


def _mp_sort_into_tempfile(kwargs):

    """
    Used by `_stream2tempfiles()`.

    Parameters
    ----------
    kwargs : dict
        data : tuple
        writer : tinysort.io.BaseSerializer
        sort_args : dict
    """

    data = kwargs['data']
    writer = kwargs['writer']
    sort_args = kwargs['sort_args']
    _, tmp = tempfile.mkstemp()

    with writer.open(tmp, 'w') as f:
        for item in sorted(data, **sort_args):
            f.write(item)

    return tmp


def _stream2tempfiles(
        stream, jobs=1, chunksize=CHUNKSIZE, writer=_PICKLE_IO, **kwargs):

    """
    Sort a stream of data into temporary files.  Caller is responsible for
    deleting files.  Tempfile paths are generated with `tempfile.mkstemp()`.

    Parameters
    ----------
    stream : iter
        Input stream to sort.
    jobs : int, optional
        Sort data with a pool of N workers.
    chunksize : int, optional
        Process this many objects from the input stream in each job.  Also
        the maximum amount of objects per tempfile.
    writer : None or tinysort.io.BaseSerializer, optional
        Instance of the serializer for writing the stream to disk.
    kwargs : **kwargs, optional
        Keyword arguments for `sorted()`.

    Returns
    -------
    list
        Temporary file paths.
    """

    tasks = ({
        'data': data,
        'writer': writer,
        'sort_args': kwargs
    } for data in tools.slicer(stream, chunksize))

    with tools.runner(_mp_sort_into_tempfile, tasks, jobs) as run:
        return list(run)


def _file2tempfiles(infile, reader, **kwargs):

    """
    Sort the contents of a single file into a bunch of temporary files.  Mostly
    a convenience wrapper for `_stream2tempfiles()` to allow reading from a file
    on disk.

    Parameters
    ----------
    infile : str
        Input file to read.
    reader : tinysort.io.BaseSerializer
        Instance of the serializer for reading `infile`.
    kwargs : **kwargs
        Keyword arguments for `_stream2tempfiles()`.

    Returns
    -------
    See `_stream2tempfiles()`.
    """

    with reader.open(infile) as f:
        return _stream2tempfiles(f, **kwargs)


def _mergefiles2stream(*infiles, **kwargs):

    """
    Merge sort a bunch of tempfiles into a sorted stream of objects.  Tempfiles
    are not deleted.

    Parameters
    ----------
    infiles : str
        Input paths to merge sort.
    reader : tinysort.io.BaseSerializer
        Instance of the serializer for reading the `paths`.
    kwargs : **kwargs, optional
        Keyword arguments for `heapq.merge()`.

    Yields
    ------
    object
    """

    if 'reader' not in kwargs:
        raise TypeError("reader parameter is required.")
    else:
        reader = kwargs.pop('reader')

    with tools.batch_open(*infiles, opener=reader.open) as handles:
        for item in heapq_merge(*handles, **kwargs):
            yield item


def stream2stream(stream, serializer=_PICKLE_IO, jobs=1, **kwargs):

    """
    Take an unsorted stream of data and turn it into a sorted stream of data.
    Data is chunked into tempfiles with `_stream2tempfiles()`, and then merged
    with `_mergefiles2stream()`.  Intermediary tempfiles are written and read
    with `serializer` and are deleted automatically.

    Parameters
    ----------
    stream : iter
        Sort this stream of data.
    serializer : tinysort.io.BaseSerializer, optional
        Instance of the class to use for writing and reading intermediary
        tempfiles.
    jobs : int, optional
        Process data in parallel with a pool of N workers.  Passed to
        `_mergefiles2stream()`.
    kwargs : **kwargs, optional
        Keyword arguments for `_stream2tempfiles()`.  The `key` and
        `reverse` value are extracted for `_mergefiles2stream()` as well.
    
    Yields
    ------
    object
        Sorted objects.
    """

    # We know we already have the data in-memory, so just doing a straight up
    # sort is almost certainly faster
    if isinstance(stream, (list, tuple, dict)):
        for item in sorted(
                stream,
                key=kwargs.get('key'),
                reverse=kwargs.get('reverse', False)):
            yield item

    else:

        # Reader, writer, and serializer have different meanings from an API and
        # documentation perspective, so we don't want this to create an error.
        kwargs.update(writer=serializer)

        chunk_paths = _stream2tempfiles(
            stream,
            jobs=jobs,
            **kwargs)

        with tools.delete_files(*chunk_paths) as paths:
            for item in _mergefiles2stream(
                    *paths,
                    reader=serializer,
                    key=kwargs.get('key'),
                    reverse=kwargs.get('reverse', False)):
                yield item


def file2stream(infile, reader, **kwargs):
    
    """
    Convenience wrapper for `stream2stream()` for working with an input file
    on disk.
    
    Parameters
    ----------
    infile : str
        Sort this file.
    reader : tinysort.io.BaseSerializer
        Instance of the serializer for reading `infile`.
    kwargs : **kwargs, optional
        Keyword arguments for `stream2stream()`.

    Yields
    ------
    See `stream2stream()`.
    """

    with reader.open(infile) as src:
        for item in stream2stream(src, **kwargs):
            yield item


def files2stream(*infiles, **kwargs):

    """
    Sort a batch of files into a single stream.

    Parameters
    ----------
    paths : *str
        Input files to sort.
    reader : tinysort.io.BaseSerializer
        Instance of the serializer for reading `infile`.
    kwargs : **kwargs, optional
        Keyword arguments for `file2stream()`.

    Yields
    ------
    object
    """

    if 'reader' not in kwargs:
        raise TypeError("reader parameter is required")
    else:
        reader = kwargs.pop('reader')

    tfiles = []
    try:
        srt = functools.partial(_file2tempfiles, reader=reader, **kwargs)
        tfiles += list(it.chain(*map(srt, infiles)))
    finally:
        with tools.delete_files(*tfiles) as merge:
            for item in _mergefiles2stream(
                    *merge,
                    reader=reader,
                    key=kwargs.get('key'),
                    reverse=kwargs.get('reverse', False)):
                yield item


def stream2file(stream, outfile, writer, **kwargs):

    """
    Convenience wrapper for `stream2stream()` for writing to a file on disk.

    Parameters
    ----------
    stream : iter
        Sort this stream of data.
    outfile : str
        Write sorted data to a file at this path.  Will be overwritten if it
        already exists.
    writer : tinysort.io.BaseSerializer
        Instance of the serializer for writing `outfile`.
    kwargs : **kwargs
        Keyword arguments for `stream2stream`.

    Returns
    -------
    str
        `outfile`
    """

    with writer.open(outfile, 'w') as dst:

        # We already have everything in-memory so this is faster
        if isinstance(stream, (list, tuple, dict)):
            sorted_data = sorted(
                stream,
                key=kwargs.get('key'),
                reverse=kwargs.get('reverse', False))

        else:
            sorted_data = stream2stream(stream, **kwargs)

        for item in sorted_data:
            dst.write(item)

    return outfile


def file2file(infile, outfile, reader, writer, **kwargs):

    """
    A _super_ convenient wrapper for reading a file on disk and writing to a
    file on disk.

    Parameters
    ----------
    infile : str
        Path to input file.
    outfile : str
        Path to output file.  Will be overwritten if it already exists.
    reader : tinysort.io.BaseSerializer
        Instance of the serializer for reading `infile`.
    writer : tinysort.io.BaseSerializer
        Instance of the serializer for writing `outfile`.
    kwargs : **kwargs, optional
        Keyword arguments for `file2stream()`.

    Returns
    -------
    str
        `outfile`
    """

    with writer.open(outfile, 'w') as dst:
        for item in file2stream(infile, reader=reader, **kwargs):
            dst.write(item)

    return outfile
