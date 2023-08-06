"""
Unittests for tinymr.serialize
"""


import os
import pickle

import pytest

from tinysort import tools
import tinysort.io


def test_BaseSerializer_exceptions():

    slz = tinysort.io.BaseSerializer()
    with pytest.raises(NotImplementedError):
        slz.open(None, None)


def test_str2type():
    values = [
        ('1', 1),
        ('0', 0),
        ('01', '01'),
        ('1.23', 1.23),
        ('01.23', '01.23'),
        ('words.dot', 'words.dot'),
        ('hey look at me', 'hey look at me'),
        ('none', None),
        ('true', True),
        ('false', False)]

    for v, e in values:
        assert tinysort.io.str2type(v) == e


def test_pickle_roundtrip():
    data = [
        (1, 2),
        (3, 4)]

    serialized = list(tinysort.io.dump_pickle(data))
    for item in serialized:
        assert isinstance(item, bytes)

    for expected, actual in zip(data, tinysort.io.load_pickle(serialized)):
        assert expected == actual


def test_pickle_from_file(tmpdir):

    path = str(tmpdir.mkdir('test_pickle_from_file').join('data'))

    data = [
        (1, 2, None),
        (3, 4, tools.OrderableNone)]

    with open(path, 'wb+') as f:
        for line in tinysort.io.dump_pickle(data):
            f.write(line)

        f.seek(0)

        for e, a in zip(data, tinysort.io.load_pickle(f)):
            assert e == a


def test_text():
    data = [

        (1, 2, None),
        (3, 4, tools.OrderableNone)]

    expected = [
        '1\t2\tNone',
        '3\t4\tOrderableNone']

    for e, a in zip(expected, tinysort.io.dump_text(data)):
        assert e == a


def test_text_roundtrip(tmpdir):

    path = str(tmpdir.mkdir('test_text_roundtrip').join('data'))

    data = [
        (1, 2, None),
        (3, 4, tools.OrderableNone)]

    out = tinysort.io.dump_text(data)
    for e, a in zip(data, tinysort.io.load_text(out)):
        assert e == a

    with open(path, 'w+') as f:
        for line in tinysort.io.dump_text(data):
            f.write(line + os.linesep)

        f.seek(0)

        for e, a in zip(data, tinysort.io.load_text(f)):
            assert e == a


def test_from_Pickler(tmpdir):

    path = str(tmpdir.mkdir('test_from_Pickler').join('data'))

    data = [
        (1, 2),
        (3, tools.OrderableNone)]

    with open(path, 'wb') as f:
        for item in tinysort.io.dump_pickle(data):
            f.write(item)

    with open(path, 'rb') as f:
        loaded = list(tinysort.io.load_pickle(f))
        assert len(loaded) > 1
        for e, a in zip(data, loaded):
            assert e == a


def test_dump_load_json():

    data = [
        {'key1': 'value1', 'key2': 'value2'},
        {'key3': 'value3', 'key4': 'value4'}]

    actual = tinysort.io.dump_json(data)
    actual = tinysort.io.load_json(actual)

    for e, a in zip(data, actual):
        assert e == a


@pytest.mark.parametrize('cls', [
    tinysort.io.Pickle,
    tinysort.io.DelimitedText,
    tinysort.io.NewlineJSON
])
def test_serialization_classes(cls, tmpdir):

    path = str(tmpdir.mkdir('test_serialization_classes').join('data'))

    data = [
        (1, 2),
        (3, 4)]

    slz = cls()

    assert isinstance(pickle.loads(pickle.dumps(slz)), type(slz))
    assert repr(slz).startswith(slz.__class__.__name__)

    with slz.open(path, 'w') as dst:
        for obj in data:
            dst.write(obj)
    assert dst.closed

    with slz.open(path) as src:
        for e, a in zip(data, src):
            assert e == tuple(a)  # Some types produce list

    assert dst.closed

    if isinstance(cls, tinysort.io.Pickle):
        with pytest.raises(ValueError):
            slz.open(path, 'a')

    with slz.open(path) as f:
        assert tuple(next(f)) == data[0]  # Some types produce list

    with pytest.raises(ValueError):
        slz.open(None, mode='a')
