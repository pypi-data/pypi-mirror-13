r"""Command line script to access the preprocessing functionality of
    twistml

    <extended summary>

    <routine listings>

    <see also>

    Notes
    -----
    The --subdirs (-s) command line option will search for files in the
    subdirectories of indir and write results to matching
    subdirectories in outdir (creating the subdirectories if they do
    not exist already). This works well with the subdirectories created
    by the category filtering, which creates subdirectories for each
    category.

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
from datetime import datetime
import twistml as tml
import json
from os import path, makedirs
from time import time

def main(fromdate, todate, indir, outdir, subdirs, logfilepath=None,
         dateformat='%Y-%m-%d', filenameformat='%Y-%m-%d.json',
         overwrite=False):
    r"""<Summary>

        <Extended Summary>

        Parameters
        ----------
        x : int, optional
            Description of parameter `x` (the default is -1, which
            implies summation over all axes).
    """

    logger = tml.setup_logger('Preprocessing', logfilepath=logfilepath,
                              console=True, level=20)

    now = datetime.now().strftime('%H:%M on %B %d, %Y')
    logger.info('Started running at {}.'.format(now))

    logger.info('Finding Files in daterange ({} - {})...'.format(
        fromdate, todate))

    if subdirs:
        filepaths = tml.find_files_in_subdirs(fromdate, todate, indir,
                                              logger=logger)
    else:
        filepaths = tml.find_files(fromdate, todate, indir, logger=logger)

    logger.info('Processing {} files. This might take a while...'.format(
        len(filepaths)))
    t0 = time()

    for filepath in filepaths:
        # load tweets
        with open(filepath) as jsonfile:
            tweets = json.load(jsonfile)

        # preprocess tweets
        tweets = tml.preprocess_tweets(tweets)

        # save tweets
        filename = path.basename(filepath)
        if subdirs:
            subdirname = path.basename(path.dirname(filepath))
            savedir = path.join(outdir, subdirname)
            if not path.isdir(savedir):
                makedirs(savedir)
            savepath = path.join(savedir, filename)
        else:
            savepath = path.join(outdir, filename)
        with open(savepath, 'wb') as jsonfile:
            json.dump(tweets, jsonfile)

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
                      help="Directory with the input .json-files")
    parser.add_option("-o", "--outdir",
                      dest="outdir",
                      help="Directory for the filtered output .json-files")
    parser.add_option("-s", "--subdirs", action="store_true",
                      dest="subdirs", default=False,
                      help="Set to true if files are in subdirs of indir.")
    parser.add_option("-l", "--logfile",
                      dest="logfile",
                      help="Path to the logfile to be created / appended.")
    parser.add_option("--datefmt",
                      dest="datefmt", default='%Y-%m-%d',
                      help="Format for the dates [default = %default]")
    parser.add_option("--filefmt",
                      dest="filefmt", default='%Y-%m-%d.json',
                      help="Format of the filenames [default = %default]")
    parser.add_option("--overwrite", action="store_true",
                      dest="overwrite", default=False,
                      help="Enable overwriting of files when saving results.")

    (options, args) = parser.parse_args()

    # validate paths
    if not options.indir:
        parser.error("Need input directory (--indir)")
    if not path.isdir(options.indir):
        parser.error("{} is not a valid path.".format(options.indir))
    if not options.outdir:
        options.outdir = options.indir
    if not path.isdir(options.outdir):
        parser.error("{} is not a valid path.".format(options.outdir))
    if not options.indir.endswith("/"):
        options.indir = options.indir + '/'
    if not options.outdir.endswith("/"):
        options.outdir = options.outdir + '/'
    if options.outdir == options.indir and not options.overwrite:
        parser.error('Please either specify an outdir different from indir' +
                     ' or set the --overwrite=True option')
    if not options.logfile:
        options.logfile = None
    if (options.logfile is not None and
          not path.isdir(path.dirname(options.logfile))):
        parser.error("{} is not a valid path for the logfile.".format(
                        path.dirname(options.logfile)))

    main(options.fromdate, options.todate, options.indir, options.outdir,
         options.subdirs, options.logfile, options.datefmt, options.filefmt,
         options.overwrite)
