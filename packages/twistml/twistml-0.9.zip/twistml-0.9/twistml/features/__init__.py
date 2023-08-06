r"""<package summary>

    <extended summary>

    <module listings>

:Author:
    Matthias Manhertz
:Copyright:
    (c) Matthias Manhertz 2015
:Licence:
    MIT
"""

# flake8: noqa

from .countvector_transformer import CountVectorTransformer
from .window import get_windowed, Window
from .doc2vec_transformer import Doc2VecTransformer
from .sentiment_transformer import SentimentTransformer
from .combine import stack_features
from .feature_transformer import FeatureTransformer