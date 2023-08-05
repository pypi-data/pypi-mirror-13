r"""Command line script to access the feature generating functinality
    of twistml

:Author:
    Matthias Manhertz
:Copyright:
    (c) Matthias Manhertz 2015
:Licence:
    MIT
"""

from os import path
import twistml as tml
from twistml.utility import query_yes_no as yes_no
import cPickle as pickle
from time import time
import optparse
import sys


def main(fromdate, todate, indir, outpath, featuretype, subdirs=True,
         logfilepath=None, dateformat='%Y-%m-%d',
         filenameformat='%Y-%m-%d.json'):
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

    logger.info('Finding Files in daterange ({} - {})...'.format(
        fromdate, todate))

    filepaths = tml.find_files(indir, subdirs,
                               fromdate=fromdate, todate=todate,
                               dateformat=dateformat,
                               filenameformat=filenameformat,
                               logger=logger)

    if featuretype == 'bow':
        # Generate Bag of Words feature
        cvg = tml.features.CountVectorTransformer(min_df=2, analyzer='word')
        features = cvg.transform(filepaths)
    elif featuretype == 'cng':
        # Generate Character n-gram features
        cvg = tml.features.CountVectorTransformer(min_df=2, analyzer='char',
                                                  ngram_range=(2, 3))
        features = cvg.transform(filepaths)
    elif featuretype == "d2v":
        # Generate Doc2Vec features
        d2v = tml.features.Doc2VecTransformer()
        features = d2v.transform(filepaths)
    else:
        sys.exit("Unknown Feature-Type: {}".format(featuretype))

    t1 = time()
    logger.info( "Dumping features into {0}...".format(outpath),)
    with open(outpath, 'wb') as pkl:
        pickle.dump( features, pkl )
    logger.info( " done in {0:.1f}sec.".format(time()-t1))

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
                      help="Directory with the twitter .json-files")
    parser.add_option("-o", "--outpath",
                      dest="outpath",
                      help="Path for the output pickle file")
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
    parser.add_option("--featuretype",
                      dest="featuretype", default='bow',
                      help="bow / cng / lexsnt / nbsnt [default = %default]")

    (options, args) = parser.parse_args()

    # validate paths
    if not options.indir:
        parser.error("Need input directory (--indir)")
    if not options.outpath:
        parser.error("Need output file path (--outpath)")
    if not path.isdir(options.indir):
        parser.error("{} is not a valid directory.".format(options.indir))
    if path.isdir(options.outpath):
        parser.error("{} should be a full filepath.".format(options.outpath))
    if path.exists(options.outpath):
        if not yes_no('{} already exists. Overwrite?'.format(options.outpath),
                      default='no'):
            parser.error("Aborted by user")
    if not options.indir.endswith("/"):
        options.indir = options.indir + '/'
    if not options.logfile:
        options.logfile = None
    if  (options.logfile is not None and
          not path.isdir(path.dirname(options.logfile))):
        parser.error("{} is not a valid path for the logfile.".format(
                        path.dirname(options.logfile)))

    main(options.fromdate, options.todate, options.indir, options.outpath,
         options.featuretype, options.subdirs, options.logfile,
         options.datefmt, options.filefmt)
