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
from twistml.evaluation.evaluation import _get_mean_std, selective_roc_auc_score, cross_validate
from sklearn.cross_validation import train_test_split
from sklearn.metrics import roc_auc_score
from sklearn.neighbors import KNeighborsClassifier
import matplotlib.pyplot as plt
from matplotlib.backends.backend_pdf import PdfPages
from os import path
import optparse
from sklearn.svm import SVC
from time import time, sleep
import numpy as np
import scipy.sparse as sps
import sys



def graph(feature_types, labels, stock, logger):
    r"""Returns a bar chart"""

    t1 = time()
    # logger.info('Graphing results... ')
    n_groups = len(feature_types[0])*2
    n_types = len(feature_types)
    # logger.info('{0} groups found.'.format(n_groups))

    fig, ax = plt.subplots()

    index = np.arange(n_groups)
    bar_width = 1.0 / float(n_types + 1)

    opacity = 0.4
    error_config = {'ecolor': '0.3'}

    i = 0
    rects = []
    colors=['b','g','y','c','r']
    figure = plt.figure()
    for ftype in feature_types:
        ftype.sort()
        windows, aucs, stds, saucs, sstds = zip(*ftype)
        name = labels[i]
        aucs = aucs + saucs
        stds = stds + sstds
        print aucs
        rects.append(plt.bar(index + bar_width*(i),
                           aucs, bar_width,
                           alpha=opacity,
                           color=colors[i],
                           yerr=stds,
                           error_kw=error_config,
                           label=name ))
##        name = labels[i+1]
####        print aucs
##        rects.append(plt.bar(index + bar_width*(i+1),
##                           saucs, bar_width,
##                           alpha=opacity,
##                           color=colors[i+1],
##                           yerr=sstds,
##                           error_kw=error_config,
##                           label=name ))
        i += 1
    windows, aucs, stds, saucs, sstds = zip(*(feature_types[0]))

    plt.xlabel('Windows')
    plt.ylabel('AUC Scores')
    plt.ylim(0.4,0.7)
    plt.title('AUC Scores by Window and Feature Representation for {}'.format(stock))
    plt.xticks(index + bar_width*n_types/2, [str(x) for x in windows])
    plt.legend()
    plt.grid(b=True, which='major', color='k', linestyle='--')
    plt.gca().xaxis.grid(False)
    plt.gca().yaxis.grid(True)

    plt.tight_layout()
##    plt.show()
##    pass
    return figure


def calculate_aucs(features, targets, windows, n_runs):
    r"""<Summary>"""

    aucs = []
    stds = []
    saucs = []
    sstds = []
    method = KNeighborsClassifier()  # SVC(probability=True)
    cvparams = {'n_neighbors': [3,4,5,6,7]}
##    cvparams = {'kernel': ['linear'], 'C': np.logspace(-2,2,5)}
    i = 0
    t0 = time()
    for win in windows:
        i += 1
        print "\rProcessing window {} of {}   ".format(i, len(windows)),
        window = tml.features.Window(win[0], win[1])
        X, y, dates = tml.features.get_windowed(features, targets, window)
        if sps.issparse(X[0]):
            X = sps.vstack(X)
        else:
            X = np.vstack(X)
        y = np.array(y)

        aucscores = []
        saucscores = []
        lowers = []
        uppers = []
        use_coeff=False

        for j in range(n_runs):
            X_train, X_test, y_train, y_test = train_test_split(
                X, y, test_size=0.2, random_state=None)

            fitted_grid = cross_validate(X_train, y_train, method,
                                         cvparams, n_jobs=4, cv=3,
                                         scoring='roc_auc', verbose=0)

            if use_coeff:
                w = fitted_grid.best_estimator_.coef_
                if sps.issparse(w):
                    w = w.toarray()
                y_proba = X_test.dot(w.ravel().T)
            else:
                y_proba = fitted_grid.predict_proba(X_test)[:, 1]

            auc = roc_auc_score(y_test, y_proba)
            sauc = 0.0
            best_lower = 0.0
            best_upper = 0.0

##            y_proba_sorted = np.sort(y_proba)
##            for lower in y_proba_sorted:
##                for upper in y_proba_sorted:
##                    if lower >= upper:
##                        continue
##                    s = selective_roc_auc_score(y_test, y_proba, lower, upper)
##                    if s > sauc:
##                        sauc = s
##                        best_lower = lower
##                        best_upper = upper


            lower = 0.10
            upper = 0.90
            sauc = selective_roc_auc_score(y_test, y_proba, lower, upper)
            best_lower = lower
            best_upper = upper

            aucscores.append(auc)
            saucscores.append(sauc)
            lowers.append(best_lower)
            uppers.append(best_upper)


        meanauc, stdauc = _get_mean_std(aucscores)
        aucs.append(meanauc)
        stds.append(stdauc)
        meansauc, stdsauc = _get_mean_std(saucscores)
        saucs.append(meansauc)
        sstds.append(stdsauc)
        print ""
        print "For window {} the means are {:.3f} | {:.3f} | {:.3f} | {:.3f}".format(
            i,meanauc, meansauc, np.mean(lowers), np.mean(uppers))
        for j in range(n_runs):
            print "AUC: {:.3f} | SAUC: {:.3f} | Lower: {:.3f} | Upper: {:.3f}".format(
                aucscores[j], saucscores[j], lowers[j], uppers[j])

    print ""
    print "Done in {0:.1f}min".format((time()-t0)/60)
    results = zip(windows, aucs, stds, saucs, sstds)
    return results


def main(featurefilepaths, stockfilepath, pricecolumn, datecolumn,
         pdffilepath, n_runs=10):
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
    results = []
    labels = []
    for featurefilepath in featurefilepaths:
        with open(featurefilepath, 'rb') as f:
            features = pickle.load(f)

        csv = StockCsvReader(stockfilepath, pricecolumn, datecolumn)
        targets = tml.targets.get_daily_changes(csv.read(), '2013-01-01',
                                                '2013-12-31', return_classes=True)

        sizes = [1,3,5]
        offsets = [-2,-1]
        windows = [list(item) for item in itertools.product(sizes, offsets)]

        results.append(calculate_aucs(features, targets, windows, n_runs))
        labels.append(path.basename(path.splitext(featurefilepath)[0]))
        labels.append(path.basename(path.splitext(featurefilepath)[0]) + '-s')

    stockfilename = path.basename(stockfilepath)
    figure = graph(results, labels, stockfilename, None)

    pp = PdfPages(pdffilepath)
    pp.savefig(figure)
    pp.close()

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

    (options, args) = parser.parse_args()

    if len(args) == 0:
        parser.error("Please enter a filepath for the {}".format(
            'feature file'))
    for featurefile in args:
        _check_file(featurefile, 'feature file', parser)
    _check_file(options.stockfile, 'stock file (-s, --stock)', parser)
    _check_dir(options.pdffile, 'pdf file (-p, --pdf)', parser)

    main(args, options.stockfile, options.pricecolumn,
         options.datecolumn, options.pdffile, options.reruns)
