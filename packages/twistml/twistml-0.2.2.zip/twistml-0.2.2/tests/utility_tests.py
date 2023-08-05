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
from os import path
from time import time

testdir = path.join(path.dirname(path.abspath(__file__)), 'testfiles')

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
