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
from twistml import evaluate_regression as evaluate
from twistml.features.window import window_stack, window_element_sum
from twistml.features.window import window_element_avg
import matplotlib.pyplot as plt
from matplotlib.backends.backend_pdf import PdfPages
from os import path, rename
import optparse
from sklearn.svm import SVR
from sklearn.linear_model import LassoCV
from sklearn.kernel_ridge import KernelRidge
from sklearn.dummy import DummyRegressor
from time import time, sleep
import numpy as np
import scipy.sparse as sps
import sys
import math
import winsound
from datetime import datetime


def calculate(features, targets, method, cv_params, windows,
              window_function, n_runs,
              relative_test_size=0.2, force_dense=False):
    r"""<Summary>"""

    mses = []
    msestds = []
    mapes = []
    mapestds = []
    aucs = []
    aucstds = []
    f1s = []
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

        # get MSE/MAPE
        result = evaluate(X, y, method, cv_params, n_runs,
                          force_dense=force_dense,
                          relative_test_size=relative_test_size,
                          simulate_classification=True,
                          n_jobs=4, cv=3, verbose=0)
        mses.append(result.mse)
        msestds.append(result.msestd/math.sqrt(n_runs))
        mapes.append(result.mape)
        mapestds.append(result.mapestd/math.sqrt(n_runs))
        aucs.append(result.auc)
        aucstds.append(result.aucstd/math.sqrt(n_runs))
        f1s.append(result.f1)
        f1stds.append(result.f1std/math.sqrt(n_runs))

    print ""
    print "Done in {0:.1f}min".format((time()-t0)/60)
    return mses, msestds, mapes, mapestds, aucs, aucstds, f1s, f1stds


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
        msedata = []
        mseerrors = []
        mapedata = []
        mapeerrors = []
        aucdata = []
        aucerrors = []
        f1data = []
        f1errors = []
        labels = []
        with open(featurefilepath, 'rb') as f:
            features = pickle.load(f)

        csv = StockCsvReader(stockfilepath, pricecolumn, datecolumn)
        targets = tml.targets.get_daily_changes(csv.read(), '2013-01-01',
                                                '2013-12-31')

##        sizes = [1,3,5]
##        offsets = [-2,-1]
##        windows = [list(item) for item in itertools.product(sizes, offsets)]
        windows = [
            (1,-1),(1,-2),(1,-3),
            (2,-1),(2,-2),(2,-3),
            (3,-1),(3,-2),(3,-3)
            ]
##        windows = [(2,-2),(3,-2)]

        featurename = path.basename(featurefilepath)

        # Method = Dummy with 'mean' strategy
        label = 'DummyR'
        print "Processing {} for {}...".format(featurename, label)
        method = DummyRegressor()
        cv_params = {}
        mses, msestds, mapes, mapestds, aucs, aucstds, f1s, f1stds = calculate(
            features, targets, method, cv_params, windows, window_function,
            n_runs)
        msedata.append(mses)
        mseerrors.append(msestds)
        mapedata.append(mapes)
        mapeerrors.append(mapestds)
        aucdata.append(aucs)
        aucerrors.append(aucstds)
        f1data.append(f1s)
        f1errors.append(f1stds)
        labels.append(label)

        # Method = SVR
        label = 'SVR'
        print "Processing {} for {}...".format(featurename, label)
        method = SVR()
        cv_params = {'kernel': ['linear'], 'C': np.logspace(-2,2,5)}
        mses, msestds, mapes, mapestds, aucs, aucstds, f1s, f1stds = calculate(
            features, targets, method, cv_params, windows, window_function,
            n_runs)
        msedata.append(mses)
        mseerrors.append(msestds)
        mapedata.append(mapes)
        mapeerrors.append(mapestds)
        aucdata.append(aucs)
        aucerrors.append(aucstds)
        f1data.append(f1s)
        f1errors.append(f1stds)
        labels.append(label)

        # Method = lasso
        label = 'lasso'
        print "Processing {} for {}...".format(featurename, label)
        method = LassoCV(normalize=True, max_iter=100, n_jobs=-1)
        cv_params = {}
        mses, msestds, mapes, mapestds, aucs, aucstds, f1s, f1stds = calculate(
            features, targets, method, cv_params, windows, window_function,
            n_runs, force_dense=True)
        msedata.append(mses)
        mseerrors.append(msestds)
        mapedata.append(mapes)
        mapeerrors.append(mapestds)
        aucdata.append(aucs)
        aucerrors.append(aucstds)
        f1data.append(f1s)
        f1errors.append(f1stds)
        labels.append(label)

        # Method = KRR
        label = 'KRR'
        print "Processing {} for {}...".format(featurename, label)
        method = KernelRidge()
        cv_params = {'kernel': ['linear'], 'alpha': np.logspace(-2,2,5)}
        mses, msestds, mapes, mapestds, aucs, aucstds, f1s, f1stds = calculate(
            features, targets, method, cv_params, windows, window_function,
            n_runs)
        msedata.append(mses)
        mseerrors.append(msestds)
        mapedata.append(mapes)
        mapeerrors.append(mapestds)
        aucdata.append(aucs)
        aucerrors.append(aucstds)
        f1data.append(f1s)
        f1errors.append(f1stds)
        labels.append(label)

        # handle MSE scores
        msedata = np.array(msedata).T
        mseerrors = np.array(mseerrors).T
        fig = tml.utility.multi_group_bar_chart(
            data=msedata,
            errors=mseerrors,
            setting_labels=[str(x) for x in windows],
            source_labels=labels,
            x_label='Windows',
            y_label='MSE',
            title='MSE by Window and Feature for {}'.format(featurename),
            ylim = 'auto')
        figures.append(fig)

        # handle MAPE scores
        mapedata = np.array(mapedata).T
        mapeerrors = np.array(mapeerrors).T
        fig = tml.utility.multi_group_bar_chart(
            data=mapedata,
            errors=mapeerrors,
            setting_labels=[str(x) for x in windows],
            source_labels=labels,
            x_label='Windows',
            y_label='MAPE',
            title='MAPE by Window and Feature for {}'.format(featurename),
            ylim = 'auto')
        figures.append(fig)

        # handle AUC scores
        aucdata = np.array(aucdata).T
        aucerrors = np.array(aucerrors).T
        fig = tml.utility.multi_group_bar_chart(
            data=aucdata,
            errors=aucerrors,
            setting_labels=[str(x) for x in windows],
            source_labels=labels,
            x_label='Windows',
            y_label='AUC',
            title='AUC by Window and Feature for {}'.format(featurename),
            ylim = 'auto')
        figures.append(fig)

        # handle F1 scores
        f1data = np.array(f1data).T
        f1errors = np.array(f1errors).T
        fig = tml.utility.multi_group_bar_chart(
            data=f1data,
            errors=f1errors,
            setting_labels=[str(x) for x in windows],
            source_labels=labels,
            x_label='Windows',
            y_label='F1',
            title='F1 by Window and Feature for {}'.format(featurename),
            ylim = 'auto')
        figures.append(fig)

        # backup all data
        window_labels = [str(x) for x in windows]
        data_backup.append({
            'Plot Type': 'Multi Group Bar Chart',
            'data': msedata,
            'errors': mseerrors,
            'setting_labels': window_labels,
            'source_labels': labels,
            'x_label': 'Windows',
            'y_label': 'MSE',
            'featurename': featurename,
            'title': 'MSE by Window and Feature for {}'.format(featurename),
            'ylim': 'auto'
            })
        data_backup.append({
            'Plot Type': 'Multi Group Bar Chart',
            'data': mapedata,
            'errors': mapeerrors,
            'setting_labels': window_labels,
            'source_labels': labels,
            'x_label': 'Windows',
            'y_label': 'MAPE',
            'featurename': featurename,
            'title': 'MAPE by Window and Feature for {}'.format(featurename),
            'ylim': 'auto'
            })
        data_backup.append({
            'Plot Type': 'Multi Group Bar Chart',
            'data': aucdata,
            'errors': aucerrors,
            'setting_labels': window_labels,
            'source_labels': labels,
            'x_label': 'Windows',
            'y_label': 'AUC',
            'featurename': featurename,
            'title': 'AUC by Window and Feature for {}'.format(featurename),
            'ylim': 'auto'
            })
        data_backup.append({
            'Plot Type': 'Multi Group Bar Chart',
            'data': f1data,
            'errors': f1errors,
            'setting_labels': window_labels,
            'source_labels': labels,
            'x_label': 'Windows',
            'y_label': 'F1',
            'featurename': featurename,
            'title': 'F1 by Window and Feature for {}'.format(featurename),
            'ylim': 'auto'
            })

    # backup all data to a master "database"
    masterResultPath = 'd:/Dropbox/Studium/MasterThesisGit/Results/master.npz'
    if(path.exists(masterResultPath)):
        with open(masterResultPath) as f:
            masterResultData = pickle.load(f)
    else:
        masterResultData = {}
    for i in range(len(data_backup)/4):
        d = data_backup[i*4]
        msedata = data_backup[i*4]['data']
        mseerrors = data_backup[i*4]['errors']
        mapedata = data_backup[i*4 + 1]['data']
        mapeerrors = data_backup[i*4 + 1]['errors']
        aucdata = data_backup[i*4 + 2]['data']
        aucerrors = data_backup[i*4 + 2]['errors']
        f1data = data_backup[i*4 + 3]['data']
        f1errors = data_backup[i*4 + 3]['errors']
        n_windows, n_methods = msedata.shape
        for w in range(n_windows):
            for m in range(n_methods):
                mr_method = masterResultData.setdefault(d['source_labels'][m],
                                                        {})
                mr_feature = mr_method.setdefault(d['featurename'], {})
                mr_window = mr_feature.setdefault(d['setting_labels'][w], {})
                mr_window['mse'] = msedata[w,m]
                mr_window['mseerror'] = mseerrors[w,m]
                mr_window['mape'] = mapedata[w,m]
                mr_window['mapeerrors'] = mapeerrors[w,m]
                mr_window['auc'] = aucdata[w,m]
                mr_window['aucerror'] = aucerrors[w,m]
                mr_window['f1'] = f1data[w,m]
                mr_window['f1errors'] = f1errors[w,m]

    if(path.exists(masterResultPath)):
        now = datetime.now().strftime("%Y%m%d%H%M%S")
        rename(masterResultPath,
               masterResultPath + '.' + now + '.bak')
    with open(masterResultPath, 'wb') as f:
        pickle.dump(masterResultData, f)

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
        for i in range(len(data_backup)/4):
            msedata = data_backup[i*4]['data']
            mapedata = data_backup[i*4 + 1]['data']
            n_rows, n_columns = msedata.shape
            f.write('%' + data_backup[i*4]['title'] + '\n')
            f.write('\\begin{tabular}{l|' + 'S'*(n_columns*2) + '}\n')
            f.write('  \\toprule\n')
            f.write('  \\multirow{2}{*}{Window} &\n')
            labels = data_backup[i*4]['source_labels']
            for i in range(len(labels)):
                line = '    \\multicolumn{2}{c}{' + labels[i] + '}'
                if i < len(labels)-1:
                    line += ' &\n'
                else:
                    line +=' \\\\\n'
                f.write(line)
            f.write('    ' + '& {MSE} & {MAPE} '*n_columns + '\\\\\n')
            f.write('    \\midrule\n')

            for r in range(n_rows):
                size = str(windows[r][0])
                offset = str(windows[r][1])
                line = '  (' + size + ',' + offset + ') '
                for c in range(n_columns):
                    line += '& {:.2f} & {:.2f} '.format(msedata[r,c],
                                                        mapedata[r,c])
                line += '\\\\\n'
                f.write(line)
            f.write('  \\bottomrule\n')
            f.write('\\end{tabular}\n')
        f.write('\n\n')
        for i in range(len(data_backup)/4):
            msedata = data_backup[i*4 + 2]['data']
            mapedata = data_backup[i*4 + 3]['data']
            n_rows, n_columns = msedata.shape
            f.write('%' + data_backup[i*4]['title'] + '\n')
            f.write('\\begin{tabular}{l|' + 'S'*(n_columns*2) + '}\n')
            f.write('  \\toprule\n')
            f.write('  \\multirow{2}{*}{Window} &\n')
            labels = data_backup[i*4]['source_labels']
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
                    line += '& {:.2f} & {:.2f} '.format(msedata[r,c],
                                                        mapedata[r,c])
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

    main(args, options.stockfile, options.pricecolumn,
         options.datecolumn, options.pdffile,
         window_function, options.reruns)

    winsound.PlaySound('h:/tml/fanfare_x.wav', winsound.SND_FILENAME)
