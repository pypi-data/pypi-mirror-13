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
from twistml.features.combine_tweets import combine_tweets, combine_sentiments
from twistml.features.countvector_transformer import CountVectorTransformer
from twistml.features.doc2vec_transformer import Doc2VecTransformer
from twistml.features.sentiment_transformer import SentimentTransformer
from twistml.features.feature_transformer import FeatureTransformer
from twistml.features.window import Window, get_windowed, _element_sum
from datetime import datetime
from scipy.sparse import csr_matrix
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
        assert_equal(value.shape, (1,6))

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
        assert_equal(value.shape, (1,6))

    pass


def test_get_windowed():
    r"""Test the get_windowed function."""

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
