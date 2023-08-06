r"""Command line script to access the filtering functionality of
    twistml

    <extended summary>

:Author:
    Matthias Manhertz
:Copyright:
    (c) Matthias Manhertz 2015
:Licence:
    MIT
"""

import optparse
import twistml as tml
from os import path, listdir
from time import time
import json

def main(fromdate, todate, indir, outdir, logfilepath=None,
         dateformat='%Y-%m-%d', filenameformat='%Y-%m-%d.json'):
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

    logger.info('Finding Files in daterange ({} - {})...'.format(
        fromdate, todate))
    filepaths = tml.find_files(indir, subdirs,
                               fromdate=fromdate, todate=todate,
                               dateformat=dateformat,
                               filenameformat=filenameformat,
                               logger=logger)

    logger.info('Processing {} files. This might take a while...'.format(
        len(filepaths)))

    t0 = time()
    logger.info('Filtering raw tweets')
    i = 0
    for filepath in filepaths:
        tml.filter_raw([filepath], outdir, logger=logger)
        i += 1
        print tml.progress_report(t0, len(filepaths), i)
    logger.info('Finished in {} minutes'.format((time()-t0)/60))
    pass

if __name__ == '__main__':
    usage = 'usage: %prog [options] INDIR OUTDIR'
    parser = optparse.OptionParser(usage=usage)
    parser.add_option("-f", "--from",
                      dest="fromdate", default='2013-01-01',
                      help="Start of the date range [default: %default]")
    parser.add_option("-t", "--to",
                      dest="todate", default='2013-12-31',
                      help="End of the date range [default: %default]")
##    parser.add_option("-i", "--indir",
##                      dest="indir",
##                      help="Directory with the raw twitter .json-files")
##    parser.add_option("-o", "--outdir",
##                      dest="outdir",
##                      help="Directory for the filtered output .json-files")
    parser.add_option("-l", "--logfile",
                      dest="logfile",
                      help="Path to the logfile to be created / appended.")
    parser.add_option("--datefmt",
                      dest="datefmt", default='%Y-%m-%d',
                      help="Format for the dates [default = %default]")
    parser.add_option("--filefmt",
                      dest="filefmt", default='%Y-%m-%d.json',
                      help="Format of the filenames [default = %default]")

    (options, args) = parser.parse_args()

    # validate paths
    if not len(args) == 2:
        parser.error("Need exactly one directory for each input and output")
##    if not options.indir:
##        parser.error("Need input directory (--indir)")
##    if not options.outdir:
##        parser.error("Need output directory (--outdir)")
    indir = args[0]
    outdir = args[1]
    if not path.isdir(indir):
        parser.error("{} is not a valid path. (INDIR)".format(indir))
    if not path.isdir(outdir):
        parser.error("{} is not a valid path. (OUTDIR)".format(outdir))
    if not indir.endswith("/"):
        indir = indir + '/'
    if not outdir.endswith("/"):
        outdir = outdir + '/'
    if not options.logfile:
        options.logfile = None
    if  (options.logfile is not None and
          not path.isdir(path.dirname(options.logfile))):
        parser.error("{} is not a valid path for the logfile.".format(
                        path.dirname(options.logfile)))

    main(options.fromdate, options.todate, indir, outdir,
         options.logfile, options.datefmt, options.filefmt)
