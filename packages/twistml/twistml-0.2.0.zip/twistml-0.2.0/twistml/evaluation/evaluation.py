r"""Contains functions to evaluate regression and classification
    methods

    The given methods can be any machine learning algorithms that
    adhere to sklearn's estimator pattern - this includes sklearn's
    pipelines. The evaluate_ functions will perform a set number of
    cross validations over given parameters and return certain metrics
    (MSE and MAPE for regression, ROC-AUC for binary classification).

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

from collections import namedtuple
from sklearn.grid_search import GridSearchCV
from sklearn.cross_validation import train_test_split
from sklearn.metrics import roc_auc_score, mean_squared_error
import numpy as np
import scipy.sparse as sps


# create named tuples to hold the results of our evaluations
EvalRegrResult = namedtuple("EvalRegrResult", "mse msestd mape mapestd")
EvalBinClassResult = namedtuple("EvalBinClassResult", "auc aucstd")


def evaluate_regression(X, y, method, cv_params, n_runs, **kwargs):
    r"""Runs cross validation on the given regression method. Returns
        evaluation metrics.

        Parameters
        ----------
        X : array_like, shape = (n_samples, n_features)
            The feature vectors
        y : array-like, shape (n_samples,)
            The target values
        method : sklearn.base.BaseEstimator
            An estimator object that is used to compute the
            predictions. Has to provide fit and predict. Can be a
            Pipeline.
        cv_params : dict or list of dicts
            The GridSearchCV param_grid as described in sklearn docs:
            Dictionary with parameters names (string) as keys and lists
            of parameter settings to try as values, or a list of such
            dictionaries, in which case the grids spanned by each
            dictionary in the list are explored. This enables searching
            over any sequence of parameter settings.
        n_runs : int
            Number of times the cross validation will be repeated to
            get averages and standard deviations for the metrics.
        **kwargs : dict of keyword arguments
            These arguments will be passed to GridSearchCV. See the
            sklearn docs for details on which arguments are available.

        Returns
        -------
        EvalRegrResult : named tuple
            The named tuple has the fields `mse`, `msestd`, `mape` and
            `mapestd`, containing the average of the mean squared
            error, the average of the mean absolute percentage error
            and their respective standard deviations over the given
            number of runs.

        Notes
        -----
        Will cause a divide by zero error in MAPE calculation if the
        targets `y` contain any zero entries.
    """

    msescores = []
    mapescores = []
    for i in range(n_runs):
        X_train, X_test, y_train, y_test = train_test_split(
            X, y, test_size=0.2)
        fitted_grid = cross_validate(X_train, y_train, method,
                                     cv_params, **kwargs)
        y_pred = fitted_grid.predict(X_test)
        msescores.append(mean_squared_error(y_test, y_pred))
        mapescores.append(mean_average_percentage_error(y_test, y_pred))

    mse, msestd = _get_mean_std(msescores)
    mape, mapestd = _get_mean_std(mapescores)

    return EvalRegrResult(mse, msestd, mape, mapestd)


def evaluate_binary_classification(X, y, method, cv_params, n_runs,
                                   use_coeff=False, **kwargs):
    r"""Runs cross validation on the given classification method.
        Returns evaluation metrics.

        Parameters
        ----------
        X : array_like, shape = (n_samples, n_features)
            The feature vectors
        y : array-like, shape (n_samples,)
            The target values
        method : sklearn.base.BaseEstimator
            An estimator object that is used to compute the
            predictions. Has to provide fit and predict. Can be a
            Pipeline.
        cv_params : dict or list of dicts
            The GridSearchCV param_grid as described in sklearn docs:
            Dictionary with parameters names (string) as keys and lists
            of parameter settings to try as values, or a list of such
            dictionaries, in which case the grids spanned by each
            dictionary in the list are explored. This enables searching
            over any sequence of parameter settings.
        n_runs : int
            Number of times the cross validation will be repeated to
            get averages and standard deviations for the metrics.
        use_coeff : bool, optional
            To generate sensible AUC values, we need confidence values
            for the predictions. For linear SVMs these can be
            efficiently obtained by multplying the coefficients-vector
            w with the test data. For most other estimators we will use
            the `predict_proba` method.
            Setting `use_coeff` to True, means the `coef_` will be used
            instead of predict_proba(). (default is False)
        **kwargs : dict of keyword arguments
            These arguments will be passed to GridSearchCV. See the
            sklearn docs for details on which arguments are available.

        Returns
        -------
        EvalBinClassResult : named tuple
            The named tuple has the fields `auc` and `aucstd`
            containing the average of the area under the roc curve and
            the respective standard deviation over the given number of
            runs.

    """

    aucscores = []
    for i in range(n_runs):
        X_train, X_test, y_train, y_test = train_test_split(
            X, y, test_size=0.2, random_state=None)
        fitted_grid = cross_validate(X_train, y_train, method,
                                     cv_params, **kwargs)

        if use_coeff:
            w = fitted_grid.best_estimator_.coef_
            if sps.issparse(w):
                w = w.toarray()
            y_proba = X_test.dot(w.ravel().T)
            aucscores.append(roc_auc_score(y_test, y_proba))
        else:
            y_proba = fitted_grid.predict_proba(X_test)
            aucscores.append(roc_auc_score(y_test, y_proba[:, 1]))

    auc, aucstd = _get_mean_std(aucscores)
    return EvalBinClassResult(auc, aucstd)
##    return EvalBinClassResult(1.0, 0.0)

def cross_validate(X, y, method, cv_params, **kwargs):
    r"""Runs cross validation on method and returns fitted GridSearchCV
        instance.

        Parameters
        ----------
        X : array_like, shape = (n_samples, n_features)
            The feature vectors
        y : array-like, shape (n_samples,)
            The target values
        method : sklearn.base.BaseEstimator
            An estimator object that is used to compute the
            predictions. Has to provide fit and predict. Can be a
            Pipeline.
        cv_params : dict or list of dicts
            The GridSearchCV param_grid as described in sklearn docs:
            Dictionary with parameters names (string) as keys and lists
            of parameter settings to try as values, or a list of such
            dictionaries, in which case the grids spanned by each
            dictionary in the list are explored. This enables searching
            over any sequence of parameter settings.
        n_runs : int
            Number of times the cross validation will be repeated to
            get averages and standard deviations for the metrics.
        **kwargs : dict of keyword arguments
            These arguments will be passed to GridSearchCV. See the
            sklearn docs for details on which arguments are available.

        Returns
        -------
        GridSearchCV
            The fitted GridSearchCV instance.

    """

    # extract the arguments that are meant for GridSearchCV()
    gridargs = {key: value for key, value in kwargs.iteritems()
                if key in GridSearchCV.__init__.func_code.co_varnames}

    gscv = GridSearchCV(method, cv_params, **gridargs)
    gscv.fit(X, y)
    return gscv


def mean_average_percentage_error(y_true, y_pred):
    r"""Calculates the mean absolute percentage error.

        Notes
        -----
        This will cause divide by zero error, if `y_true` contains zeroes.

    """

    return np.mean(np.abs((y_true - y_pred) / y_true)) * 100


def _get_mean_std(scores):
    r"""Calculates the mean and std for the given sequence of scores."""

    score_arr = np.array(scores)
    mean = np.mean(score_arr)
    std = np.std(score_arr)
    return mean, std
