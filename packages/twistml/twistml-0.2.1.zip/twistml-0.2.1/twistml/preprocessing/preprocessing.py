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

import re
from nltk.tokenize import WordPunctTokenizer
from nltk.corpus import wordnet, stopwords
from nltk.stem import PorterStemmer


def preprocess_tweets(tweets,
                      remove_twitter=True,
                      remove_stopwords=True,
                      remove_nonenglish=True,
                      perform_stemming=True):
    r"""Preprocess a list of tweets for processing in a machine
        learning task.

        A series of preprocessing steps will be applied to the given
        tweets that are generally viewed as being beneficial for
        machine learning tasks. The steps include the removal of
        twitter specific tokens (like links and @-mentions), removal of
        stopwords, removal of non English words and stemming.

        Each of these steps can be individually disabled by setting
        the corresponding parameter to False. Though not all
        combinations of enabled / disabled parameters have been tested
        and for some combinations the results may not be as desired.

        Parameters
        ----------
        tweets : list[dict[str,str]]
            The tweets to be preprocessed.
        remove_twitter : bool
            If twitter specific tokens (links, @mentions) will be
            removed (default is True)
        correct_spelling : bool
            If spelling correction will be applied to the `tweets`
            (default is True)
        remove_stopwords : bool
            If stopwords will be removed from the `tweets` (default
            is True)
        remove_nonenglish : bool
            If non English words (names, uncorrected misspellings, ...)
            will be removed (default is True)
        perform_stemming : bool
            If stemming will be performed on the `tweets` (default is
            True)

        Returns
        -------
        tweets : list[dict[str,str]]
            The preprocessed tweets

    """

    def _need_to_tokenize():
        r"""If we want to remove stopwords, remove non English words or
            or perform stemming, we will nee to tokenize the texts."""

        return (remove_stopwords or remove_nonenglish or perform_stemming)

    # some stuff we only need to do once for all tweets
    if _need_to_tokenize():
        wpt = WordPunctTokenizer()
    if remove_stopwords:
        sws = stopwords.words('english')
    if perform_stemming:
        stemmer = PorterStemmer()

    for tweet in tweets:
        text = tweet['text']

        # remove links, @-mentions etc
        if remove_twitter:
            text = re.sub(r"(?:\@|https?\://)\S+", "", text)

        # remove non ASCII chars
        text = re.sub(r"[^\x00-\x7F]+", " ", text)

        # decode unicode
        text = text.decode('utf-8')

        # the next three steps require tokenization
        if _need_to_tokenize:
            words = wpt.tokenize(text)

            # remove stopwords
            if remove_stopwords:
                words = [w for w in words if w not in sws and len(w) > 1]

            # remove non English words
            if remove_nonenglish:
                words = [w for w in words if (wordnet.synsets(w))]

            # perform stemming
            if perform_stemming:
                words = [stemmer.stem(w) for w in words]

        # rejoin tokens
        text = ' '.join(words)

        # remove unnecessary white space
        text = ' '.join(text.split())

        # back to unicode
        text = text.encode('utf-8')

        # write resulting text back to the tweet
        tweet['text'] = text

    return tweets
