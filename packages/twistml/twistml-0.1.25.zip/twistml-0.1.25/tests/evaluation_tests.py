r"""Unittests of the functions in the features subpackage.

:Author:
    Matthias Manhertz
:Copyright:
    (c) Matthias Manhertz 2015
:Licence:
    MIT
"""

from nose.tools import assert_equal
from twistml import evaluate_binary_classification
from sklearn.svm import SVC
import numpy as np


def generate_toy_data(n, dim, min_pc,):
    r"""Generates a toy data set for testing"""
    # determine two sets of mean / cov for two different gaussian distributions
    mean1 = np.ones((dim,)) * 1
    mean2 = np.ones((dim,)) * 2
    cov1 = np.identity(dim)
    cov2 = np.identity(dim)

    # generate data points randomly from either of the gaussians
    num1 = np.random.randint(1,n - (2*min_pc)) + min_pc
    gaus1 = np.random.multivariate_normal(mean1, cov1, num1)
    gaus2 = np.random.multivariate_normal(mean2, cov2, n-num1)
    X = np.concatenate((gaus1, gaus2), axis=0)

    # generate targets to go with data points
    targets1 = np.ones((num1,))
    targets2 = np.zeros((n-num1,))
    y = np.concatenate((targets1, targets2), axis=0)

    return X, y


def test_evaluate_binary_classification():
    r"""Test the evaluation function for binary classification"""

    X, y = generate_toy_data(100, 10, 20)
    svc = SVC(probability=True)
    cvparams = {'kernel': ['linear'], 'C': [1, 10, 100, 1000]}
    result = evaluate_binary_classification(X, y, svc, cvparams, 10)
    print("AUC: {} | STD: {}".format(result.auc, result.aucstd))
    assert result.auc > 0.8
    assert result.aucstd < 0.2

