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
from twistml.features.combine_tweets import combine_tweets
from twistml.features.countvector_transformer import CountVectorTransformer
from datetime import datetime
from scipy.sparse import csr_matrix

testdir = path.join(path.dirname(path.abspath(__file__)), 'testfiles')

def test_combine_tweets():
    r"""Test combine_tweets"""

    combined = combine_tweets([path.join(testdir, 'test_combine.json')])

    assert_equal(combined[datetime.strptime('2013-01-10','%Y-%m-%d')],
                 'this is correct ')
    assert_equal(combined[datetime.strptime('2013-01-11','%Y-%m-%d')],
                 'and so is this ')
    pass

@raises(ValueError)
def test_countvectortransformer_illegal_arg():
    cvt = CountVectorTransformer(yomomma='fat')

def test_countvectortransformer_transform():
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