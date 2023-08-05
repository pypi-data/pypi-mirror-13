r"""Unittests of the functions in the utility module.

:Author:
    Matthias Manhertz
:Copyright:
    (c) Matthias Manhertz 2015
:Licence:
    MIT
"""

from nose.tools import assert_equal
from twistml.utility import generate_datesequence
from twistml.utility import find_files_in_daterange
from twistml.utility import setup_logger
from os import path

testdir = path.dirname(path.abspath(__file__)) + '\\testfiles\\'

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
    files = find_files_in_daterange('2015-01-01', '2015-01-31', testdir,
                                    filenameformat='test-%Y-%m-%d.txt')
    assert_equal(len(files), 4)

    files = find_files_in_daterange('2014-01-01', '2015-12-31', testdir,
                                    filenameformat='test-%Y-%m-%d.txt')
    assert_equal(len(files), 6)

    pass


if __name__ == '__main__':
    main()
