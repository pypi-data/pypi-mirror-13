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

from twistml.features.sentence2vec.word2vec import Word2Vec
import json
import re


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

    with open('d:/twitterdata/2013-01-21_EnglishTimeTextOnly.json') as f:
        data = json.load(f)

    texts = []
    i = 0
    for d in data:
        text = d['text']
        text = re.sub(r"(?:\@|https?\://)\S+", "", text)
        text = re.sub(r"[^\x00-\x7F]+", " ", text)
        texts.append(text)
        i += 1
        print "{}/{}      \r".format(i, len(data)),
        if i >= 100000:
            break;

    model = Word2Vec(texts, min_count=2)

    pass

if __name__ == '__main__':
    main()
