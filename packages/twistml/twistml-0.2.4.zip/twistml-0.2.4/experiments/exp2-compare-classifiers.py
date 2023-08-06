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
from sklearn.neighbors import KNeighborsClassifier
from sklearn.ensemble import GradientBoostingClassifier
from sklearn.dummy import DummyClassifier
from time import time, sleep
import numpy as np
import scipy.sparse as sps
import sys
import math
import winsound


def calculate(features, targets, method, cv_params, windows,
              window_function, n_runs,
              relative_test_size=0.2, force_dense=False):
    r"""<Summary>"""

    aucs = []
    stds = []
    f1scores = []
    f1stds = []
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

        # get AUCs
        result = evaluate(X, y, method, cv_params, n_runs,
                          force_dense=force_dense,
                          relative_test_size=relative_test_size,
                          n_jobs=4, cv=3, verbose=0)
        aucs.append(result.auc)
        stds.append(result.aucstd/math.sqrt(n_runs))
        f1scores.append(result.f1)
        f1stds.append(result.f1std/math.sqrt(n_runs))

    print ""
    print "Done in {0:.1f}min".format((time()-t0)/60)
    # results = zip(windows, aucs, stds)
    return aucs, stds, f1scores, f1stds


def main(featurefilepaths, stockfilepath, pricecolumn, datecolumn,
         pdffilepath, window_function, n_runs=10):
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
        pdffilepath : str
            Path to the .pdf file the resulting graphs should be saved
            to
        n_runs : int, optional
            The number of runs for each evaluation within the
            experiment. More runs means more stable means and stds.
            (default is 10)

    """

    t0 = time()
    figures = []
    data_backup = []

    for featurefilepath in featurefilepaths:
        aucdata = []
        aucerrors = []
        f1data = []
        f1errors = []
        labels = []
        with open(featurefilepath, 'rb') as f:
            features = pickle.load(f)

        csv = StockCsvReader(stockfilepath, pricecolumn, datecolumn)
        targets = tml.targets.get_daily_changes(csv.read(), '2013-01-01',
                                                '2013-12-31', return_classes=True)

##        sizes = [1,3,5]
##        offsets = [-2,-1]
##        windows = [list(item) for item in itertools.product(sizes, offsets)]
        windows = [
            [1,-1],[1,-2],[1,-3],[1,-4],[1,-5],[1,-6],[1,-7],
            [2,-1],[2,-3],[2,-5],
            [3,-1],[3,-3],
            [4,-1],[4,-3],
            [5,-1],[5,-3]
            ]

        featurename = path.basename(featurefilepath)

        # Method = Dummy with stratified strategy
        label = 'DumS'
        print "Processing {} for {}...".format(featurename, label)
        dum = DummyClassifier()
        cv_params = {}
        aucs , stds, f1scores, f1stds = calculate(
            features, targets, dum, cv_params, windows, window_function,
            n_runs)
        aucdata.append(aucs)
        aucerrors.append(stds)
        f1data.append(f1scores)
        f1errors.append(f1stds)
        labels.append(label)

        # Method = SVC
        label = 'SVC'
        print "Processing {} for {}...".format(featurename, label)
        svm = SVC(probability=True)
        cv_params = {'kernel': ['linear'], 'C': np.logspace(-2,2,5)}
        aucs , stds, f1scores, f1stds = calculate(
            features, targets, svm, cv_params, windows, window_function,
            n_runs)
        aucdata.append(aucs)
        aucerrors.append(stds)
        f1data.append(f1scores)
        f1errors.append(f1stds)
        labels.append(label)

        # Method = kNN
        label = 'KNN'
        print "Processing {} for {}...".format(featurename, label)
        knn = KNeighborsClassifier(n_jobs = 1)
        cv_params = {'n_neighbors': [2,4,5,6,10]}
        aucs , stds, f1scores, f1stds = calculate(
            features, targets, knn, cv_params, windows, window_function,
            n_runs)
        aucdata.append(aucs)
        aucerrors.append(stds)
        f1data.append(f1scores)
        f1errors.append(f1stds)
        labels.append(label)

        # Method = GBDT
        label = 'GBDT'
        print "Processing {} for {}...".format(featurename, label)
        gbdt = GradientBoostingClassifier()
        cv_params = {'max_depth': [2,3,4]}
        aucs , stds, f1scores, f1stds = calculate(
            features, targets, gbdt, cv_params, windows, window_function,
            n_runs,
            force_dense=True)
        aucdata.append(aucs)
        aucerrors.append(stds)
        f1data.append(f1scores)
        f1errors.append(f1stds)
        labels.append(label)

        # handle AUC scores
        aucdata = np.array(aucdata).T
        aucerrors = np.array(aucerrors).T
        fig = tml.utility.multi_group_bar_chart(
            data=aucdata,
            errors=aucerrors,
            setting_labels=[str(x) for x in windows],
            source_labels=labels,
            x_label='Windows',
            y_label='AUCs',
            title='AUCs by Window and Feature for {}'.format(featurename),
            ylim = 'auto')
        figures.append(fig)

        # handle f1 scores
        f1data = np.array(f1data).T
        f1errors = np.array(f1errors).T
        fig = tml.utility.multi_group_bar_chart(
            data=f1data,
            errors=f1errors,
            setting_labels=[str(x) for x in windows],
            source_labels=labels,
            x_label='Windows',
            y_label='F1 Score',
            title='F1 Scores by Window and Feature for {}'.format(featurename),
            ylim = 'auto')
        figures.append(fig)

        # backup all data
        window_labels = [str(x) for x in windows]
        data_backup.append({
            'Plot Type': 'Multi Group Bar Chart',
            'aucdata': aucdata,
            'aucerrors': aucerrors,
            'f1data': f1data,
            'f1errors': f1errors,
            'setting_labels': window_labels,
            'source_labels': labels,
            'x_label': 'Windows',
            'y_label': 'AUCs',
            'title': 'AUCs by Window and Feature for {}'.format(featurename),
            'ylim': 'auto'
            })


    # export plots to pdf
    pp = PdfPages(pdffilepath)
    for fig in figures:
        pp.savefig(fig)
    pp.close()

    # save raw data as pickle
    with open(pdffilepath + '.data.bak', 'wb') as f:
        pickle.dump(data_backup, f)

    # write raw data to a txt file in latex table format
    with open(pdffilepath + '.latex.txt', 'w') as f:
        for d in data_backup:
            aucdata = d['aucdata']
            f1data = d['f1data']
            n_rows, n_columns = aucdata.shape
            f.write('%' + d['title'] + '\n')
            f.write('\\begin{tabular}{l|' + 'S'*(n_columns*2) + '}\n')
            f.write('  \\toprule\n')
            f.write('  \\multirow{2}{*}{Window} &\n')
            labels = d['source_labels']
            for i in range(len(labels)):
                line = '    \\multicolumn{2}{c}{' + labels[i] + '}'
                if i < len(labels)-1:
                    line += ' &\n'
                else:
                    line +=' \\\\\n'
                f.write(line)
            f.write('    ' + '& {AUC} & {F1} '*n_columns + '\\\\\n')
            f.write('    \\midrule\n')

            for r in range(n_rows):
                size = str(windows[r][0])
                offset = str(windows[r][1])
                line = '  (' + size + ',' + offset + ') '
                for c in range(n_columns):
                    line += '& {:.2f} & {:.2f} '.format(aucdata[r,c], f1data[r,c])
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
    parser.add_option("-p", "--pdf",
                      type="string", dest="pdffile",
                      help="store the graphs to this .pdf file")
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
    _check_dir(options.pdffile, 'pdf file (-p, --pdf)', parser)

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
    print window_function

    main(args, options.stockfile, options.pricecolumn,
         options.datecolumn, options.pdffile,
         window_function, options.reruns)

    winsound.PlaySound('h:/tml/fanfare_x.wav', winsound.SND_FILENAME)
