r"""Uses ldig to perform language filtering of tweets.

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

from .ldig.ldig import normalize_twitter

def filter_tweets_by_language(tweets, languages=['en'],
                              field_to_filter='text'):
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

        Returns
        -------
        filtered_tweets : list[dict[str, str]]
            A list of dict containing the twitter data of the filtered
            tweets.

        <Notes>

        <References>

        <Examples>
    """



    pass

