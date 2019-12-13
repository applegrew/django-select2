Contributing
============

This package uses the pyTest test runner. To run the tests locally simply run::

    python setup.py test

If you need to the development dependencies installed of you local IDE, you can run::

    python setup.py develop

Documentation pull requests welcome. The Sphinx documentation can be compiled via::

    python setup.py build_sphinx

Bug reports welcome, even more so if they include a correct patch.  Much
more so if you start your patch by adding a failing unit test, and correct
the code until zero unit tests fail.

The list of supported Django and Python version can be found in the CI suite setup.
Please make sure to verify that none of the linters or tests failed, before you submit
a patch for review.
