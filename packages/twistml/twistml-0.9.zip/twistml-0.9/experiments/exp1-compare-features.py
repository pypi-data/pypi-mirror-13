r"""<summary>

    <extended summary>

    <routine listings>

    <see also>

    <notes>

    <references>

    <examples>

:Author:
    Matthias Manhertz
:Copyright:
    (c) Matthias Manhertz 2015
:Licence:
    MIT
"""

import pickle
import itertools
from twistml.targets import StockCsvReader, get_daily_changes
import twistml as tml
from twistml import evaluate_binary_classification as evaluate
from twistml.features.window import window_stack, window_element_sum
from twistml.features.window import window_element_avg
import matplotlib.pyplot as plt
from matplotlib.backends.backend_pdf import PdfPages
from os import path
import optparse
from sklearn.svm import SVC
from time import time, sleep
import numpy as np
import scipy.sparse as sps
import sys


def calculate_aucs(features, targets, windows, n_runs, window_function,
                   use_coeff):
    r"""<Summary>"""

    aucs = []
    stds = []
    svm = SVC(probability=(not use_coeff))
    cvparams = {'kernel': ['linear'], 'C': np.logspace(-2,2,5)}
    i = 0
    t0 = time()
    for win in windows:
        i += 1
        print "\rProcessing window {} of {}   ".format(i, len(windows)),
        window = tml.features.Window(win[0], win[1])
        X, y, dates = tml.features.get_windowed(
            features, targets, window, window_function=window_function)
        if sps.issparse(X[0]):
            X = sps.vstack(X)
        else:
            X = np.vstack(X)
        y = np.array(y)
        result = evaluate(X, y, svm, cvparams, n_runs, use_coeff=use_coeff,
                          n_jobs=4, cv=3, verbose=0, return_F1=False)
        aucs.append(result.auc)
        stds.append(result.aucstd)

    print ""
    print "Done in {0:.1f}min".format((time()-t0)/60)

    return aucs, stds


def main(featurefilepaths, stockfilepath, pricecolumn, datecolumn,
         txtfilepath, window_function, n_runs=10):
    r"""

        Parameters
        ----------
        featurefilepath : list[str]
            List of paths to the .npz files containing the different
            feature representations as dicts mapping each feature
            vector to a datetime stamp.
        stockfilepath : str
            Path to the .csv file containing the stock prices.
        pricecolumn : int
            The column index within the stock file of the column
            containing the closing prices
        datecolumn : int
            The column index within the stock file of the column
            containing the date
        txtfilepath : str
            Path to the .pdf file the resulting graphs should be saved
            to
        n_runs : int, optional
            The number of runs for each evaluation within the
            experiment. More runs means more stable means and stds.
            (default is 10)

    """

    t0 = time()
    windows = [
        [1,-1],[1,-2],[1,-3],[1,-4],[1,-5],[1,-6],
        [2,-1],[2,-2],[2,-3],[2,-4],[2,-5],
        [3,-1],[3,-2],[3,-3],[3,-4],
        [4,-1],[4,-2],[4,-3]]

    csv = StockCsvReader(stockfilepath, pricecolumn, datecolumn)
    targets = tml.targets.get_daily_changes(
        csv.read(), '2013-01-01', '2013-12-31', return_classes=True)

    aucdata = []
    aucerrors = []
    labels = []
    for featurefilepath in featurefilepaths:
        with open(featurefilepath, 'rb') as f:
            features = pickle.load(f)

        aucs, stds = calculate_aucs(features, targets, windows, n_runs,
                                    window_function, use_coeff=True)
        aucdata.append(aucs)
        aucerrors.append(stds)
        labels.append(path.basename(path.splitext(featurefilepath)[0]))

    stockfilename = path.basename(stockfilepath)

##    figure = graph(results, labels, stockfilename, None)
##    pp = PdfPages(pdffilepath)
##    pp.savefig(figure)
##    pp.close()


    with open(txtfilepath + '.npz', 'wb') as f:
        pickle.dump(aucdata, f)


    # generate latex table with results
    aucdata = np.array(aucdata).T
    with open(txtfilepath, 'w') as f:
        n_rows, n_columns = aucdata.shape
        f.write('%AUC by Window and Feature Representation\n')

        # Header row
        f.write('\\begin{tabular}{l|' + 'S'*(n_columns) + '}\n')
        f.write('  \\toprule\n')
        f.write('  Window &')
        for i in range(len(labels)):
            line = ' ' + labels[i]
            if i == len(labels)-1:
                line +=' \\\\\n'
            f.write(line)
        f.write('  ' + '& {AUC} '*n_columns + '\\\\\n')
        f.write('  \\midrule\n')

        # data body
        for r in range(n_rows):
            size = str(windows[r][0])
            offset = str(windows[r][1])
            line = '  (' + size + ',' + offset + ') '
            for c in range(n_columns):
                line += '& {:.2f} '.format(aucdata[r,c])
            line += '\\\\\n'
            f.write(line)

        f.write('  \\bottomrule\n')
        f.write('\\end{tabular}\n')

    print "Total runtime: {0:.1f} minutes".format((time()-t0)/60)
    pass


def _check_dir(filepath, name, parser):
    if not filepath:
        parser.error("Please enter a filepath for the {}".format(name))
    dirname = path.dirname(filepath)
    if not path.isdir(dirname):
        parser.error("{} is not a valid directory.".format(dirname))
    pass


def _check_file(filepath, name, parser):
    if not filepath:
        parser.error("Please enter a filepath for the {}".format(name))
    if not path.exists(filepath):
        parser.error("{} is not a valid filepath.".format(filepath))
    pass


if __name__ == '__main__':
    usage = 'usage: %prog [options] featurefilepath1 featurefilepath2...'
    parser = optparse.OptionParser(usage=usage)
##    parser.add_option("-f", "--features",
##                      type="string", dest="featurefile",
##                      help=".npz file with the features")
    parser.add_option("-s", "--stock",
                      type="string", dest="stockfile",
                      help=".csv file with the stock data")
    parser.add_option("-t", "--txt",
                      type="string", dest="txtfile",
                      help="store the resulting latex table to this file")
    parser.add_option("-r", "--reruns",
                      type="int", dest="reruns", default=10,
                      help="Number of reruns [default = 10]")
    parser.add_option("--pricecolumn",
                      type="int", dest="pricecolumn", default=6,
                      help="Column index of the prices [default = 6]")
    parser.add_option("--datecolumn",
                      type="int", dest="datecolumn", default=0,
                      help="Column index of the dates [default = 0]")
    parser.add_option("-w", "--windowfunction",
                      type="string", dest="windowfunction",
                      help="Use this function to form windows.")

    (options, args) = parser.parse_args()

    if len(args) == 0:
        parser.error("Please enter a filepath for the {}".format(
            'feature file'))
    for featurefile in args:
        _check_file(featurefile, 'feature file', parser)
    _check_file(options.stockfile, 'stock file (-s, --stock)', parser)
    _check_dir(options.txtfile, 'text file (-t, --txt)', parser)

    window_func_map = {
        'sum': window_element_sum,
        'avg': window_element_avg,
        'stack': window_stack}
    win_options_str = "Available Window Functions are 'sum', 'avg' and 'stack'"
    if not options.windowfunction:
        parser.error("Need Window Function (-w)\n" + win_options_str)
    if not options.windowfunction in window_func_map:
        parser.error("Unknown Window Function: {}\n".format(
            options.windowfunction) + win_options_str)
    window_function = window_func_map[options.windowfunction]

    main(args, options.stockfile, options.pricecolumn,
         options.datecolumn, options.txtfile,
         window_function, options.reruns)
