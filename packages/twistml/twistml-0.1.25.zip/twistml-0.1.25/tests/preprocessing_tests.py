# -*- coding: utf-8 -*-
r"""Unittests of the functions in the preprocessing subpackage.

:Author:
    Matthias Manhertz
:Copyright:
    (c) Matthias Manhertz 2015
:Licence:
    MIT
"""

from nose.tools import assert_equal
from twistml.preprocessing import preprocess_tweets

def test_preprocess_single_tweet():

    test_tweets = [{'text':u'i am an exciting english tweet. @yomomma äöü'}]
    test_tweets = preprocess_tweets(test_tweets)
    assert_equal(test_tweets[0]['text'], u'excit english tweet')

    pass

def test_preprocess_full():

    test_tweets = [{'text':u'i am an exciting english tweet. @yomomma äöü'},
                   {'text':u'stemming is fun at http://www.nltk.org'},
                   {'text':u'my name is matthias manhertz'}]
    expected_results =    [u'excit english tweet',
                           u'stem fun',
                           u'name']
    test_tweets = preprocess_tweets(test_tweets)
    for i in range(3):
        assert_equal(test_tweets[i]['text'], expected_results[i])

    pass

def test_preprocess_dont_remove_twitter():

    test_tweets = [{'text':u'i am an exciting english tweet. @yomomma äöü'},
                   {'text':u'stemming is fun at http://www.nltk.org'},
                   {'text':u'my name is matthias manhertz'}]
    expected_results =    [u'excit english tweet',
                           u'stem fun http www',
                           u'name']
    test_tweets = preprocess_tweets(test_tweets, remove_twitter=False)
    for i in range(3):
        assert_equal(test_tweets[i]['text'], expected_results[i])

    pass

def test_preprocess_dont_remove_stopwords():

    test_tweets = [{'text':u'i am an exciting english tweet. @yomomma äöü'},
                   {'text':u'stemming is fun at http://www.nltk.org'},
                   {'text':u'my name is matthias manhertz'}]
    expected_results =    [u'i am an excit english tweet',
                           u'stem is fun at',
                           u'name is']
    test_tweets = preprocess_tweets(test_tweets, remove_stopwords=False)
    for i in range(3):
        assert_equal(test_tweets[i]['text'], expected_results[i])

    pass

def test_preprocess_dont_remove_nonenglish():

    test_tweets = [{'text':u'i am an exciting english tweet. @yomomma äöü'},
                   {'text':u'stemming is fun at http://www.nltk.org'},
                   {'text':u'my name is matthias manhertz'}]
    expected_results =    [u'excit english tweet',
                           u'stem fun',
                           u'name matthia manhertz']
    test_tweets = preprocess_tweets(test_tweets, remove_nonenglish=False)
    for i in range(3):
        assert_equal(test_tweets[i]['text'], expected_results[i])

    pass

def test_preprocess_dont_perform_stemming():

    test_tweets = [{'text':u'i am an exciting english tweet. @yomomma äöü'},
                   {'text':u'stemming is fun at http://www.nltk.org'},
                   {'text':u'my name is matthias manhertz'}]
    expected_results =    [u'exciting english tweet',
                           u'stemming fun',
                           u'name']
    test_tweets = preprocess_tweets(test_tweets, perform_stemming=False)
    for i in range(3):
        assert_equal(test_tweets[i]['text'], expected_results[i])

    pass

