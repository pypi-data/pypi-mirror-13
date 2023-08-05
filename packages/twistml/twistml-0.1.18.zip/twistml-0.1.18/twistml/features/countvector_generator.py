r"""CountVectorGenerator uses
    sklearn.feature_extraction.text.CountVectorizer to generate count
    vector features (Bag of Words, n-grams, ...).

:Author:
    Matthias Manhertz
:Copyright:
    (c) Matthias Manhertz 2015
:Licence:
    MIT
"""

from sklearn.feature_extraction.text import CountVectorizer
from .feature_generator import FeatureGenerator

class CountVectorGenerator(FeatureGenerator):
    r"""Generates count vector features (e.g. bag of words)

        <Extended Summary>

        <Notes>

        <References>

        <Examples>
    """

    def __init__(self, countvectorizerparamstuffgoeshere):
##        self.countvectorparams = countvectorizerparamstuffgoeshere
        pass

    def transform(self, filepaths):
##        tweets = perform_magic(filepaths)
##        vectorizer = CountVectorizer(tweets, self.countvectorparams)
##        countvector_features = vectorizer.fit_transform(tweets)
##        return countvector_features
        pass

    pass

