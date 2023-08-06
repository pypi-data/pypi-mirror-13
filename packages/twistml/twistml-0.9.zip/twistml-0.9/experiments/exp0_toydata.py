r"""<summary>

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

from twistml.utility.toydata import create_toy_data
from twistml import find_files
from datetime import datetime
import json
import numpy as np
import matplotlib.mlab as mlab
import matplotlib.pyplot as plt
import math
from matplotlib.backends.backend_pdf import PdfPages


def main():
    r"""<Summary>

        <Extended Summary>

        Parameters
        ----------
        x : int, optional
            Description of parameter `x` (the default is -1, which
            implies summation over all axes).

        Returns
        -------
        int
            Description of anonymous integer return value.

        <Notes>

        <References>

        <Examples>
    """

    # setup
##    targetdate1 = datetime.strptime('2013-01-10', '%Y-%m-%d')
##    targetdate2 = datetime.strptime('2013-01-11', '%Y-%m-%d')
##    targetdate3 = datetime.strptime('2013-01-12', '%Y-%m-%d')
##    targetdate4 = datetime.strptime('2013-01-13', '%Y-%m-%d')
##    targetdate5 = datetime.strptime('2013-01-14', '%Y-%m-%d')
##    targetdate6 = datetime.strptime('2013-01-15', '%Y-%m-%d')
##    targetdate7 = datetime.strptime('2013-01-16', '%Y-%m-%d')
##    targets = {targetdate1: -1.0,
##               targetdate2: 1.0,
##               targetdate3: 0.1,
##               targetdate4: -0.8,
##               targetdate5: 0.2,
##               targetdate6: 0.7,
##               targetdate7: 0.9}
    targetdate1 = datetime.strptime('2013-01-31', '%Y-%m-%d')
    targetdate2 = datetime.strptime('2013-02-01', '%Y-%m-%d')
    targetdate3 = datetime.strptime('2013-01-12', '%Y-%m-%d')
    targetdate4 = datetime.strptime('2013-02-03', '%Y-%m-%d')
    targetdate5 = datetime.strptime('2013-02-04', '%Y-%m-%d')
    targetdate6 = datetime.strptime('2013-02-05', '%Y-%m-%d')
    targetdate7 = datetime.strptime('2013-02-06', '%Y-%m-%d')
    targets = {targetdate1: -1.0,
               targetdate2: 1.0,
               targetdate3: 0.1,
               targetdate4: -0.8,
               targetdate5: 0.2,
               targetdate6: 0.7,
               targetdate7: 0.9}
    keywords = ['the dow', 'the DJI', 'the stock market', 'stocks',
                'the market', 'wall street', 'stock indices', 'market indexes']


    # create data
##    create_toy_data(targets, 'd:/temp/', keywords, 10000, 4.0)


    #read data

    pos = []
    neg = []
    filepaths = find_files('d:/temp/', fromdate='2013-01-01', todate='2013-02-10')
    for filepath in filepaths:
        with open(filepath) as f:
            tweets = json.load(f)
            pos.extend([_lag(x, targetdate7) for x in tweets if x['pos']])
            neg.extend([_lag(x, targetdate7) for x in tweets if not x['pos']])



    # generate the histogram of the data
    fig1 = plt.figure()
    bins = np.linspace(-40, 0, 41)
    p,b1,patches1 = plt.hist(pos, bins, alpha=0.5, facecolor='#69BE28',
                             label='Positive')
    n,b2,patches2 = plt.hist(neg, bins, alpha=0.5, facecolor='#002244',
                             label='Negative')

    print p.shape
    print p[20:40]
    print p[20:40].shape


    # add a 'best fit' line
##    y = mlab.normpdf( bins, mu, sigma)
##    l = plt.plot(bins, y, 'r--', linewidth=1)

    plt.xlabel('Smarts')
    plt.ylabel('Probability')
    plt.title(r'$\mathrm{Histogram\ of\ IQ:}\ \mu=100,\ \sigma=15$')
    plt.grid(True)

    fig2 = plt.figure()
    ind = np.arange(8)    # the x locations for the groups
    width = 1.0       # the width of the bars: can also be len(x) sequence

    p1 = plt.bar(ind, p[7:15], width, color='#69BE28')
    p2 = plt.bar(ind, n[7:15], width, color='#002244', bottom=p[7:15])

    plt.ylabel('Number of Tweets')
    plt.title('Positive and Negative Tweets per Day in the Toy Data Set')
    x_tick_labels = ('2013-01-04', ' ', '2013-01-06', ' ',
                     '2013-01-08', ' ', '2013-01-10', ' ',
                     '2013-01-12', ' ', '2013-01-11', ' ',
                     '2013-01-13', ' ', '2013-01-15')
    plt.xticks(ind + width/2., x_tick_labels, ha='right', rotation=40)
##    plt.yticks(np.arange(0, 81, 10))
    plt.legend((p1[0], p2[0]), ('Positive', 'Negative'))
    fig2.tight_layout()
    #plt.show()

    # export plots to pdf
    pp = PdfPages('d:/temp/histogram.pdf')
    pp.savefig(fig2)
    pp.close()

    pass

def _lag(tweet, tgtdate):
    fmt = "%a %b %d %H:%M:%S +0000 %Y"
    key = 'created_at'
    tweetdate = datetime.strptime(tweet[key], fmt)
    seconds = (tweetdate-tgtdate).total_seconds()
    minutes = seconds / float(60)
    hours = minutes / float(60)
    days = hours / float(24)
    return math.floor(days)

if __name__ == '__main__':
    main()
