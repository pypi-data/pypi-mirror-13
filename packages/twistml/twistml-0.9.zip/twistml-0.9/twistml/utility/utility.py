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
import sys
from math import ceil, floor


def find_files(indir, subdirs=False, fromdate=None, todate=None,
               dateformat='%Y-%m-%d', filenameformat='%Y-%m-%d.json',
               logger=None):
    r"""Flexible function to find relevant files. Returns a list of
        filepaths.

    Parameters
    ----------
    indir : str
        The input directory, where the twitter files are located.
    subdirs : bool, optional
        Are the files located in subdirectories within `indir` (default
        is False)
    fromdate : str, optional
        First date of a daterange within which to find the files. The
        format for parsing the date from the string is given in
        `dateformat`. The file names are then parsed according to
        `filenameformat` and only files within the daterange are
        returned.
    todate : str, optional
        Last date of a daterange within which to find the files. The
        format for parsing the date from the string is given in
        `dateformat`. The file names are then parsed according to
        `filenameformat` and only files within the daterange are
        returned.
    dateformat : str, optional
        The format used to parse datetime objects from the given
        `fromdate` and `todate`.
    filenameformat : str, optional
        The format used to parse datetime objects from the filenames.
    logger : logging.Logger, optional
        A logger object, used to display / log console output
        (default is None, which implies quiet execution).

    Returns
    -------
    filepaths : list[str]
        A list of the found files' paths.

    References
    ----------
    For details about datetime formatting strings see the official
    documentation at docs.python.org_.

    .. _docs.python.org : https://docs.python.org/2/library/datetime.html#strftime-and-strptime-behavior

    """  # NOQA

    if fromdate is None or todate is None:
        raise NotImplementedError("find_files without fixed daterange")

    if subdirs:
        filepaths = _find_files_in_daterange_insubdirs(
            fromdate, todate, indir,
            dateformat=dateformat, filenameformat=filenameformat,
            logger=logger)
    else:
        filepaths = _find_files_in_daterange(
            fromdate, todate, indir,
            dateformat=dateformat, filenameformat=filenameformat,
            logger=logger)
    return filepaths


def _find_files_in_daterange(fromdate, todate, indir,
                             dateformat='%Y-%m-%d',
                             filenameformat='%Y-%m-%d.json',
                             logger=None):
    r"""Finds all files in a daterange in a directory. Returns a list.

    Finds all files that fall within `fromdate` to `todate` inside
    `indir`, by looking at the file's names, **not their creation
    dates**.

    """

    filenames = generate_datesequence(fromdate, todate, dateformat,
                                      filenameformat)
    filepaths = []
    for filename in filenames:
        loadfilepath = path.join(indir, filename)
        if(path.exists(loadfilepath)):
            filepaths.append(loadfilepath)
        elif logger is not None:
            logger.debug('File not found: {}'.format(loadfilepath))
    if logger is not None:
        logger.info("{0} files found in date range {1} to {2}".format(
                    len(filepaths), fromdate, todate))

    return filepaths


def _find_files_in_daterange_insubdirs(fromdate, todate, indir,
                                       dateformat='%Y-%m-%d',
                                       filenameformat='%Y-%m-%d.json',
                                       logger=None):
    r"""Performs find_files_in_daterange on all immediate
        subdirectories and returns a list of all the files.
    """

    catdirs = _get_immediate_subdirectories(indir)
    filepaths = []
    for catdir in catdirs:
        filepaths.extend(_find_files_in_daterange(fromdate, todate, catdir,
                                                  dateformat, filenameformat,
                                                  logger=None))
    if logger is not None:
        files = len(filepaths)
        dirs = len(catdirs)
        logger.info("{} files found in {} directories".format(files, dirs) +
                    " in date range {} to {}".format(fromdate, todate))
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
        fromdate, todate : str or datetime
            A date in format `dateformat`.
        informat : str, optional
            The format string as detailed in the python documentation
            for the datetime package (default is '%Y-%m-%d').
            If this is None, it is assumed, that a valid datetime
            instance was passed.
        outformat : str, optional
            The format string as detailed in the python documentation
            for the datetime package (default is '%Y-%m-%d').
            If this is None, the the returned dates will be datetime
            instances instead of formatted strings.
        Returns
        -------
        list[str] or list[datetime]
            A list of dates in format `dateformat` starting at
            `fromdate` and ending at `todate` (inclusive)
    """

    dates = []
    if informat is not None:
        start = datetime.strptime(fromdate, informat)
        end = datetime.strptime(todate, informat)
    else:
        start = fromdate
        end = todate
    step = timedelta(days=1)
    while start <= end:
        if outformat is None:
            dates.append(start)
        else:
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
        consoleformat = logging.Formatter(
            '%(name)-12s: %(levelname)-8s %(message)s')
        console.setFormatter(consoleformat)
        logging.getLogger(name).addHandler(console)

    logger = logging.getLogger(name)
    logger.setLevel(level)

    now = datetime.now().strftime('%H:%M on %B %d, %Y')
    logger.info('Started running at {}.'.format(now))

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
    report = ' '.join((line1, line2))
    return report


def query_yes_no(question, default="yes"):
    """Ask a yes/no question via raw_input() and return their answer.

    "question" is a string that is presented to the user.
    "default" is the presumed answer if the user just hits <Enter>.
        It must be "yes" (the default), "no" or None (meaning
        an answer is required of the user).

    The "answer" return value is True for "yes" or False for "no".
    """
    valid = {"yes": True, "y": True, "ye": True,
             "no": False, "n": False}
    if default is None:
        prompt = " [y/n] "
    elif default == "yes":
        prompt = " [Y/n] "
    elif default == "no":
        prompt = " [y/N] "
    else:
        raise ValueError("invalid default answer: '%s'" % default)

    while True:
        sys.stdout.write(question + prompt)
        choice = raw_input().lower()
        if default is not None and choice == '':
            return valid[default]
        elif choice in valid:
            return valid[choice]
        else:
            sys.stdout.write("Please respond with 'yes' or 'no' "
                             "(or 'y' or 'n').\n")


def remap(oldValue, oldMin, oldMax, newMin=0.0, newMax=1.0):
    r"""Linear scaling of a value between two intervals.

    Assuming `oldValue` lies in the interval [`oldMin`, `oldMax`] this
    function returns a new value that has been linearly scaled to the
    interval [`newMin`, `newMax`].

    Parameters
    ----------
    oldvalue : float
        The old value from the interval [`oldMin`, `oldMax`].
    oldMin : float
        The minimum of the old interval.
    oldMax : float
        The maximum of the old interval.
    newMin : float, optional
        The minimum of the new interval (default is 0.0).
    newMax : float, optional
        The maximum of the new interval (default is 1.0).

    Returns
    -------
    newValue : float
        The `oldValue` linearly scaled to the new interval.

    Raises
    ------
    ValueError
        IF the `oldValue` is outside the old interval or either minimum
        is greater than or equal to the corresponding maximum.

    Notes
    -----
    The code for this function has been partially taken from this
    stackexchange_ question by SpliFF and the answers by jerryjvl and
    PenguinTD.

    .. _stackexchange : http://stackoverflow.com/questions/929103/convert-a-number-range-to-another-range-maintaining-ratio

    """  # NOQA

    if (oldMin >= oldMax or newMin >= newMax):
        raise ValueError("Illegal interval. Max has to be > Min!")
    if (oldValue < oldMin or oldValue > oldMax):
        raise ValueError("oldValue outside old interval")

    oldRange = (oldMax - oldMin)
    newRange = (newMax - newMin)
    newValue = (((oldValue - oldMin) * newRange) / float(oldRange)) + newMin

    return newValue


def float_ceil(x, n=0):
    r"""Return the floating point value x rounded up to n digits
    after the decimal point.

    Parameters
    ----------
    x : float
        The value to be rounded.
    n : int, optional
        The number of digits after the decimal point to be rounded to.
        (default is 0)

    Returns
    -------
    float
        The value `x`, rounded up to `n` digits after the decimal
        point.

    """
    return ceil(x * (10**n)) / float(10**n)


def float_floor(x, n=0):
    r"""Return the floating point value x rounded down to n digits
    after the decimal point.

    Parameters
    ----------
    x : float
        The value to be rounded.
    n : int, optional
        The number of digits after the decimal point to be rounded to.
        (default is 0)

    Returns
    -------
    float
        The value `x`, rounded down to `n` digits after the decimal
        point.

    """
    return floor(x * (10**n)) / float(10**n)
