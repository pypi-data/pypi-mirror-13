r"""Contains functions to extract useful target vectors from raw stock
    data .csv files.

    <extended summary>

    <routine listings>

    <see also>

    <notes>

    <references>

    <examples>

:Author:
    Matthias Manhertz
:Copyright:
    (c) Matthias Manhertz 2015
:Licence:
    MIT
"""

import csv
from datetime import datetime, timedelta
from ..utility.utility import generate_datesequence


class StockCsvReader():
    r"""Reads daily stock prices from a .csv file."""

    def __init__(self, filepath, pricecolumn, datecolumn,
                 dateformat='%Y-%m-%d', delimiter=','):
        r"""Initialize the reader with details about the .csv file.

        Parameters
        ----------
        filepath : str
            Full path to the .csv file containing the stock data.
        pricecolumn : int
            The column index of the closing price column within the
            .csv file.
        datecolumn : int
            The column index of the date stamp column within the .csv
            file.
        dateformat : str, optional
            The dateformat as used by datetime.strftime and
            datetime.strptime. (See python documentation for details.)
            (Default is '%Y-%m-%d', which is used by for example in
            .csv files of daily stock prices downloaded from
            dukascopy.com.)
        delimiter : str, optional
            The delimiter between two entries in the .csv. (Default is
            ',')

        """

        self.filepath = filepath
        self.pricecolumn = pricecolumn
        self.datecolumn = datecolumn
        self.dateformat = dateformat
        self.delimiter = delimiter
        pass

    def read(self):
        r"""Reads the .csv file an returns a dict mapping stock price
            to datetime.

            Returns
            -------
            dict[datetime,float]
                A dictionary where the datetime stamps from the .csv
                file are the keys and the corresponding stock prices
                are the values.

        """

        daily_prices = {}

        with open(self.filepath, 'rb') as csvfile:
            stockreader = csv.reader(csvfile, delimiter=self.delimiter)
            stockreader.next()  # skip headings
            for row in stockreader:
                date = datetime.strptime(row[self.datecolumn], self.dateformat)
                price = float(row[self.pricecolumn])
                daily_prices[date] = price

        return daily_prices


def get_daily_changes(prices, fromdate, todate,
                      dateformat='%Y-%m-%d', return_classes=False,
                      ignore_neutral_days=True, logger=None):
    r"""Returns the relative change for each date in a range.

        <Extended Summary>

        Parameters
        ----------
        prices : dict[datetime, float]
            A dictionary that has datetime stamps as keys and the stock
            prices as values. (Can be generated from a .csv file using
            the StockCsvReader class.)
        fromdate : str
            Start of the daterange for which to get the stock prize
            changes as a string in `dateformat`.
        todate : str
            End of the daterange for which to get the stock prize
            changes as a string in `dateformat`.
        dateformat : str, optional
            The dateformat as used by datetime.strftime and
            datetime.strptime. (See python documentation for details.)
        return_classes : bool, optional
            If True, the returned changes will be 1 for days with
            positive price change and -1 for days with negative price
            change, instead of continous values. (If
            `ignore_neutral_days` is False 0 will be returned for days
            without price change.) (default is False)
        ignore_neutral_days : bool, optional
            Days that have no change in stock price are treated as
            nonexistant. This almost exclusively removes weekends and
            bank holidays, but may on occasion remove a legitimate
            datapoint. (default is True)
        logger : logging.Logger, optional
            A logger object, used to display / log console output
            (default is None, which implies quiet execution).

        Returns
        -------
        daily_changes : dict[datetime, float]
            A dictionary mapping the percentage change in stockprice
            to a datetime. This does not include dates for which no
            change can be computed (either because the date itself or
            the day before are not part of the `prices` dict).

        <Notes>

        <References>

        <Examples>
    """

    daily_changes = {}
    for today in generate_datesequence(fromdate, todate, outformat=None):
        yesterday = _day_before(today)
        if today in prices and yesterday in prices:
            change = prices[today] - prices[yesterday]
            if ignore_neutral_days and change == 0:
                continue
            if return_classes:
                # 0 for negative / 1 for positive
                if change <= 0:
                    daily_changes[today] = 0
                else:
                    daily_changes[today] = 1
            else:
                daily_changes[today] = change/float(prices[yesterday])*100
    return daily_changes


def _day_before(day):
    r"""Returns a datetime stamp that is one day before the given one."""

    return day - timedelta(days=1)
