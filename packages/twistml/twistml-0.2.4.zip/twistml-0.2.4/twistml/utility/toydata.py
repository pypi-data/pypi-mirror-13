r"""Contains functions / classes to create toy datasets fot twistml.

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

from twistml.utility import remap
from random import random, gauss, choice
from datetime import timedelta
from os import path
import json


def create_toy_data(targets, outdir, keywords, tweets_per_target=1000,
                    lag=4.0):
    r"""Creates a set of tweets for the given targets and saves them to
    disk.

    Parameters
    ----------
    targets : dict[datetime,float]
        The percentual change in stock price for each datetime stamp.
    outdir : str
        The full path to a directory where the .json files with the
        generated tweets should be saved.
    tweet_per_target : int, optional
        How many tweets will be generated per target value.
    lag : float, optional
        How many days should the tweets precede the stock prices.
        (Default is 4.0, which implies tweets are on average made four
        days before the corresponding change in stock price.)
    """

    tweets = {}
    min_target_value = min(targets.values())
    max_target_value = max(targets.values())
    lag_delta = timedelta(days=lag)

    for target_date, pricechange in targets.iteritems():
        change01 = remap(pricechange, min_target_value, max_target_value)
        for i in range(tweets_per_target):
            is_positive = random() < change01
            tweet_text = _create_tweet_text(is_positive, keywords)
            tweet_date = _create_tweet_date(target_date - lag_delta)
            tweet_datestamp = tweet_date.strftime("%a %b %d %H:%M:%S +0000 %Y")
            tweet_date = tweet_date.replace(hour=0, minute=0, second=0,
                                            microsecond=0)
            if tweet_date not in tweets:
                tweets[tweet_date] = []
            tweets[tweet_date].append({'text': tweet_text,
                                       'created_at': tweet_datestamp})

    for date, day_tweets in tweets.iteritems():
        filename = date.strftime('%Y-%m-%d') + '.json'
        filepath = path.join(outdir, filename)
        with open(filepath, 'wb') as f:
            json.dump(day_tweets, f)

    pass


def _create_tweet_text(is_positive, keywords):
    r"""Returns either a positive or a negative tweet text."""

    source = choice(sources)
    verb = choice(verbs)
    keyword = choice(keywords)
    tense = choice(tenses)

    if is_positive:
        pred = choice(pos_pred)
    else:
        pred = choice(neg_pred)

    tweet_text = ' '.join([source, verb, keyword, tense, pred])

    return tweet_text


def _create_tweet_date(center, sigma_in_days=1.0):
    r"""Creates a random date normally distributed around a given date.

    Parameters
    ----------
    center : datetime
        The datetime around which to center the gaussian distribution,
        i.e. the mu of the gaussian.
    sigma_in_days : float, optional
        The sigma of the gaussian expressed in days. (default is 1.0,
        which implies 68% of sampled dates will be within one day of
        `center`, 95% within two days and 99.7% within 3 days.)

    Returns
    -------
    datetime
        A datetime randomly sampled from a gaussian distribution,
        centered a `center` with a sigma of `sigma_in_days`.

    """

    sigma = timedelta(days=sigma_in_days).total_seconds()
    delta_in_seconds = gauss(0.0, sigma)
    delta = timedelta(seconds=delta_in_seconds)
    return center + delta


sources = ['I', 'Do You', 'Your Momma', 'My Daddy', 'I have a friend who',
           'The New York Times', 'Scientists', 'The Wall Street Journal',
           'Donald Trump', 'The public', 'Fortune 500 CEOs',
           'The man on the street', 'Everybody', 'The Internet', 'Wiki Leaks',
           'Wikipedia', 'That one website', 'Some guy on facebook']

verbs = ['feel', 'say', 'state', 'claim', 'predict', 'pronounce', 'foresee',
         'announce', 'write', 'expect', 'think', 'know', 'release']

tenses = ['will', 'is going to', 'should', 'could']

pos_pred = ['perform well', 'be great', 'increase', 'be awesome', 'improve',
            'accomplish good things', 'grow impressively', 'be amazing',
            'have many advantages', 'outperform its competition',
            'be beneficial for investors', 'provide handsome returns']

neg_pred = ['perform badly', 'be weak', 'decrease', 'be awefull',
            'deteriorate', 'accomplish only bad things', 'shrink dramatically',
            'be disappointing', 'have only disadvantages', 'underperform',
            'be catastrophic for investors', 'provide shocking losses']
