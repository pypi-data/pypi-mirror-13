"""
Tests that process a more significant amount of data.  Might need to only
run these on Travis if they start taking too long.
"""


import os
import random

import pytest

import tinysort


@pytest.mark.skipif(
    os.environ.get('TRAVIS', 'true').lower() == 'true',
    reason="Not running on Travis")
def test_lots_of_ints():

    values = list(range(1000000))
    random.shuffle(values)

    assert list(tinysort.stream2stream(values)) == list(range(1000000))
