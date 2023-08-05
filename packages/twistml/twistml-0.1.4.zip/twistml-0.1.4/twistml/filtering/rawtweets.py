r"""Main module for all preprocessing steps in twistml

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

from time import time
import json
from os import path, makedirs

def filter_multiple_raw_json(filepaths, outdir,
                    meta_fields=['text', 'created_at'],
                    filter_words=[],
                    filter_language=['en'],
                    logger=None):
    r"""Filters raw twitter .json files and writes filtered files.

        Reads twitter data from multiple raw twitter .json files,
        discarding all tweets that do not contain at least one of the
        words from `filter_words` and those that are not in one of the
        `filter_language' languages. Keeps only the `meta_fields`of the
        remaining tweets.
        Writes the filtered tweets to `outdir` keeping the original
        filenames.

        Parameters
        ----------
        filepaths : list[str]
            Full paths to the .json files to be read.
        outdir : str
            Full path to the directory, the filtered tweets will be
            written to. **Needs to end with '/'!**
        meta_fields : list[str], optional
            Contains the names of the twitter data fields to be read.
            See the twitter documentation for a list of fields.
            (Default is ['text', 'created_at'], which filters the tweet
            text and timestamp.)
        filter_words : list[str], optional
            A list of keywords. Only tweets containing at least of the
            keywords, are considered elligible for further processing
            (default is [], which implies all tweets are elligible).
        filter_language : list[str], optional
            Tweets that do not have at least one of the fields
            *lang* or *user.lang* set to one of the languages in the
            list are discarded. An empty list means no language
            filtering will be applied. (Default is ['en'], which
            filters all English tweets)
        logger : logging.Logger, optional
            A logger object, used to display / log console output
            (default is None, which implies quiet execution).

    """

    # make sure the outdir exists, if not create it
    if not path.exists(outdir):
        makedirs(outdir)
        if logger is not None:
            logger.info("{} did not exist. Creating it.".format(outdir))

    for filepath in filepaths:
        data = filter_raw_json(filepath, meta_fields, filter_words,
                               filter_language, logger)
        outpath = outdir + path.basename(filepath)
        with open(outpath, 'w') as outfile:
            json.dump(data, outfile)

    pass

def filter_raw_json(filepath,
                    meta_fields=['text', 'created_at'],
                    filter_words=[],
                    filter_language=['en'],
                    logger=None):
    r"""Reads from a single raw twitter .json. Returns a list of dicts.

        Reads twitter data from `filepath`, discarding all tweets that
        do not contain at least one of the words from `filter_words`
        and those that are not in one of the `filter_language'
        languages. Keeps only the `meta_fields`of the remaining tweets.
        Returns a list containing a dict[str, str] for each tweet. Each
        dict holds the fields specified in `meta_fields`.

        Parameters
        ----------
        filepath : str
            Full path to the .json file to be read.
        meta_fields : list[str], optional
            Contains the names of the twitter data fields to be read.
            See the twitter documentation for a list of fields.
            (Default is ['text', 'created_at'], which filters the tweet
            text and timestamp.)
        filter_words : list[str], optional
            A list of keywords. Only tweets containing at least of the
            keywords, are considered elligible for further processing
            (default is [], which implies all tweets are elligible).
        filter_language : list[str], optional
            Tweets that do not have at least one of the fields
            *lang* or *user.lang* set to one of the languages in the
            list are discarded. An empty list means no language
            filtering will be applied. (Default is ['en'], which
            filters all English tweets)
        logger : logging.Logger, optional
            A logger object, used to display / log console output
            (default is None, which implies quiet execution).

        Returns
        -------
        list[dict[str, str]]
            A list of dicts (one per tweet). Each dict has
            `meta_fields` as keys and the corresponding field content
            as values.

    """

    if logger is not None:
        logger.info('Filtering {}...'.format(filepath))

    t0 = time()
    data = []
    lines_in_part = 0
    broken_entries = 0
    processed_entries = 0
    read_entries = 0

    with open(filepath, 'r') as json_string:
        partial = ''
        old = ''
        for line in json_string:
            partial += line.rstrip('\n')
            try:  # we cant be sure partial contains a complete json entry
                entry = json.loads(partial)
            except ValueError, e: # indeed partial was not complete
                lines_in_part += 1
                # experience showed, that it was more likely entries of more
                # than two lines were corrupted, than not. So we skip those.
                if lines_in_part >= 2:
                    partial = ''
                    broken_entries = broken_entries + 1
                continue  # Not yet a complete JSON value
            extracted_data = _extract_metadata(entry, meta_fields, filter_words,
                                               filter_language, logger)
            if extracted_data is not None:
                data.append(extracted_data)
                read_entries += 1
            processed_entries += 1
            lines_in_part = 0
            partial = ''

    if logger is not None:
        _log_result_of_filter_raw_json(logger, time() - t0,
            broken_entries, read_entries, processed_entries
        )

    return data

def _extract_metadata(tweet, fields, keywords, languages, logger):
    r"""Extracts metadata from a single raw tweet and returns a dict."""

    if len(languages) > 0:
        if not _is_tweet_in_language(tweet, languages):
            return None

    tweet['text'] = tweet['text'].lower()
    if any(x in tweet['text'] for x in keywords) or keywords == []:
        d = {}
        for field in fields:
            if tweet.has_key(field):
                d[field] = tweet[field]
            else:
                d[field] = None
                if logger is not None:
                    logger.warning(
                        "Field '{}' not present in tweet.".format(keyword)
                    )
        return d
    else:
        return None

def _is_tweet_in_language(tweet, languages):
    r"""Checks if the tweet has one of the language tags. Returns True or False."""

    # Check if twitter has classified the tweet.
    if tweet.has_key('lang'):
        if tweet['lang'] in languages:
            return True
        else:
            return False

    # Only use the user setting, if twitter has not classified the tweet.
    if tweet.has_key('user') and tweet['user'].has_key('lang'):
        if tweet['user']['lang'] in languages:
            return True

    return False

def _log_result_of_filter_raw_json(logger, runtime, broken, read, processed):
    r"""Provides output of results for filter_raw_json."""

    logger.info("...done in {}s".format(runtime))
    logger.info("{0} lines were corrupted.".format(broken))
    logger.info("{0}k of {1}k tweets have been processed.".format(
        read/1000, processed/1000)
    )
    pass

