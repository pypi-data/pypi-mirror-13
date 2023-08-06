# -*- coding: utf-8; -*-
#
# test/test_tutorial.py
# Part of Gajja, a Python test double library.
#
# Copyright © 2016 Ben Finney <ben+python@benfinney.id.au>
#
# This is free software: you may copy, modify, and/or distribute this work
# under the terms of the GNU General Public License as published by the
# Free Software Foundation; version 3 of that license or any later version.
# No warranty expressed or implied. See the file ‘LICENSE.GPL-3’ for details.

""" Test suite for tutorial examples. """

from __future__ import (absolute_import, unicode_literals)

import os
import os.path
import doctest

__package__ = str("test")
__import__(__package__)

this_dir = os.path.dirname(__file__)
doc_dir = os.path.join(os.path.pardir, "doc")


def load_tests(loader, tests, pattern):
    """ Test discovery hook to load test cases for this module.

        :param loader: The `unittest.TestLoader` instance to use for
            loading test cases.
        :param tests: Collection of cases already loaded for this
            module.
        :param pattern: File glob pattern to match test modules.
        :return: A `unittest.TestSuite` instance comprising the
            modified test suite for this module.

        See the `load_tests protocol`_ section of the Python
        `unittest` documentation.

        ..  _load_tests protocol:
            https://docs.python.org/3/library/unittest.html#load-tests-protocol

        """
    tutorial_file_path = os.path.join(doc_dir, "tutorial.txt")
    tests.addTests(doctest.DocFileSuite(
            tutorial_file_path,
            optionflags=doctest.NORMALIZE_WHITESPACE))

    return tests


# Local variables:
# coding: utf-8
# mode: python
# End:
# vim: fileencoding=utf-8 filetype=python :
