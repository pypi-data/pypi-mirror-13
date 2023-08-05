r"""Command line script to access the feature generating functinality
    of twistml

:Author:
    Matthias Manhertz
:Copyright:
    (c) Matthias Manhertz 2015
:Licence:
    MIT
"""


def main():
    r"""<Summary>

        <Extended Summary>

        Parameters
        ----------
        x : int, optional
            Description of parameter `x` (the default is -1, which
            implies summation over all axes).

    """

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
         options.logfile, options.datefmt, options.filefmt)
