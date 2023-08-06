r"""Base class for feature generation. Inherit from this to implement
    custom feature transformers for twistml.

:Author:
    Matthias Manhertz
:Copyright:
    (c) Matthias Manhertz 2015
:Licence:
    MIT
"""

from sklearn.base import TransformerMixin, BaseEstimator


class FeatureTransformer(BaseEstimator, TransformerMixin):
    r"""FeatureTransformer is a base class for Transformers that generate
        complex features from tweets.

        The intention is to have many different Transformers that
        inherit from `FeatureTransformer` and that can be
        interchangeably used in sklearn Pipelines. Child classes have
        to implement the transform() method required by sklearn
        Transformers.

        fit() is inherited as empty method (FeatureTransformers should
        not usually need to fit to the data and fit_transform() is
        automatically inherited from TransformerMixin.

        BaseEstimator provides get_params and set_params, which make
        the generators copy-able, so they can be used in multiple-jobs
        like in a GridSearchCV.

        See Also
        --------
        Stackoverflow_
        ZacStewart_
        scikit-learn_

        .. _Stackoverflow: http://stackoverflow.com/questions/27810855/
        .. _ZacStewart: http://zacstewart.com/2014/08/05/pipelines-of-featureunions-of-pipelines.html
        .. _scikit-learn: http://scikit-learn.org/stable/auto_examples/hetero_feature_union.html

        Examples
        --------
        See CountVectorTransformer for a possible implementation.

    """  # NOQA

    def fit(self, X, y=None, **fit_params):
        return self

    pass
