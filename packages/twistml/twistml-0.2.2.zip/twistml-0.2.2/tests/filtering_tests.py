# -*- coding: utf-8 -*-
r"""Unittests of the functions in the filtering subpackage.

:Author:
    Matthias Manhertz
:Copyright:
    (c) Matthias Manhertz 2015
:Licence:
    MIT
"""

from nose.tools import assert_equal
from twistml.filtering import filter_raw_json
from twistml.filtering import filter_multiple_raw_json
from twistml.filtering import filter_tweets_by_language
from twistml.filtering import filter_tweets_by_category, Category
from os import path, remove, rmdir, listdir, makedirs
import datetime
import filecmp

# locate the files with the sample tweets for testing
testdir = path.join(path.dirname(path.abspath(__file__)),'testfiles')
tempdir = path.join(testdir, 'temp')
testfile = path.join(testdir, 'test_raw_tweets.json')
testfile2 = path.join(testdir, 'test_raw_tweets_copy.json')


def setup():
    if not path.exists(tempdir):
        makedirs(tempdir)
    pass


def teardown():
    if not listdir(tempdir):
        rmdir(tempdir)


def test_filter_raw_json_default():
    r"""Test filter_raw_json() in default mode."""

    data = filter_raw_json(testfile)
    assert_equal(len(data), 7) # 7 of the test tweets have been tagged as 'en'
    pass


def test_filter_raw_json_no_language_filter():
    r"""Test if filter_raw_json() works without language filter"""

    data = filter_raw_json(testfile, filter_language=[])
    assert_equal(len(data), 17) # The test file contains 17 tweets
    pass


def test_filter_raw_json_no_language_filter():
    r"""Test if filter_raw_json() works for multi language filter"""

    data = filter_raw_json(testfile, filter_language=["en","es"])
    assert_equal(len(data), 10) # Test file contains 10 tweets, in 'en' or 'es'
    pass


def test_filter_raw_json_keywords():
    r"""Test if filter_raw_json() can filter keywords."""

    data = filter_raw_json(testfile, filter_words=[' the ','scandal'])
    assert_equal(len(data), 3) # 3 of the 'en' tweets contain one of the words
    pass


def test_filter_raw_json_datafields():
    r"""Test if filter_raw_json() reads the correct datafields."""

    data = filter_raw_json(testfile, ['text', 'created_at','user'])
    for item in data:
        assert_equal(type(item['text']), type(u' '))
        timestamp = datetime.datetime.strptime(item['created_at'],
                                       "%a %b %d %H:%M:%S +0000 %Y")
        assert isinstance(timestamp, datetime.datetime)
        assert isinstance(item['user'], dict)
    pass


def test_multiple_filter():
    r"""Test if filter_multiple_raw_json() works correctly."""

    testfiles = [testfile, testfile2]

    filter_multiple_raw_json(testfiles, tempdir)

    comparefile = testdir + '\\test_filtered_tweets.json'
    resultfiles = []
    for file_ in testfiles:
        resultfiles.append(path.join(tempdir, path.basename(file_)))

    for result in resultfiles:
        assert filecmp.cmp(result, comparefile)
        remove(result)
    pass


def test_filter_tweets_by_language():
    r"""Test the language filter."""

    # setup
    test_tweets = [{'text':u'i am an english tweet.'},
                   {'text':u'je ne suis pas une pomme de terre.'},
                   {'text':u'ich bin ein kleiner grüner kaktus.'},
                   {'text':u'én egy magyar mondat sok beszéddel.'},
                   {'text':u'asdfgh jkl qwertzuiop yxcv bnm.'}]
    test_langs = ['en', 'fr', 'de', 'hu']

    # run
    test_tweets = filter_tweets_by_language(test_tweets, test_langs)

    # test
    assert_equal(len(test_tweets),4)
    for i in range(4):
        tweet = test_tweets[i]
        assert_equal(tweet['ldig_lang'],test_langs[i])

    pass

def test_filter_tweets_by_catgory():
    r"""Test the category filter"""

    # setup
    test_tweets = [{'text':'i feel like having pancakes with maple sirup.'},
                   {'text':'my new apple watch makes me soooo happy.'},
                   {'text':'google, apple and microsoft all suck equally.'},
                   {'text':'i have the feeling android is superior to ios.'},
                   {'text':'google knows everything.'}]
    categories = []
    categories.append(Category('feeling', ['feel','makes me']))
    categories.append(Category('apple', ['apple','ios']))
    categories.append(Category('google', ['google','android']))

    # run
    filename = 'cat_test.json'
    filter_tweets_by_category(test_tweets, testdir, filename, categories)

    # test
    for cat in ['feeling', 'apple', 'google']:
        comparefile = path.join(testdir,'expected_cat_{}.json'.format(cat))
        resultfile = path.join(testdir, cat, filename)
        assert filecmp.cmp(resultfile, comparefile)
    pass


def test_save_load_categories():
    r"""Test the saving and loading of categories."""

    # setup
    categories = []
    categories.append(Category('feeling', ['feel','makes me']))
    categories.append(Category('apple', ['apple','ios']))
    categories.append(Category('google', ['google','android']))

    testfilepath = path.join(tempdir, 'test.cat')

    # run
    Category.save_categories_to_json(categories, testfilepath)
    cats = Category.load_categories_from_json(testfilepath)

    # test
    for i in range(len(cats)):
        assert_equal(cats[i], categories[i])
    remove(testfilepath)
    pass
