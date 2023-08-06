r"""Unittests of the functions in the utility subpackage.

:Author:
    Matthias Manhertz
:Copyright:
    (c) Matthias Manhertz 2015
:Licence:
    MIT
"""

from nose.tools import assert_equal, raises
from twistml.utility import generate_datesequence
from twistml.utility import find_files
from twistml.utility import progress_report
from twistml.utility import remap
from twistml.utility import create_toy_data
from twistml.utility import float_ceil, float_floor
from twistml.utility import multi_group_bar_chart
from os import path, remove, rmdir, listdir, makedirs
from time import time
from datetime import datetime
import json
import numpy as np
import matplotlib

testdir = path.join(path.dirname(path.abspath(__file__)), 'testfiles')
tempdir = path.join(testdir, 'temp')

def setup():
    if not path.exists(tempdir):
        makedirs(tempdir)
    pass


def teardown():
    if not listdir(tempdir):
        rmdir(tempdir)

def test_generate_datesequence():
    r"""Test the 'normal' usecase."""
    assert_equal(generate_datesequence('2015-12-16','2015-12-19'),
                 ['2015-12-16','2015-12-17','2015-12-18','2015-12-19'])
    pass

def test_generate_datesquence_informat():
    r"""Test datesequence with different informat."""
    assert_equal(generate_datesequence('16.12.2015','19.12.2015',
                                       informat='%d.%m.%Y'),
                 ['2015-12-16','2015-12-17','2015-12-18','2015-12-19'])
    pass

def test_generate_datesquence_outformat():
    r"""Test datesequence with different outformat."""
    assert_equal(generate_datesequence('2015-12-16','2015-12-19',
                                       outformat='%d.%m.%Y'),
                 ['16.12.2015','17.12.2015','18.12.2015','19.12.2015'])
    pass

def test_generate_datesquence_single_day():
    r"""Test datesequence for one day."""
    assert_equal(generate_datesequence('2015-12-16','2015-12-16'),
                 ['2015-12-16'])
    pass

def test_generate_datesquence_wrong_order():
    r"""Test datesequence for one day."""
    assert_equal(generate_datesequence('2015-12-19','2015-12-16'), [])
    pass

def test_find_files_in_daterange():
    r"""Test find_files_in_daterange."""
    files = find_files(testdir, fromdate='2015-01-01', todate='2015-01-31',
                       filenameformat='test-%Y-%m-%d.txt')
    assert_equal(len(files), 4)

    files = find_files(testdir, fromdate='2014-01-01', todate='2015-12-31',
                       filenameformat='test-%Y-%m-%d.txt')
    assert_equal(len(files), 6)

    pass

def test_find_files_in_subdirs():
    r"""Test _find_files_in_daterange_insubdirs"""
    files = find_files(testdir, fromdate='2015-01-01', todate='2015-01-31',
                       filenameformat='test-%Y-%m-%d.txt', subdirs=True)
    assert_equal(len(files), 12)

    files = find_files(testdir, fromdate='2014-01-01', todate='2015-12-31',
                       filenameformat='test-%Y-%m-%d.txt', subdirs=True)
    assert_equal(len(files), 18)

def test_progress_report():
    r"""Test that prgress_report() returns a string."""
    assert isinstance(progress_report(time(), 5, 5), str)

def test_remap():
    r""" Assert that remap correctly scales values."""
    assert_equal(remap(0.5, -1, 1), 0.75)
    assert_equal(remap(75, 0, 100, 100, 200), 175)
    assert_equal(remap(-1, -1, 1, 0, 2), 0)
    assert_equal(remap(1, -1, 1, 15, 64), 64)
    pass

@raises(ValueError)
def test_remap_outside_interval():
    a = remap(-5, -1, 1)
    pass

@raises(ValueError)
def test_remap_illegal_interval():
    a = remap(1, 1, -1)
    pass

def test_create_toy_data():
    r"""Assert that create toy data creates the right amount of tweets."""

    tweets_per_target = 10
    targets = {datetime.strptime('2013-01-10', '%Y-%m-%d'): 0.2,
               datetime.strptime('2013-01-12', '%Y-%m-%d'): 0.8,}
    keywords = ['the dow', 'the DJI', 'the stock market', 'stocks',
                'the market', 'wall street', 'stock indices', 'market indexes']

    filepaths = listdir(tempdir)
    for filepath in filepaths:
        remove(path.join(tempdir,filepath))

    toy_data = create_toy_data(targets, tempdir, keywords, tweets_per_target)

    count = 0
    filepaths = listdir(tempdir)
    for filepath in filepaths:
        with open(path.join(tempdir,filepath)) as f:
            tweets = json.load(f)
            count += len(tweets)
        remove(path.join(tempdir,filepath))

    assert_equal(count, len(targets) * tweets_per_target)

def test_float_floor():
    r"""Assert that float_floor() works correctly."""
    assert_equal(float_floor(0.12345), 0.0)
    assert_equal(float_floor(0.12345,1), 0.1)
    assert_equal(float_floor(0.12345,2), 0.12)
    assert_equal(float_floor(0.12345,3), 0.123)
    assert_equal(float_floor(0.12345,9), 0.12345)

def test_float_ceil():
    r"""Assert that float_floor() works correctly."""
    assert_equal(float_ceil(0.12345), 1.0)
    assert_equal(float_ceil(0.12345,1), 0.2)
    assert_equal(float_ceil(0.12345,2), 0.13)
    assert_equal(float_ceil(0.12345,3), 0.124)
    assert_equal(float_ceil(0.12345,9), 0.12345)

def test_multi_group_bar_chart():
    r"""Assert that multi_group_bar_chart returns a matplotlib.figure."""

    settings = ['Set1', 'Set2', 'Set3']
    sources = ['SVC', 'KNN']
    data = np.random.rand(len(settings), len(sources))
    erros = np.random.rand(len(settings), len(sources))
    fig = multi_group_bar_chart(data, erros, settings, sources, 'Settings',
                                'Results', 'A Test Figure')
    assert isinstance(fig, matplotlib.figure.Figure)