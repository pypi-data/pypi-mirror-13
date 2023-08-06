TwistML
=======

TwistML is a package that makes it easier to work with raw twitter data
for machine learning tasks, like predicting changes in the stock 
market.

TwistML implements a pipeline that includes filtering of the twitter 
data, preprocessing, feature extraction into several feature 
representations (bag of words, sentiments, Doc2Vec), regression / 
classification using algorithms from the sklearn package, and
model selection / evaluation.

The API documentation is available at `TwistML's PyPI page 
<https://pypi.python.org/pypi/twistml>`_. A more usage focuse
documentation is coming soon, until then you can get the full package
from BitBucket (also linked at the PyPI page) and check out the 
experiments folder for some usage examples.

TwistML was developed as part of my master's thesis and I hope to keep
improving it afterwards.

Installation
------------
You can use pip to install TwistML like so::

	$ pip install twistml

Please make you sure you **have numpy, scipy and gensim installed** as
well. I have opted out of adding them to the install_requires as this
has caused problems in my own tests on windows machines. (For numpy the
problem is described `here
<https://github.com/numpy/numpy/issues/2434>`_.) So these packages will
not be installed automatically by pip.
