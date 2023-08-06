r"""Unittests of the functions in the features subpackage.

:Author:
    Matthias Manhertz
:Copyright:
    (c) Matthias Manhertz 2015
:Licence:
    MIT
"""

from nose.tools import assert_equal, raises
from os import path
from twistml.features.combine import combine_tweets, combine_sentiments
from twistml.features.combine import stack_features
from twistml.features.countvector_transformer import CountVectorTransformer
from twistml.features.doc2vec_transformer import Doc2VecTransformer
from twistml.features.sentiment_transformer import SentimentTransformer
from twistml.features.feature_transformer import FeatureTransformer
from twistml.features.window import Window, get_windowed
from twistml.features.window import window_stack, window_element_avg
from datetime import datetime
from scipy.sparse import csr_matrix, isspmatrix_csr
import numpy as np
from datetime import datetime

testdir = path.join(path.dirname(path.abspath(__file__)), 'testfiles')


def test_combine_tweets():
    r"""Test combine_tweets"""

    combined = combine_tweets([path.join(testdir, 'test_combine.json')])

    assert_equal(combined[datetime.strptime('2013-01-10','%Y-%m-%d')],
                 'this is correct ')
    assert_equal(combined[datetime.strptime('2013-01-11','%Y-%m-%d')],
                 'and so is this ')
    pass


def test_combine_sentiments():
    r"""Assert that combine_sentiments() returns ndarrays of correct shape"""

    combined = combine_sentiments([path.join(testdir, 'test_combine.json')])
    combined2 = combine_sentiments([path.join(testdir, 'test_combine.json')],
                                   analyzer='naivebayes')
    assert_equal(combined[datetime.strptime('2013-01-10','%Y-%m-%d')].shape,
                 (3,2))
    assert_equal(combined[datetime.strptime('2013-01-11','%Y-%m-%d')].shape,
                 (4,2))
    assert_equal(combined2[datetime.strptime('2013-01-10','%Y-%m-%d')].shape,
                 (3,2))
    assert_equal(combined2[datetime.strptime('2013-01-11','%Y-%m-%d')].shape,
                 (4,2))
    pass


@raises(ValueError)
def test_combine_sentiments_unknown_analyzer():
    combined2 = combine_sentiments([path.join(testdir, 'test_combine.json')],
                                   analyzer='UnknownAnalyzer')
    pass


def test_stack_features():
    date1 = datetime.strptime('2013-01-10','%Y-%m-%d')
    date2 = datetime.strptime('2013-01-11','%Y-%m-%d')
    f1 = {date1 : np.asarray([[1,0]]), date2 : np.asarray([[0,0]])}
    f2 = {date1 : np.asarray([[1,1]]), date2 : np.asarray([[0,1]])}
    stacked = stack_features([f1, f2])
    assert np.array_equal(stacked[date1], np.asarray([[1,0,1,1]]))
    assert np.array_equal(stacked[date2], np.asarray([[0,0,0,1]]))
    pass

def test_stack_features_sparse():
    date1 = datetime.strptime('2013-01-10','%Y-%m-%d')
    date2 = datetime.strptime('2013-01-11','%Y-%m-%d')
    f1 = {date1 : csr_matrix((1,4)), date2 : csr_matrix((1,4))}
    f2 = {date1 : csr_matrix((1,4)), date2 : csr_matrix((1,4))}
    stacked = stack_features([f1, f2], sparse=True, sparse_format='csr')
    assert_equal(stacked[date1].shape, (1,8))
    assert_equal(stacked[date2].shape, (1,8))
    pass

@raises(ValueError)
def test_stack_features_keys_dont_match():
    date1 = datetime.strptime('2013-01-10','%Y-%m-%d')
    date2 = datetime.strptime('2013-01-11','%Y-%m-%d')
    date3 = datetime.strptime('2013-01-12','%Y-%m-%d')
    f1 = {date1 : np.asarray([1,0]), date2 : np.asarray([0,0])}
    f2 = {date1 : np.asarray([1,1]), date3 : np.asarray([0,1])}
    stacked = stack_features([f1, f2])
    pass

def test_feature_transformer_fit():
    r"""Make sure FeatureTransformer.fit() returns self unchanged"""
    ftr = FeatureTransformer()
    ftrfit = ftr.fit(None)
    assert_equal(ftr, ftrfit)


@raises(ValueError)
def test_countvectortransformer_illegal_arg():
    r"""Test if the CountVectorTransformer correctly raises a
        ValueError for illegal arguments."""
    cvt = CountVectorTransformer(yomomma='fat')
    pass


def test_countvectortransformer_transform():
    r"""Test the transform method of CountVectorTransformer."""
    cvt = CountVectorTransformer()
    filepaths = [path.join(testdir, 'test_combine.json')]
    features = cvt.transform(filepaths)
    assert isinstance(features[datetime.strptime('2013-01-10','%Y-%m-%d')],
                      csr_matrix)
    assert isinstance(features[datetime.strptime('2013-01-11','%Y-%m-%d')],
                      csr_matrix)
    for key, value in features.iteritems():
        assert_equal(value.shape, (1,5))
    pass


@raises(ValueError)
def test_doc2vectransformer_illegal_arg():
    r"""Test if the Doc2VecTransformer correctly raises a
        ValueError for illegal arguments."""
    d2v = Doc2VecTransformer(yomomma='fat')
    pass


def test_doc2vectransformer_transform():
    r"""Test the transform method of Doc2VecTransformer."""
    d2v = Doc2VecTransformer()
    filepaths = [path.join(testdir, 'test_combine.json')]
    features = d2v.transform(filepaths)
    assert isinstance(features[datetime.strptime('2013-01-10','%Y-%m-%d')],
                      np.ndarray)
    assert isinstance(features[datetime.strptime('2013-01-11','%Y-%m-%d')],
                      np.ndarray)
    for key, value in features.iteritems():
        assert_equal(value.shape, (1,100))

    pass


def test_sentimenttransformer_transform_pattern():
    r"""Test the transform method of SentimentTransformer."""
    snt = SentimentTransformer(analyzer='pattern')
    filepaths = [path.join(testdir, 'test_combine.json')]
    features = snt.transform(filepaths)
    assert isinstance(features[datetime.strptime('2013-01-10','%Y-%m-%d')],
                      np.ndarray)
    assert isinstance(features[datetime.strptime('2013-01-11','%Y-%m-%d')],
                      np.ndarray)
    for key, value in features.iteritems():
        assert_equal(value.shape, (1,4))

    pass

def test_sentimenttransformer_transform_bayes():
    r"""Test the transform method of SentimentTransformer."""
    snt = SentimentTransformer(analyzer='pattern')
    filepaths = [path.join(testdir, 'test_combine.json')]
    features = snt.transform(filepaths)
    assert isinstance(features[datetime.strptime('2013-01-10','%Y-%m-%d')],
                      np.ndarray)
    assert isinstance(features[datetime.strptime('2013-01-11','%Y-%m-%d')],
                      np.ndarray)
    for key, value in features.iteritems():
        assert_equal(value.shape, (1,4))

    pass


def test_get_windowed_sum():
    r"""Test the get_windowed function with window function
    element_sum"""

    # generate some test data
    dates = ['2013-01-01', '2013-01-02', '2013-01-03', '2013-01-04',
             '2013-01-05', '2013-01-07', '2013-01-08', '2013-01-09']
    targets = {}
    features = {}
    for i in range(len(dates)):
        date = datetime.strptime(dates[i], '%Y-%m-%d')
        dates[i] = date
        targets[date] = i
        features[date] = np.ones((1,10)) * (i+1)

    # perform test
    win = Window(3,0)
    X, y, outdates = get_windowed(features, targets, win)

    # assert
    expected_outdates = [dates[i] for i in [2,3,4,7]]
    assert_equal(expected_outdates, outdates)

    assert_equal(len(X), 4)
    expected_outsums = [6, 9, 12, 21]
    for i in range(len(X)):
        print X[i]
        print np.ones((1,10)) * expected_outsums[i]
        assert (X[i] == np.ones((1,10)) * expected_outsums[i]).all()

    assert_equal(y, [2,3,4,7])

    pass


def test_get_windowed_avg():
    r"""Test the get_windowed function with window function
    element_avg"""

    # generate some test data
    dates = ['2013-01-01', '2013-01-02', '2013-01-03', '2013-01-04',
             '2013-01-05', '2013-01-07', '2013-01-08', '2013-01-09']
    targets = {}
    features = {}
    for i in range(len(dates)):
        date = datetime.strptime(dates[i], '%Y-%m-%d')
        dates[i] = date
        targets[date] = i
        features[date] = np.ones((1,10)) * (i+1)

    # perform test
    win = Window(3,0)
    X, y, outdates = get_windowed(features, targets, win,
                                  window_function=window_element_avg)

    # assert
    expected_outdates = [dates[i] for i in [2,3,4,7]]
    assert_equal(expected_outdates, outdates)

    assert_equal(len(X), 4)
    expected_outavgs = [2, 3, 4, 7]
    for i in range(len(X)):
        print X[i]
        print np.ones((1,10)) * expected_outavgs[i]
        assert (X[i] == np.ones((1,10)) * expected_outavgs[i]).all()

    assert_equal(y, [2,3,4,7])

    pass


def test_get_windowed_stack():
    r"""Test the get_windowed function with window function hstack"""

    # generate some test data
    dates = ['2013-01-01', '2013-01-02', '2013-01-03', '2013-01-04',
             '2013-01-05', '2013-01-07', '2013-01-08', '2013-01-09']
    targets = {}
    features = {}
    for i in range(len(dates)):
        date = datetime.strptime(dates[i], '%Y-%m-%d')
        dates[i] = date
        targets[date] = i
        features[date] = np.ones((1,2)) * (i+1)

    # perform test
    win = Window(3,0)
    X, y, outdates = get_windowed(features, targets, win,
                                  window_function=window_stack)

    # assert
    expected_outdates = [dates[i] for i in [2,3,4,7]]
    assert_equal(expected_outdates, outdates)

    assert_equal(len(X), 4)
    expected_out = [
        np.array([[1.,1.,2.,2.,3.,3.]]),
        np.array([[2.,2.,3.,3.,4.,4.]]),
        np.array([[3.,3.,4.,4.,5.,5.]]),
        np.array([[6.,6.,7.,7.,8.,8.]])]
    for i in range(len(X)):
        print X[i]
        print expected_out[i]
        assert (X[i] == expected_out[i]).all()

    assert_equal(y, [2,3,4,7])

    pass
