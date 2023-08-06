Changes
=======

Version 0.9
-----------

- Changed status to Beta

- Added API documentation generated via sphinx and numpydoc

- Doc2VecTransformer now supports iterative training (as explained 
`here <http://rare-technologies.com/doc2vec-tutorial/>`_)

- Regression evaluation can now treat predictions as binary 
classifications and evaluate AUC and F1

- Changed some command line scripts to have more intuitive usage

- various small fixes


Version 0.2.4
-------------

**ATTENTION: Some of these may break existing code!**!

- renamed combine_tweets.py to combine.py

- added support for stacking of features

- classification targets are now 0 / 1 instead of -1 / 1

- added toydata module -> create some toydata for testing

- added F1-Score to classifcation evaluation

- added additional window functions: window_stack and window_element_avg

Version 0.2.3
-------------

- Improved long_description generation

- Fixed CHANGES.rst

Version 0.2.2
-------------

- Added sentiment features based on TextBlob sentiments

Version 0.2.1
-------------

- Added functionality for complex category subsets to 
  tml-generate-features

- Also improved documentation for tml-generate-features (on cmd line as
  well as docstring)

- improved test coverage 

Version 0.2.0
-------------

- Changed Development Status to Alpha

- Removed Sentence2Vec as that functionality is included in current 
  gensim versions' Doc2Vec class
  
- Added Changelog
