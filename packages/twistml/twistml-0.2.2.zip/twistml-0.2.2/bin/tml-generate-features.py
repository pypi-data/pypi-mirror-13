#!/usr/bin/env python
r"""Command line script to generate features.

The inputs can be either directories or paths to files containing
directories. Each such file must be a plain text file containing one
directory path per line. This way the resulting features can be built
from arbitralily complex sets of categories, assuming that each
categories has its own directory with its data files.


Usage
-----

Command Line Options
--------------------

Examples
--------

For example the categories 'apple', 'ipad', 'iphone' and 'samsung'
could each have their own directories (e.g. 'c:/cats/apple',
'c:/cats/ipad', 'c:/cats/iphone' and 'c:/cats/samsung'). The apple
centric categories could be summed up in a file 'c:/apple_all.cat'.

Generating features for apple and samsung could then be done like
this::

    tml-generate-features.py -o c:/feat/apl_smsg.npz c:/apple_all.cat
    c:/cats/samsung

Generating features for all categories in 'c:/cats' can be accomplished
by using the subdirs flag::

    tml-generate-features.py -o c:/feat/all.npz --subdirs c:/cats

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


def main(fromdate, todate, inputs, outpath, featuretype, subdirs=True,
         logfilepath=None, dateformat='%Y-%m-%d',
         filenameformat='%Y-%m-%d.json'):
    r"""Generate a feature file in pickle format.

        Intended to be invoked as a command line script, this function
        reads preprocessed twitter .json files from `inputs`, generates
        features of type `featuretype` and saves those in a pickle file
        at `outpath`.

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

    # inputs can be a list of directories or paths to files containing
    # a list of dirs each
    for i in inputs:
        if path.isdir(i):
            filepaths = tml.find_files(i, subdirs,
                                       fromdate=fromdate, todate=todate,
                                       dateformat=dateformat,
                                       filenameformat=filenameformat,
                                       logger=logger)
        elif path.isfile(i):
            paths = [line.rstrip() for line in open(i)]
            filepaths = []
            for p in paths:
                if not path.isdir(p):
                    print p
                    print type(p)
                    raise ValueError("Invalid path {} in {}".format(p, i))
                filepaths.extend(tml.find_files(p, subdirs,
                                                fromdate=fromdate, todate=todate,
                                                dateformat=dateformat,
                                                filenameformat=filenameformat,
                                                logger=logger))
        else:
            raise ValueError("{} is not a valid input path.")

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
    elif featuretype == "lexsnt":
        # Generate Sentiment features with lexical 'pattern' analyzer
        snt = tml.features.SentimentTransformer(analyzer='pattern')
        features = snt.transform(filepaths)
    elif featuretype == "nbsnt":
        # Generate Sentiment features with lexical 'pattern' analyzer
        snt = tml.features.SentimentTransformer(analyzer='naivebayes')
        features = snt.transform(filepaths)
    else:
        sys.exit("Unknown Feature-Type: {}\n".format(featuretype) +
                 "Supported types are: bow / cng / lexsnt / nbsnt / d2v")

    t1 = time()
    logger.info( "Dumping features into {0}...".format(outpath),)
    with open(outpath, 'wb') as pkl:
        pickle.dump( features, pkl )
    logger.info( " done in {0:.1f}sec.".format(time()-t1))

    pass


class MyParser(optparse.OptionParser):
        def format_epilog(self, formatter):
            return self.epilog


if __name__ == '__main__':
    usage = "usage: %prog -o OUTPATH [options] INPUT1 INPUT2..."
    description = __doc__.split('\n\n')[1]
    epilog = "\n\n" + "\n\n".join(__doc__.split('\n\n')[5:10])
    parser = MyParser(usage=usage, description=description, epilog=epilog)
    parser.add_option("-f", "--from",
                      dest="fromdate", default='2013-01-01',
                      help="Start of the date range [default: %default]")
    parser.add_option("-t", "--to",
                      dest="todate", default='2013-12-31',
                      help="End of the date range [default: %default]")
    parser.add_option("-o", "--outpath",
                      dest="outpath",
                      help="Path for the output pickle file")
    parser.add_option("-s", "--subdirs", action="store_true",
                      dest="subdirs", default=False,
                      help="If data is in subdirs of inputs. [default=False]")
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
                      help="bow / cng / lexsnt / nbsnt / d2v [default = bow]")

    (options, args) = parser.parse_args()

    # validate paths
    if not options.outpath:
        parser.error("Need output file path (--outpath)")
    if path.isdir(options.outpath):
        parser.error("{} should be a full filepath.".format(options.outpath))
    if not path.isdir(path.dirname(options.outpath)):
        parser.error("{} doesn't exist.".format(path.dirname(options.outpath)))
    if path.exists(options.outpath):
        if not yes_no('{} already exists. Overwrite?'.format(options.outpath),
                      default='no'):
            parser.error("Aborted by user")
    if not options.logfile:
        options.logfile = None
    if (options.logfile is not None and
        not path.isdir(path.dirname(options.logfile))):
        parser.error("{} is not a valid path for the logfile.".format(
                        path.dirname(options.logfile)))

    main(options.fromdate, options.todate, args, options.outpath,
         options.featuretype, options.subdirs, options.logfile,
         options.datefmt, options.filefmt)
