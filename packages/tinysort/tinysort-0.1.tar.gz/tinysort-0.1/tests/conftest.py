"""
Test fixtures
"""


from collections import OrderedDict
import os
import pickle
import random

import pytest


@pytest.fixture(scope='function')
def tiny_text():
    return os.linesep.join([
        "word something else",
        "else something word",
        "mr python could be cool 1"
    ])


@pytest.fixture(scope='function')
def tiny_text_wc_output():
    return OrderedDict((
        ('1', 1),
        ('be', 1),
        ('cool', 1),
        ('could', 1),
        ('else', 2),
        ('mr', 1),
        ('python', 1),
        ('something', 2),
        ('word', 2),
    ))


@pytest.fixture(scope='function')
def mr_wordcount_memory_no_sort():

    class WordCount(mr.memory.MemMapReduce):

        def mapper(self, item):
            for word in item.split():
                yield word, 1

        def reducer(self, key, values):
            yield key, sum(values)

        def output(self, pairs):
            return {k: tuple(v)[0] for k, v in pairs}

    return WordCount


@pytest.fixture(scope='function')
def linecount_file(tmpdir):

    """
    Return a function that copies the license and writes it to a tempfile.
    Can optionally change the `linesep` character.
    """

    def _linecount_file(linesep=os.linesep):
        path = str(tmpdir.mkdir('test').join('count-lines.txt'))
        with open('LICENSE.txt') as src, open(path, 'w') as dst:
            for line in src:
                dst.write(line.strip() + linesep)
        return path
    return _linecount_file


@pytest.fixture(scope='function')
def sorted_file(tmpdir):

    outfile = str(tmpdir.mkdir('sorted_file').join('sorted_file'))

    with open(outfile, 'wb') as f:
        pickler = pickle.Pickler(f)
        for value in range(10):
            pickler.dump(value)

    return outfile


@pytest.fixture(scope='function')
def unsorted_file(tmpdir):

    outfile = str(tmpdir.mkdir('unsorted_file').join('unsorted_file'))

    values = list(range(10))
    random.shuffle(values)

    with open(outfile, 'wb') as f:
        pickler = pickle.Pickler(f)
        for v in values:
            pickler.dump(v)

    return outfile


@pytest.fixture(scope='function')
def sorted_file_values(sorted_file):
    out = []
    with open(sorted_file, 'rb') as f:
        unpickler = pickle.Unpickler(f)
        while True:
            try:
                out.append(unpickler.load())
            except EOFError:
                break
    return out


@pytest.fixture(scope='function')
def unsorted_file_values(unsorted_file):
    out = []
    with open(unsorted_file, 'rb') as f:
        unpickler = pickle.Unpickler(f)
        while True:
            try:
                out.append(unpickler.load())
            except EOFError:
                break
    return out
