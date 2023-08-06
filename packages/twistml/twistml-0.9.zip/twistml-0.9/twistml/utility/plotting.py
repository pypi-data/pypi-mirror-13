r"""Provides functions for creating graphs using matplotlib

:Author:
    Matthias Manhertz
:Copyright:
    (c) Matthias Manhertz 2015
:Licence:
    MIT
"""

import matplotlib.pyplot as plt
import numpy as np
from twistml.utility import float_ceil, float_floor


def multi_group_bar_chart(data, errors, setting_labels, source_labels,
                          x_label, y_label, title,
                          colors=['b', 'g', 'y', 'c', 'r', 'm', 'k', 'w'],
                          ylim=None, loc="lower right", **kwargs):
    r"""Returns a bar chart figure

    The bar chart contains multiple groups of bars. Each group has the
    same number of bars (one for each data source) and represents a
    certain setting. For example the data sources could be different
    machine learning algorithms like SVM or KNN. The setting could be
    different feature representations like bag of words, sentiment
    features or word2vec. In this case the data would have the shape
    (3x2).

    Parameters
    ----------
    data : array-like
        The data that defines the actual bar heights. The shape is
        (n_settings x n_sources).
    errors : array-like
        The data that defines the error bars on each data bar. The
        shape is (n_settings x n_sources).
    setting_labels : list[str]
        A list of labels for the settings. Needs to be of length
        n_settings.
    source_labels : list[str]
        A list of labels for the sources. Needs to be of length
        n_sources.
    x_label : str
        Label for the x-axis.
    y_label : str
        Label for the y-axis.
    title : str
        Title for the whole plot.
    colors : list[str], optional for less than 9 sources
        The colors for the bar faces. Has to have at least as many
        entries as the data has sources. Each source gets it's own
        color in order. Additional colors are discarded.
        (default is ['b','g','y','c','r','m','k','w'])
        To find valid color names check the matplotlib documentation or
        run the following code snippet::
            $ import matplotlib
            $ for colorname in matplotlib.colors.cnames:
            $     print colorname
    ylim : tuple(ymin, ymax) or 'auto' or None, optional
        The min and max values for the y-axis. (Default is None, which
        implies matplotlib can set these automatically.)
        Another option is to specify 'auto', which sets the minimum
        just below the smallest height and the maximum just above the
        largest height, wich often looks better than the matplotlib
        auto setting.

    Returns
    -------
    fig : figure
        A matplotlib figure of the finished bar chart.

    Raises
    ------
    ValueError
        If the shapes of `data`, `errors`, `setting_labels` and
        `source_labels` do not match.

    """

    data = np.array(data)
    errors = np.array(errors)

    # sanity checks
    n_groups, n_types = data.shape
    if not (n_groups, n_types) == errors.shape:
        raise ValueError('Shapes do not match for data and error bars!')
    if not n_groups == len(setting_labels):
        raise ValueError('Wrong number of labels for the groups')
    if not n_types == len(source_labels):
        raise ValueError('Wrong number of labels for the legend')

    # some settings
    index = np.arange(n_groups)
    bar_width = 1.0 / float(n_types + 1)
    error_config = {'ecolor': '0.3'}

    # start plotting
    fig = plt.figure()
    for i in range(n_types):
        plt.bar(left=index + bar_width*(i),
                height=data[:, i],
                width=bar_width,
                color=colors[i],
                yerr=errors[:, i],
                error_kw=error_config,
                label=source_labels[i])
    plt.xlabel(x_label)
    plt.ylabel(y_label)
    plt.title(title)
    if ylim is not None:
        if ylim == 'auto':
            plt.ylim(float_floor(data.min(), 1), float_ceil(data.max(), 1))
        else:
            plt.ylim(ylim[0], ylim[1])
    plt.xticks(index + bar_width*n_types/2, setting_labels, **kwargs)
    plt.legend(loc=loc)
    plt.grid(b=True, which='major', color='k', linestyle='--')
    plt.gca().xaxis.grid(False)
    plt.gca().yaxis.grid(True)
    plt.tight_layout()

    return fig
