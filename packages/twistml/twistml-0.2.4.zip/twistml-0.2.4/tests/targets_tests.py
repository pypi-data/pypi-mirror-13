r"""Unittests of the functions in the features subpackage.

:Author:
    Matthias Manhertz
:Copyright:
    (c) Matthias Manhertz 2015
:Licence:
    MIT
"""

from nose.tools import assert_equal, raises
from twistml.targets import StockCsvReader, get_daily_changes
from datetime import datetime
from os import path

testdir = path.join(path.dirname(path.abspath(__file__)), 'testfiles')


def test_stockcsvreader():
    r"""Test the StockCsvReader class"""

    filepath = path.join(testdir, 'test_csvreader.csv')
    csv = StockCsvReader(filepath, 6, 0)
    prices = csv.read()

    assert_equal(prices[datetime.strptime('2011-05-17', '%Y-%m-%d')], 12479.6)
    assert_equal(prices[datetime.strptime('2011-05-18', '%Y-%m-%d')], 12560.2)
    assert_equal(prices[datetime.strptime('2011-05-19', '%Y-%m-%d')], 12605.3)
    assert_equal(prices[datetime.strptime('2011-05-20', '%Y-%m-%d')], 12512.0)
    assert_equal(len(prices), 4)

    pass


def test_get_daily_changes():
    r"""Test the get_daily_changes() function."""

    prices = {}
    prices[datetime.strptime('2011-05-17', '%Y-%m-%d')] = 100
    prices[datetime.strptime('2011-05-18', '%Y-%m-%d')] = 110
    prices[datetime.strptime('2011-05-19', '%Y-%m-%d')] = 99
    changes = get_daily_changes(prices, '2011-05-01', '2011-05-30')
    print(changes)
    assert_equal(changes[datetime.strptime('2011-05-18', '%Y-%m-%d')], 10)
    assert_equal(changes[datetime.strptime('2011-05-19', '%Y-%m-%d')], -10)
    assert_equal(len(changes), 2)

    changes = get_daily_changes(prices, '2011-05-01', '2011-05-30',
                                return_classes=True)

    assert_equal(changes[datetime.strptime('2011-05-18', '%Y-%m-%d')], 1)
    assert_equal(changes[datetime.strptime('2011-05-19', '%Y-%m-%d')], 0)
    assert_equal(len(changes), 2)
    pass