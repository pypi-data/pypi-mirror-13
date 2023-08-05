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
from os import path, listdir
from time import time

def find_files_in_daterange(fromdate, todate, indir,
                            dateformat='%Y-%m-%d',
                            filenameformat='%Y-%m-%d.json',
                            logger=None):
    r"""Finds all files in a daterange in a directory. Returns a list.

    Finds all files that fall within `fromdate` to `todate` inside
    `indir`, by looking at the file's names, **not their creation
    dates**.

    Parameters
    ----------


    Returns
    -------
    filepaths : list[str]
        A list of the found files' paths.

    """

    filenames = generate_datesequence(fromdate, todate, dateformat, filenameformat)
    filepaths = []
    for filename in filenames:
        loadfilepath = path.join(indir, filename)
        if(path.exists(loadfilepath)):
            filepaths.append(loadfilepath)
        elif logger is not None:
            logger.debug('File not found: {}'.format(loadfilepath))
    if logger is not None:
        logger.info("{0} files found in date range {1} to {2}".format(
                        len(filepaths),fromdate,todate))

    return filepaths

def find_files_in_daterange_insubdirs(fromdate, todate, indir,
                                      dateformat='%Y-%m-%d',
                                      filenameformat='%Y-%m-%d.json',
                                      logger=None):
    r"""Performs find_files_in_daterange on all immediate
        subdirectories and returns a list of all the files.
    """

    catdirs = _get_immediate_subdirectories(indir)
    filepaths = []
    for catdir in catdirs:
        filepaths.extend(find_files_in_daterange(fromdate, todate, catdir,
                                                 dateformat, filenameformat,
                                                 logger=None))
    if logger is not None:
        files = len(filepaths)
        dirs = len(catdirs)
        logger.info("{} files found in {} directories".format(files, dirs) +
                    " in date range {} to {}".format(fromdate,todate))
    return filepaths

def _get_immediate_subdirectories(a_dir):
    return [path.join(a_dir, name) for name in listdir(a_dir)
            if path.isdir(path.join(a_dir, name))]

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

def setup_logger(name, logfilepath=None, console=True, level=20):
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

    logger = logging.getLogger(name)
    logger.setLevel(level)

    return logger

def progress_report(starting_time, total_files, completed_files):
    r"""Returns a progress report for multi-file-operations.

    Parameters
    ----------
    starting_time : float
        Timestamp of the starting time of the multi-file-operation,
        usually obtained by calling time.time().
    total_files : int
        Number of files that are being processed.
    completed_files : int
        Number of files that have been completed.

    Returns
    -------
    report : str
        A two-line string stating time passed, number of files
        completed / left and estimated time remaining.

    """

    time_passed = time() - starting_time
    files_remaining = total_files - completed_files
    time_remaining = files_remaining * (time_passed/completed_files)
    line1 = "File {0} of {1} done in {2:.1f}min.".format(
            completed_files, total_files, time_passed/60)
    line2 = "Est. time remaining: {0:.1f}min".format(time_remaining/60)
    report = ' '.join((line1,line2))
    return report

##if __name__ == '__main__':
##    print generate_datelist('2015-12-16','2015-12-24')
