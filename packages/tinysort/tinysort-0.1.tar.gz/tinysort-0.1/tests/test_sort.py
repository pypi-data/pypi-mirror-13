"""
Unittests for tinysort.tinysort
"""


import io
import itertools as it
import os

import pytest
import random
import six

import tinysort
import tinysort.io
from tinysort import tools
from tinysort import _sort


def test_delete_files(tmpdir):

    base = tmpdir.mkdir('test_delete_files')
    paths = [str(base.join(str(i))) for i in range(5)]

    for p in paths:
        assert not os.path.exists(p)
        with open(p, 'w') as f:
            pass
        assert os.path.exists(p)

    with tools.delete_files(*paths) as pths:
        for p in pths:
            assert os.path.exists(p)

    for p in pths:
        assert not os.path.exists(p)

    # Run it again to make sure we don't get an exception
    with tools.delete_files(*paths) as pths:
        pass


def test_batch_open(tmpdir):

    base = tmpdir.mkdir('test_delete_files')
    paths = [str(base.join(str(i))) for i in range(5)]

    for p in paths:
        assert not os.path.exists(p)

    with tools.batch_open(*paths, mode='w') as handles:
        if six.PY2:
            t = file
        else:
            t = io.IOBase
        for h in handles:
            assert isinstance(h, t)


def test_sort_into_files():

    # Use an odd number so one chunk only has 1 value
    values = tuple(range(9))

    results = _sort._stream2tempfiles(reversed(values), chunksize=2)
    assert len(results) == 5

    with tools.delete_files(*results) as paths:
        for p in paths:
            with tinysort.io.Pickle().open(p) as f:
                lines = [int(l) for l in list(f)]

                # Input values are reversed, so the odd chunk is 0, not 9
                if len(lines) == 1:
                    assert lines[0] == 0
                elif len(lines) == 2:
                    assert lines[0] + 1 == lines[1]

                else:
                    raise ValueError("Unexpected condition")


@pytest.fixture(scope='function')
def unsorted_files(tmpdir):

    """
    Returns a tuple where the first element is a list of temporary files
    containing unsorted data the the second is the serializer needed to
    read them.

        ([p1, p2, ...], tinysort.tinysort.io.Serializer())
    """

    base = tmpdir.mkdir('sort_files_into_files')

    values_210 = str(base.join('210'))
    values_543 = str(base.join('543'))
    values_765 = str(base.join('876'))
    values_98 = str(base.join('9'))
    paths = (values_210, values_543, values_765, values_98)
    slz = tinysort.io.Pickle()

    for p in paths:
        nums = os.path.basename(p)
        with slz.open(p, 'w') as f:
            for n in nums:
                n = int(n)
                f.write((n, n))

    return paths, slz


def test_sort_files(unsorted_files):
    paths, slz = unsorted_files
    result = list(tinysort.files2stream(*paths, reader=slz, key=lambda x: x[0]))
    print(result)
    assert result == [(i, i) for i in range(10)]


def test_required_parameters():

    """
    Python 2 has some restrictive function declaration syntax that we have to
    work around.  Make sure missing parameters raise the right exceptions.
    """

    with pytest.raises(TypeError):
        next(_sort._mergefiles2stream(*[]))

    with pytest.raises(TypeError):
        next(_sort.files2stream(*[]))


@pytest.mark.parametrize('values', [
    tuple(reversed(range(10))), iter(reversed(range(10)))])
def test_stream2stream(values):
    expected = list(range(10))
    assert list(tinysort.stream2stream(values)) == expected


def test_files2stream(unsorted_file, unsorted_file_values):

    infiles = [unsorted_file, unsorted_file, unsorted_file]

    srt = tinysort.files2stream(*infiles, reader=tinysort.io.Pickle())

    expected = sorted(it.chain(
        unsorted_file_values, unsorted_file_values, unsorted_file_values))
    assert len(expected) == 3 * len(unsorted_file_values)

    assert expected == list(srt)


def test_file2stream(unsorted_file, sorted_file_values):

    actual = list(tinysort.file2stream(
        unsorted_file, reader=tinysort.io.Pickle(), chunksize=2))
    assert actual == sorted_file_values


@pytest.mark.parametrize('memory', [True, False])
def test_stream2file(tmpdir, memory, unsorted_file_values, sorted_file_values):

    outfile = str(tmpdir.mkdir('test_stream2file').join('data'))
    slz = tinysort.io.Pickle()

    if memory:
        unsorted_file_values = iter(unsorted_file_values)

    result = tinysort.stream2file(
        unsorted_file_values,
        outfile,
        writer=slz,
        chunksize=2)

    assert result == outfile
    with slz.open(outfile) as f:
        assert sorted_file_values == list(f)


def test_file2file(tmpdir, unsorted_file, sorted_file_values):

    outfile = str(tmpdir.mkdir('test_file2file').join('data'))
    slz = tinysort.io.Pickle()

    result = tinysort.file2file(
        unsorted_file,
        outfile,
        reader=slz,
        writer=slz,
        chunksize=2)

    assert result == outfile

    with slz.open(outfile) as f:
        assert sorted_file_values == list(f)
