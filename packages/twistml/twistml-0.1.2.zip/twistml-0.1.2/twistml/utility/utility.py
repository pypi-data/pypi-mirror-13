r"""Provides some internal utility functions for the twistml package

:Author:
    Matthias Manhertz
:Copyright:
    (c) Matthias Manhertz 2015
:Licence:
    MIT
"""

from datetime import datetime, timedelta
import logging
from os import path

def find_files_in_daterange(fromdate, todate, rawdir,
                            dateformat='%Y-%m-%d',
                            filenameformat='%Y-%m-%d.json',
                            logger=None):
    r"""Finds all files in a daterange in a directory. Returns a list.

    Finds all files that fall within `fromdate` to `todate` inside
    `rawdir`, by looking at the files names, **not their creation
    dates**.

    Parameters
    ----------


    Returns
    -------
    filepaths : list[str]
        A list of the found files' paths.

    """

    dates = generate_datesequence(fromdate, todate, dateformat, filenameformat)
    filepaths = []
    for date in dates:
        loadfilepath = rawdir + date
        if(path.exists(loadfilepath)):
            filepaths.append(loadfilepath)
        elif logger is not None:
            logger.debug('File not found: {}'.format(loadfilepath))
    if logger is not None:
        logger.info("{0} files found in date range {1} to {2}".format(
                        len(filepaths),fromdate,todate))

    return filepaths

def generate_datesequence(fromdate, todate,
                          informat='%Y-%m-%d',
                          outformat='%Y-%m-%d'):
    r"""Generates a list of sequential dates.

        Parameters
        ----------
        fromdate, todate : str
            A date in format `dateformat`.
        dateformat : str, optional
            The format string as detailed in the python documentation
            for the datetime package (default is '%Y-%m-%d').

        Returns
        -------
        list[str]
            A list of dates in format `dateformat` starting at
            `fromdate` and ending at `todate` (inclusive)
    """

    dates = []
    start = datetime.strptime(fromdate, informat)
    end = datetime.strptime(todate, informat)
    step = timedelta(days=1)
    while start <= end:
        dates.append(start.strftime(outformat))
        start += step

    return dates

def setup_logger(name, logfilepath=None, console=True, level=logging.INFO):
    r"""Setup logging to a file and/or the console. Returns the logger.

    Parameters
    ----------
    name : str
        The name for the logger.
    logfilepath : str, optional
        The full path to the logfile, that shall be written. (Default
        is None, which implies no log file will be created.)
    console : bool, optional
        Determines whether the log should (also) be written to the
        console. (Default is True.)
    level : int, optional
        The minimal level of logs, that shall be written. (Default is
        logging.INFO (20).)

    Returns
    -------
    logger : logging.Logger
        The logger object.

    """

    if logfilepath is not None and path.isdir(path.dirname(logfilepath)):
        logfile = logging.FileHandler(logfilepath)
        logfile.setLevel(level)
        fileformat = logging.Formatter(
            fmt='%(asctime)s %(name)-12s %(levelname)-8s %(message)s',
            datefmt='%m-%d %H:%M:%S')
        logfile.setFormatter(fileformat)
        logging.getLogger(name).addHandler(logfile)

    if console:
        console = logging.StreamHandler()
        console.setLevel(level)
        consoleformat = logging.Formatter('%(name)-12s: %(levelname)-8s %(message)s')
        console.setFormatter(consoleformat)
        logging.getLogger(name).addHandler(console)

    return logging.getLogger(name)

##if __name__ == '__main__':
##    print generate_datelist('2015-12-16','2015-12-24')
