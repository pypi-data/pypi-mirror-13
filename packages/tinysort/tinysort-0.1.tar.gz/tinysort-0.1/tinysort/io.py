"""
Data serialization and de-serialization.

All of the sorting functions writer to intermediary tempfiles, so we have to
be able to read/write arbitrary Python objects.  By default `pickle` is used,
but brewing your own custom format can provide a performance boost.

The subclasses of `BaseSerializer()` provide the interface needed by the sort
functions to read and/or write data on disk.  The sort functions accept
instances of these classes through one or more of the following keyword
arguments:

* `reader` - Format for reading data from disk.
* `writer` - Format for writing data to disk.
* `serializer` - Format for writing to and reading from intermediary tempfiles.

We allow each of these as a separate argument for better optimization, and to
account for serializers that may not support reading and writing.

This module also contains a few functions for working with streams of data.
"""


import pickle
import functools
import json
import os

from tinysort import tools


def str2type(string):

    """
    Convert a string to its native Python type.
    """

    # String might be an integer
    if string.isdigit():

        # Don't convert strings with leading 0's to an int - they probably aren't ints
        if len(string) == 1 or (string[0] != '0' and len(string) > 1):
            return int(string)
        else:
            return string

    # String might be a float
    elif '.' in string:

        # But not if it starts with a 0
        if len(string) > 1 and string[0] != '0':
            try:
                return float(string)
            except ValueError:
                return string
        else:
            return string

    else:

        # None, True, or False?
        string_lower = string.lower()
        if string_lower == 'none':
            return None
        elif string_lower == 'true':
            return True
        elif string_lower == 'false':
            return False
        elif string_lower == 'orderablenone':
            return tools.OrderableNone

        # It's really just a string
        else:
            return string


def dump_pickle(stream, *args, **kwargs):

    """
    Pickle a stream of data one item at a time.  Primarily used to serialize
    keys.

    Parameters
    ----------
    stream : iter
        Data to process.  Usually tuples.
    args : *args, optional
        *args for `pickle.dumps()`.
    kwargs : **kwargs, optional
        **kwargs for `pickle.dumps()`.

    Yields
    ------
    str
    """

    for key in stream:
        yield pickle.dumps(key, *args, **kwargs)


def load_pickle(stream, **kwargs):

    """
    Unpickle a file or stream of data.  Primarily used to de-serialize keys.

    Parameters
    ----------
    stream : file or iter
        If a `file` is given it is un-pickled with `pickle.Unpickler()`.  If
        an iterator is given each item is passed through `pickle.loads()`.
    kwargs : **kwargs, optional
        Not used - included to homogenize the serialization API.

    Yields
    ------
    object
    """

    if hasattr(stream, 'read') and 'b' in getattr(stream, 'mode', ''):
        up = pickle.Unpickler(stream)
        while True:
            try:
                yield up.load()
            except EOFError:
                break
    else:
        for key in stream:
            yield pickle.loads(key)


def dump_text(stream, delimiter='\t', serializer=str):

    """
    Convert keys to delimited text.

        >>> from tinysort.io import dump_text
        >>> keys = [
        ...     ('partition', 'sort', 'data')
        ...     (1, 1.23, None)]
        >>> print(list(dump_text(keys)))
        [
            'partition\tsort\tdata\t',
            '1\t1.23\tNone'
        ]

    Parameters
    ----------
    stream : iter
        One set of keys per iteration.
    delimiter : str, optional
        Output text delimiter.
    serializer : function, optional
        Function to serialize each key to a string.

    Yields
    ------
    str
    """

    for keys in stream:
        yield delimiter.join((serializer(k) for k in keys))


def load_text(stream, delimiter='\t', deserializer=str2type):

    """
    Parse delimited text to a stream of key tuples.

        >>> import os
        >>> from tinysort.io import load_text
        >>> text = os.linesep.join([
        ...     'partition\tsort\tdata\t',
        ...     '1\t1.23\tNone'])
        >>> keys = [
        ...     ('partition', 'sort', 'data')
        ...     (1, 1.23, None)]
        >>> print(list(load_text(text)))
        [
            ('partition', 'sort', 'data',
            ('1', '1.23', None)
        ]

    Parameters
    ----------
    stream
    """

    for line in stream:
        yield tuple((deserializer(k) for k in line.strip().split(delimiter)))


def load_json(stream, json_lib=json, **kwargs):

    """
    Load a series of JSON encoded strings.

    Parameters
    ----------
    stream : iter
        Strings to load.
    json_lib : module, optional
        JSON library to use for loading.  Must match the builtin `json`
        module's API.
    kwargs : **kwargs, optional
        Arguments for `json.loads()`.

    Yields
    ------
    dict or list
    """

    for item in stream:
        yield json_lib.loads(item, **kwargs)


def dump_json(stream, json_lib=json, **kwargs):

    """
    Dump objects to JSON.

    Parameters
    ----------
    stream : iter
        JSON encodable objects.
    json_lib : module, optional
        JSON library to use for loading.  Must match the builtin `json`
        module's API.
    kwargs : **kwargs, optional
        Arguments for `json.dumps()`.

    Yields
    ------
    str
    """

    for item in stream:
        yield json_lib.dumps(item, **kwargs)


class BaseSerializer(object):

    """
    Base class for creating data serialization formats.
    """

    def __repr__(self):
        return "{}()".format(self.__class__.__name__)

    def open(self, f, mode='r', *kwargs):

        """
        Open a file for reading or writing.  Resulting object is responsible
        for serializing and de-serializing data.
        """

        raise NotImplementedError


class PickleReader(object):

    """
    A more Pythonic file-like interface to `pickle.Unpickler()`.

    Limited to:

        >>> with open('data.pickle') as f, PickleReader(f) as reader:
        ...     for obj in reader:
        ...         # Do stuff
    """

    def __init__(self, f, **kwargs):
        self._f = f
        self._unpickler = pickle.Unpickler(self._f, **kwargs)
        self._iterator = self._iter_reader()

    def __iter__(self):
        return self._iterator

    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        self.close()

    def __del__(self):
        self.close()

    def __next__(self):
        return next(self._iterator)

    next = __next__

    def close(self):
        return self._f.close()

    @property
    def closed(self):
        return self._f.closed

    def _iter_reader(self):
        while True:
            try:
                yield self._unpickler.load()
            except EOFError:
                raise StopIteration


class PickleWriter(object):

    """
    A file-like interface for `pickle.Pickler()`.  Intended for use with the
    `Pickle()` serializer.  Primarily exists to give `pickle.Pickler()` a
    `write()` method.

        >>> with open('data.pickle', 'wb') as f, PickleWriter(f) as writer:
        ...     for obj in stream:
        ...         writer.write(obj)
    """

    def __init__(self, f, **kwargs):
        self._f = f
        self._pickler = pickle.Pickler(self._f, **kwargs)

    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        self.close()

    def __del__(self):
        self.close()

    def close(self):
        self._f.close()

    def write(self, obj):
        self._pickler.dump(obj)

    @property
    def closed(self):
        return self._f.closed


class Pickle(BaseSerializer):

    def __init__(self, **kwargs):
        self._kwargs = kwargs

    def open(self, path, mode='r', **kwargs):
        if mode == 'r':
            mode = 'rb'
            cls = PickleReader
        elif mode == 'w':
            mode = 'wb'
            cls = PickleWriter
        else:
            raise ValueError("Mode {} is not supported".format(mode))

        f = open(path, mode=mode, **kwargs)

        return cls(f, **self._kwargs)


class DelimTextReader(object):

    def __init__(self, f, **kwargs):
        self._f = f
        self._iterator = load_text(self._f, **kwargs)

    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        self.close()

    def __del__(self):
        self.close()

    def __iter__(self):
        return self._iterator

    def __next__(self):
        return next(self._iterator)

    next = __next__

    def close(self):
        return self._f.close()

    @property
    def closed(self):
        return self._f.closed


class DelimTextWriter(object):

    def __init__(self, f, **kwargs):

        self._f = f
        self._kwargs = kwargs
        self._serialize = functools.partial(dump_text, **kwargs)

    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        self.close()

    def __del__(self):
        self.close()

    def close(self):
        return self._f.close()

    def write(self, obj):
        self._f.write(next(self._serialize([obj])) + os.linesep)

    @property
    def closed(self):
        return self._f.closed


class DelimitedText(BaseSerializer):

    """
    Read and write delimited text.
    """

    def __init__(self, **kwargs):
        self._kwargs = kwargs

    def open(self, path, mode='r', **kwargs):
        if mode == 'r':
            cls = DelimTextReader
        elif mode == 'w':
            cls = DelimTextWriter
        else:
            raise ValueError("Mode {} is not supported".format(mode))

        f = open(path, mode=mode, **kwargs)

        return cls(f, **self._kwargs)


class NewlineJSON(BaseSerializer):

    """
    Read and write newline delimited JSON with the `newlinejson` module.
    """

    def __init__(self, **kwargs):

        """
        Parameters
        ----------
        kwargs : **kwargs
            Keyword arguments for `newlinejson.open()`.
        """

        self._kwargs = kwargs

    def open(self, f, mode='r', **kwargs):

        """
        See `newlinejson.open()`.

        The `kwargs` here override the arguments from `__init__`.
        """

        if mode not in ('r', 'w'):
            raise ValueError("Mode {} is not supported".format(mode))

        try:
            import newlinejson as nlj
        except ImportError:
            raise ImportError(
                "Please 'pip install newlinejosn'.  This is an optional "
                "dependency, but is required for the NewlineJSON() serializer.")
        kw = dict(self._kwargs.items(), **kwargs)
        return nlj.open(f, mode=mode, **kw)
