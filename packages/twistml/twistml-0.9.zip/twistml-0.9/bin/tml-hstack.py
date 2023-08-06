r"""

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
from twistml.features.combine import stack_features


def main(outpath, inpaths):
    r"""

    """

    print 'Stacking...',

    features = []
    for i in inpaths:
        if path.isfile(i):
            with open(i) as f:
                features.append(pickle.load(f))
        else:
            raise ValueError("{} is not a valid input path.")

    stacked =  stack_features(features)

    with open(outpath, 'wb') as f:
        pickle.dump(stacked, f)

    print ' done.'

    pass


class MyParser(optparse.OptionParser):
        def format_epilog(self, formatter):
            return self.epilog


if __name__ == '__main__':
    usage = "usage: %prog [OPTIONS] OUTPATH INPATH1 INPATH2..."
##    description = __doc__.split('\n\n')[1]
##    epilog = "\n\n" + "\n\n".join(__doc__.split('\n\n')[5:10])
    parser = optparse.OptionParser(usage=usage)#, description=description, epilog=epilog)

    (options, args) = parser.parse_args()

    # validate paths
    if len(args) < 3:
        parser.error("Need at least one outpath and two inpaths to make sense")
    for arg in args[1:]:
        if not path.isfile(arg):
            parser.error("{} is not a valid file".format(arg))

    main(args[0], args[1:])
