Hints to Developers
=========================

Documentation pull requests welcome.

Please do not add the "missing" Makefile.  That is intentionally so.
Compile the docs locally by ways of ``python setup.py build_sphinx``.

Bug reports welcome, even more so if they include a correct patch.  Much
more so if you start your patch by adding a failing unit test, and correct
the code until zero unit tests fail.

Please note: the test suite uses the newly introduced f-strings, so that it
needs Python3.6+ to run.  The code itself is targeted at Python3.5+.

