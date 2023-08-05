r"""Unittests of the functions in the filtering module.

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
from os import path, remove, rmdir, listdir
import datetime
import filecmp

# locate the file with the sample tweets for testing
testdir = path.dirname(path.abspath(__file__)) + '\\testfiles'
testfile = testdir + '\\test_raw_tweets.json'
testfile2 = testdir + '\\test_raw_tweets_copy.json'

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

    outdir = testdir + '\\temp\\'
    testfiles = [testfile, testfile2]

    filter_multiple_raw_json(testfiles, outdir)

    comparefile = testdir + '\\test_filtered_tweets.json'
    resultfiles = []
    for file_ in testfiles:
        resultfiles.append(outdir + path.basename(file_))

    for result in resultfiles:
        assert filecmp.cmp(result, comparefile)
        remove(result)

    if not listdir(outdir):
        rmdir(outdir)

    pass
