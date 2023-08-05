TwistML
=======

Disclaimer
----------
This package is still very much under developement. 

At this point most of the intended functionality is in place, but
documentation is still very spotty.

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
