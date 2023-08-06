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

import json
from twistml.features import CountVectorTransformer
from twistml.preprocessing import preprocess_tweets
from os import path
import optparse


def main(unprocessed):
    r"""

    """

    noextension = path.splitext(unprocessed)[0]
    unicode_removed = noextension + '_unicode.json'
    tokens_removed = noextension + '_tokens.json'
    preprocessed = noextension + '_preprocessed.json'

    with open(unprocessed) as f:
        tweets = json.load(f)

    cvt = CountVectorTransformer(use_tfidf=False, analyzer='char',
                                                  ngram_range=(2, 3))
    features = cvt.transform([unprocessed])
    for date, bow in features.iteritems():
        print "Unprocessed: {}".format(bow.shape)

    with open(unicode_removed, 'w') as f:
        t = preprocess_tweets(tweets,
                              remove_twitter=False,
                              remove_stopwords=False,
                              remove_nonenglish=False,
                              perform_stemming=False)
        json.dump(t, f)
    cvt = CountVectorTransformer(use_tfidf=False, analyzer='char',
                                                  ngram_range=(2, 3))
    features = cvt.transform([unicode_removed])
    for date, bow in features.iteritems():
        print "Unicode Removed: {}".format(bow.shape)

    with open(tokens_removed, 'w') as f:
        t = preprocess_tweets(tweets,
                              remove_twitter=True,
                              remove_stopwords=True,
                              remove_nonenglish=True,
                              perform_stemming=False)
        json.dump(t, f)
    cvt = CountVectorTransformer(use_tfidf=False, analyzer='char',
                                                  ngram_range=(2, 3))
    features = cvt.transform([tokens_removed])
    for date, bow in features.iteritems():
        print "Tokens Removed: {}".format(bow.shape)

    with open(preprocessed, 'w') as f:
        t = preprocess_tweets(tweets,
                              remove_twitter=True,
                              remove_stopwords=True,
                              remove_nonenglish=True,
                              perform_stemming=True)
        json.dump(t, f)
    cvt = CountVectorTransformer(use_tfidf=False, analyzer='char',
                                                  ngram_range=(2, 3))
    features = cvt.transform([preprocessed])
    for date, bow in features.iteritems():
        print "Fully Preprocessed: {}".format(bow.shape)

    pass


def _check_file(filepath, name, parser):
    if not filepath:
        parser.error("Please enter a filepath for the {}".format(name))
    if not path.exists(filepath):
        parser.error("{} is not a valid filepath.".format(filepath))
    pass


if __name__ == '__main__':
    usage = 'usage: %prog [options] filepath'
    parser = optparse.OptionParser(usage=usage)

##    parser.add_option("-s", "--stock",
##                      type="string", dest="stockfile",
##                      help=".csv file with the stock data")

    (options, args) = parser.parse_args()

    if not len(args) == 1:
        parser.error("Please enter exactly one filepath for the {}".format(
            'feature file'))
    for featurefile in args:
        _check_file(featurefile, 'feature file', parser)

    main(args[0])
