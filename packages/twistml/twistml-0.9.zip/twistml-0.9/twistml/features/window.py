r"""Contains the Window class and related functions.

    <extended summary>

    <routine listings>

    <see also>

    <notes>

    <references>


    Examples
    --------
    Suppose we have our features X = {|x1|, ..., |xn|} and our targets
    Y = {|y1|, ..., |yn|}. Using a Window of size 4 with offset 0, we
    can generate alternative features Z = {|z1|, ..., |zn|}, where

        |zi| = some_function(|xi|, |xi-1|, |xi-2|, |xi-3|), with i =
        {4, ..., n}.

    For a Window of size 3 with offset 0:

        |zi| = some_function(|xi|, |xi-1|, |xi-2|)

    For a Window of size 3 with offset -1:

        |zi| = some_function(|xi-1|, |xi-2|, |xi-3|)

    .. |x1| replace:: x\ :sub:`1`\
    .. |xn| replace:: x\ :sub:`n`\
    .. |y1| replace:: y\ :sub:`1`\
    .. |yn| replace:: y\ :sub:`n`\
    .. |z1| replace:: y\ :sub:`1`\
    .. |zn| replace:: y\ :sub:`n`\
    .. |zi| replace:: y\ :sub:`i`\
    .. |xi| replace:: x\ :sub:`i`\
    .. |xi-1| replace:: x\ :sub:`i-1`\
    .. |xi-2| replace:: x\ :sub:`i-2`\
    .. |xi-3| replace:: x\ :sub:`i-3`\

:Author:
    Matthias Manhertz
:Copyright:
    (c) Matthias Manhertz 2015
:Licence:
    MIT
"""

import numpy as np
import scipy.sparse as sps
from datetime import timedelta
from ..utility.utility import generate_datesequence


class Window():
    r"""

    """

    def __init__(self, size, offset):
        r"""Initialize a Window.

        Parameters
        ----------
        size : int
            The size of the window.
        offset : int
            The offset of the window.
        """
        if size < 1:
            raise ValueError("Window.size must be at least 1!")
        self.size = size
        self.offset = offset


def window_element_sum(window_features):
    r"""Calculates an element wise sum of mutiple np.arrays."""

    return reduce(np.add, window_features)


def window_element_avg(window_features):
    r"""Calculates an element wise sum of mutiple np.arrays."""

    return reduce(np.add, window_features) / len(window_features)


def window_stack(window_features):
    r"""Horizontally stacks multiple np.arrays or sparse matrices."""

    if sps.issparse(window_features[0]):
        return sps.hstack(window_features)
    else:
        return np.hstack(window_features)


def get_windowed(features, targets, window,
                 window_function=window_element_sum):
    r"""Generate a new, windowed feature vector for each target.

        Parameters
        ----------
        features : dict[datetime, array_like]
            A dictionary with datetimes for keys and arrays for values.
        targets : dict[datetime, float or class_id]
            A dictionary with datetimes for keys and either floats for
            values (for regression tasks) or class ids (for
            classification tasks.
        window : Window
            An instance of the Window class.
        window_function : callable, optional
            The function that will be used to combine the features
            within a windows. The function needs to take a list of
            array_likes as argument (actually a list of whatever type
            the values of the `features` array are) and return a single
            array_like (the new "windowed" feature vector).
            (Default is window_element_sum, which simply calculates the
            element wise sum of all arrays within a window.)

        Returns
        -------
        X : list[array_like]
            A list of the new windowed features. The exact type is
            determined by the `window_function`.
        y : list[float or class_id]
            A list of corresponding target values.
        dates : list[datetime]
            A list of the corresponding timestamps.

    """

    day = timedelta(days=1)
    X = []
    y = []
    dates = []
    for target_date in targets:
        window_intact = True
        win_start = target_date - day*(window.size-1) + day*window.offset
        win_end = target_date + day*window.offset
        win_dates = generate_datesequence(win_start, win_end,
                                          informat=None, outformat=None)
        win_features = []
        for win_date in win_dates:
            if win_date in features:
                win_features.append(features[win_date])
            else:
                window_intact = False
                break
        if window_intact:
            X.append(window_function(win_features))
            y.append(targets[target_date])
            dates.append(target_date)
        else:
            continue

    # sort everything by date
    dates, X, y = (list(t) for t in zip(*sorted(zip(dates, X, y))))

    return X, y, dates
