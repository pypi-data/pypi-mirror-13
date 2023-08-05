r"""Uses ldig to perform language filtering of tweets.

    ldig is an external module written by Nakatani Shuyo to perform
    language detection especially on tweets. The module is not
    extensively documented and therefore difficult to adapt to one's
    special needs.
    This module represents a sort of interface to ldig that allows
    to perform language detectiong on a list of tweets, instead of
    a specially formatted text-file.

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

from .ldig.ldig import ldig
from .ldig.ldig import predict as ldig_predict_language
from .ldig.ldig import normalize_twitter as ldig_normalize_twitter
from os import path
import numpy as np
import re


def filter_tweets_by_language(tweets, languages=['en'],
                              field_to_filter='text',
                              logger=None):
    r"""Filters a list of tweets by language. Returns the filtered list.

        The `tweets` list contains a dict for each tweet. The ldig
        algorithm is applied to the `field_to_filter` of each tweet
        and only the once that are found to be in one of the languages
        specified in `languages` are retained.

        Parameters
        ----------
        tweets : list[dict[str, str]]
            A list of dicts containing twitter data (tweet text and
            some metadata).
        languages : list[str], optional
            A list of two-letter language tags (e.g. 'en', 'de',...)
            specifying the laguage-filters. (Default is ['en'], which
            implies only English tweets are retained.)
        field_to_filter : str, optional
            The (meta)data field in the `tweets` dict to be used for
            filtering. (Default is 'text', which implies the tweet body
            will be used for filtering.)
        logger : logging.Logger, optional
            A logger object, used to display / log console output
            (default is None, which implies quiet execution).

        Returns
        -------
        filtered_tweets : list[dict[str, str]]
            A list of dict containing the twitter data of the filtered
            tweets.

        <Notes>

        <References>

        <Examples>
    """

    # Ideally this would be replaced by using pkgutil.get_data(),
    # but that would have meant to seriously alter the ldig module iself.
    modelpath = path.join(path.dirname(path.abspath(__file__)),
                          'ldig',
                          'modeldata')

    assert path.exists(modelpath), "Directory not found: {}".format(modelpath)

    language_detector = ldig(modelpath)

    trie = language_detector.load_da()
    param = np.load(language_detector.param)
    labels = language_detector.load_labels()
    ldig_args = [trie, param, labels]

    tweets = [x for x in tweets if _lang(x, ldig_args) in languages]

    return tweets


def _lang(tweet, ldig_args, threshold=0.95):
    r"""Detects the language of a tweet using ldig."""

    trie, param, labels = ldig_args
    text = _normalize_text(tweet['text'])
    events = trie.extract_features(u"\u0001" + text + u"\u0001")
    y = ldig_predict_language(param, events)
    predict_k = y.argmax()
    if y[predict_k] < threshold:
        return None
    else:
        tweet['ldig_lang'] = labels[predict_k]
        return labels[predict_k]


def _normalize_text(s):
    s = re.sub(u'[\u2010-\u2015]', '-', s)
    s = re.sub(u'[0-9]+', '0', s)
    s = re.sub(u'[^\u0020-\u007e\u00a1-\u024f\u0300-\u036f\u1e00-\u1eff]+',
               ' ', s)
    s = re.sub(u'  +', ' ', s)
    s = ldig_normalize_twitter(s)
    return s.strip()
