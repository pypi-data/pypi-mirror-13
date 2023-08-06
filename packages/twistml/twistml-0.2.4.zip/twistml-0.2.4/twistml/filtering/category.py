r"""Filter tweets into categories.

    A category consists of a name and a list of keywords, e.g.::
        exmpl_cat = {'name':'feeling', 'keywords':['feel','makes me']}

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
from os import path, makedirs


class Category:
    r"""Combines multiple keywords into a named catgory.

    A category has a name and a list of keywords both of which have to
    be passed to the construtor. The Category class provides functions
    to save to and load from a .json file and defines equality /
    inequality between categories.

    """

    def __init__(self, name, keywords):
        self.name = name
        self.keywords = keywords

    def __eq__(self, other):
        return ((self.name, self.keywords) == (other.name, other.keywords))

    def __ne__(self, other):
        return not self == other

    @staticmethod
    def save_categories_to_json(categories, filename):
        r"""Saves a list of categories to a file in JSON-format."""

        data = [{'name': c.name, 'keywords': c.keywords} for c in categories]
        with open(filename, 'wb') as jsonfile:
            json.dump(data, jsonfile)

        pass

    @staticmethod
    def load_categories_from_json(filename):
        r"""Loads a list of categories from a file in JSON-format."""

        categories = []
        with open(filename, 'rb') as jsonfile:
            data = json.load(jsonfile)
            categories = [Category(d['name'], d['keywords']) for d in data]
        return categories


def filter_tweets_by_category(tweets, outdir, filename, categories='default',
                              fields=['text'], logger=None):
    r"""Filters a list of tweets into categories, saves the results to
        files and returns a list of those files.

        For each category in `categories` this function discards those
        tweets in `tweets` that do not contain at least one of the
        'category.keywords' in at least one of the specified
        `fields` and saves the rest into a directory 'category.name'
        inside `outdir` as `filename`.

        Parameters
        ----------
        tweets : list[dict[str, str]]
            A list of tweets in dict form (like one might obtain from
            the rawtweets-module.
        outdir : str
            The full path to the directory into which the result will
            be saved. Subdirectories for each Category will be created
            as needed.
        filename : str
            The filename the resulting list of tweets will be saved
            under.
        categories : list[Category], optional
            A list of categories. For each Category the `tweets` will
            be filtered by the keywords of that category and saved
            into a directory named after the category.
            (Default is 'default', which means a default list of
            categories will be generated.)
        fields : list[str], optional
            The fields of the tweets that will be checked against each
            Category's keywords. (Default is ['text'], which implies
            only the tweet's text body will be checked.)
        logger : logging.Logger, optional
            A logger object, used to display / log console output
            (default is None, which implies quiet execution).

        Returns
        -------
        outputfiles : list[str]
            A list of all the filepaths that were written as a result.

    """

    if categories == 'default':
        categories = _create_default_categories()

    outputfiles = []

    for cat in categories:
        keys = cat.keywords

        catdir = path.join(outdir, cat.name)
        if not _directory_ok(catdir, logger):
            if logger is not None:
                logger.warning("Skipping Category: {}".format(cat.name))
            continue

        filtered_tweets = [t for t in tweets if _contains(t, keys, fields)]

        savepath = path.join(catdir, filename)
        with open(savepath, 'wb') as jsonfile:
            json.dump(filtered_tweets, jsonfile)
        outputfiles.append(savepath)

    return outputfiles


def _directory_ok(directory, logger):
    r"""Checks if the directory exists or creates it. Returns False
        it doesn't exist and cannot be created."""

    if not path.exists(directory):
        makedirs(directory)  # Possible race condition!?
    if not path.isdir(directory):
        if logger is not None:
            logger.warning("Problems with directory: {}".format(directory))
        return False

    return True


def _contains(tweet, keys, fields):
    r"""Returns true if the tweet contains any of the keywords in any
        of its meta_fields."""

    return any(k in tweet[f] for k in keys for f in fields)


def _create_default_categories():
    categories = []
    categories.append(Category('index', ['index', 'indices', 'indeces']))
    categories.append(Category('iphone', ['iphone']))
    categories.append(Category('ipad', ['ipad']))
    categories.append(Category('android', ['android']))
    categories.append(Category('samsung', ['samsung']))
    categories.append(Category('atapple', ['@apple']))
    categories.append(Category('ios', ['ios']))
    categories.append(Category('microsoft', ['microsoft']))
    categories.append(Category('$msft', ['$msft']))
    categories.append(Category('windows', ['windows']))
    categories.append(Category('google', ['google']))
    categories.append(Category('feeling', [' feel ', 'feeling', 'makes me']))
    categories.append(Category('gmail', ['gmail', 'googlemail']))
    categories.append(Category('adwords', ['adwords']))
    categories.append(Category('microsoft', ['microsoft']))
    categories.append(Category('dow', [' dow ', 'djia']))
    categories.append(Category('stock', [' stock ']))
    categories.append(Category('market', ['market']))
    categories.append(Category('wallstreet', ['wall street']))
    return categories
