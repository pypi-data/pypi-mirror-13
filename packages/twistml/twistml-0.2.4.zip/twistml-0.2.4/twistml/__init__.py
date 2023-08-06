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

from .filtering.rawtweets import filter_multiple_raw_json as filter_raw
from .filtering.category import filter_tweets_by_category as filter_categories
from .filtering.language import filter_tweets_by_language as filter_languages

from .preprocessing.preprocessing import preprocess_tweets

from .utility.utility import setup_logger
from .utility.utility import find_files
from .utility.utility import progress_report

from .evaluation.evaluation import evaluate_binary_classification
from .evaluation.evaluation import evaluate_regression

from . import features
from . import targets
from . import utility