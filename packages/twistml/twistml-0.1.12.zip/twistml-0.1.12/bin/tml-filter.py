r"""Command line script to access the filtering functionality of
    twistml

    <extended summary>

    Notes
    -----
    The --skipto command line option can be used to skip for example
    the time consuming raw filtering (by setting --skipto=1).

    <references>

    <examples>

:Author:
    Matthias Manhertz
:Copyright:
    (c) Matthias Manhertz 2015
:Licence:
    MIT
"""

import optparse
import twistml as tml
from twistml.utility import progress_report as progress
from os import path, listdir
from time import time
import json
from datetime import datetime

def main(fromdate, todate, indir, outdir, logfilepath=None,
         dateformat='%Y-%m-%d', filenameformat='%Y-%m-%d.json',
         skipto=0):
    r"""<Summary>

        <Extended Summary>

        Parameters
        ----------
        x : int, optional
            Description of parameter `x` (the default is -1, which
            implies summation over all axes).
    """

    logger = tml.setup_logger('Filtering', logfilepath=logfilepath,
                                      console=True, level=20)

    now = datetime.now().strftime('%H:%M on %B %d, %Y')
    logger.info('Started running at {}.'.format(now))

    logger.info('Finding Files in daterange ({} - {})...'.format(
        fromdate, todate))
    filepaths = tml.find_files(fromdate, todate, indir, logger=logger)

    logger.info('Processing {} files. This might take a while...'.format(
        len(filepaths)))
    t0 = time()

    # filter raw tweets
    if skipto < 1:
        logger.info('Filtering raw tweets')
        t00 = time()
        i = 0
        for filepath in filepaths:
            i += 1
            tml.filter_raw([filepath], outdir, logger=logger)
            print progress(t00, len(filepaths), i)


    # filter categories
    if skipto < 2:
        if skipto < 1:
            filepaths = tml.find_files(fromdate, todate, outdir, logger=logger)
        logger.info('Filtering tweets by category')
        t00 = time()
        i = 0
        for filepath in filepaths:
            i += 1

            with open(filepath) as jsonfile:
                tweets = json.load(jsonfile)

            filename = path.basename(filepath)
            filepaths = tml.filter_categories(tweets, outdir, filename)

            print progress(t00, len(filepaths), i)

    # filter languages
    if skipto < 3:
        if skipto == 2:
            filepaths = tml.find_files_in_subdirs(fromdate, todate, catdir,
                                                  logger=logger)
        logger.info('Filtering tweets by language')
        t00 = time()
        i = 0
        for filepath in filepaths:
            i += 1

            with open(filepath) as jsonfile:
                tweets = json.load(jsonfile)

            filtered_tweets = tml.filter_languages(tweets)

            newfilename = 'lang_' + path.basename(filepath)
            newfilepath = path.join(path.dirname(filepath), newfilename)
            with open(newfilepath, 'wb') as jsonfile:
                json.dump(tweets, jsonfile)

            print progress(t00, len(filepaths), i)
    pass

if __name__ == '__main__':
    parser = optparse.OptionParser()
    parser.add_option("-f", "--from",
                      dest="fromdate", default='2013-01-01',
                      help="Start of the date range [default: %default]")
    parser.add_option("-t", "--to",
                      dest="todate", default='2013-12-31',
                      help="End of the date range [default: %default]")
    parser.add_option("-i", "--indir",
                      dest="indir",
                      help="Directory with the raw twitter .json-files")
    parser.add_option("-o", "--outdir",
                      dest="outdir",
                      help="Directory for the filtered output .json-files")
    parser.add_option("-l", "--logfile",
                      dest="logfile",
                      help="Path to the logfile to be created / appended.")
    parser.add_option("--datefmt",
                      dest="datefmt", default='%Y-%m-%d',
                      help="Format for the dates [default = %default]")
    parser.add_option("--filefmt",
                      dest="filefmt", default='%Y-%m-%d.json',
                      help="Format of the filenames [default = %default]")
    parser.add_option("-s", "--skipto",
                      type="int", dest="skipto", default=0,
                      help="Skip some steps. See documentation for detail.")

    (options, args) = parser.parse_args()

    # validate paths
    if not options.indir:
        parser.error("Need input directory (--indir)")
    if not options.outdir:
        parser.error("Need output directory (--outdir)")
    if not path.isdir(options.indir):
        parser.error("{} is not a valid path.".format(options.indir))
    if not path.isdir(options.outdir):
        parser.error("{} is not a valid path.".format(options.outdir))
    if not options.indir.endswith("/"):
        options.indir = options.indir + '/'
    if not options.outdir.endswith("/"):
        options.outdir = options.outdir + '/'
    if not options.logfile:
        options.logfile = None
    if  (options.logfile is not None and
          not path.isdir(path.dirname(options.logfile))):
        parser.error("{} is not a valid path for the logfile.".format(
                        path.dirname(options.logfile)))

    main(options.fromdate, options.todate, options.indir, options.outdir,
         options.logfile, options.datefmt, options.filefmt, options.skipto)
