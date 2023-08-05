r"""This module contains functions to combine tweets from multiple
    files into useful data structures (lists, dicts...) for further
    transformation into feature vectors.

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

import json
from datetime import datetime
from cStringIO import StringIO
from time import time


def combine_tweets(filepaths, meta_fields=['text'],
                   timeformat="%a %b %d %H:%M:%S +0000 %Y"):
    r"""<Summary>

        <Extended Summary>

        Parameters
        ----------
        filepaths : list[str]
            A list of filepaths to .json-files containing tweets in the
            format common to twistml. Each tweet must contain at least
            a 'created_at' field and the field specified in
            `meta_fields`.
        meta_fields : list[str]
            A list of meta_fields (keys in the tweet dictionaries).
            These are the fields, whose content will be combined in the
            result. (Default is ['text'], which implies the tweet-texts
            will be combined.)
        Returns
        -------
        daily_texts : dict[str,str]
            The keys are datestamps and the values are the concatenated
            contents of the `meta_fields` of all tweets in `filepaths`
            for that datestamp.

        References
        ----------
        This function uses cStringIO to perform the many string
        concatenations necessary, as this has the best runtime to
        process-size tradeoff as detailed on waymoot.org_.

        .. _waymoot.org : https://waymoot.org/home/python_string/
    """

    daily_texts = {}
    i = 0
    t0 = time()
    print "Combining Tweets"
    for filepath in filepaths:
        with open(filepath) as jsonfile:
            tweets = json.load(jsonfile)

        for tweet in tweets:
            datestamp = datetime.strptime(tweet['created_at'], timeformat)
            # "round down" to the day of the tweet
            datestamp = datestamp.replace(hour=0, minute=0, second=0,
                                          microsecond=0)
            if datestamp not in daily_texts:
                daily_texts[datestamp] = StringIO()
            for field in meta_fields:
                daily_texts[datestamp].write(tweet[field].encode('utf-8'))
                daily_texts[datestamp].write(' ')

        i += 1
        t1 = time() - t0
        print "{0} of {1} done in {2:.1f}s. Est. {3:.1f}m rem.      \r".format(
            i, len(filepaths), t1, t1/i*(len(filepaths)-i)/60),

    print ''
    for datestamp, stringIO in daily_texts.iteritems():
        daily_texts[datestamp] = stringIO.getvalue()
    print "Done in {0:.1f}min.".format((time()-t0)/60)
    return daily_texts
