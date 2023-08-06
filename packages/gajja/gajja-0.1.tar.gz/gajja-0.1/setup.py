# -*- coding: utf-8; -*-

# setup.py
# Part of Gajja, a Python test double library.
#
# Copyright © 2008–2016 Ben Finney <ben+python@benfinney.id.au>
#
# This is free software: you may copy, modify, and/or distribute this work
# under the terms of the GNU General Public License as published by the
# Free Software Foundation; version 3 of that license or any later version.
# No warranty expressed or implied. See the file ‘LICENSE.GPL-3’ for details.

""" Distribution setup for Gajja code base. """

from __future__ import (absolute_import, unicode_literals)

import sys
import os
import os.path
import types
import pydoc
import email.utils

from setuptools import (setup, find_packages)

__metaclass__ = type


class SimpleNamespace:
    """ A simple attribute-based namespace. """


setup_dir = os.path.dirname(__file__)

changelog = SimpleNamespace()
changelog.package = "gajja"
changelog.version = "0.1"
changelog.author = "Ben Finney <ben+python@benfinney.id.au>"
(author_name, author_email) = email.utils.parseaddr(changelog.author)

control_structure = dict()
control_structure['maintainer'] = changelog.author
(maintainer_name, maintainer_email) = email.utils.parseaddr(
        control_structure['maintainer'])
control_structure['homepage'] = "https://notabug.org/bignose/python-gajja"

copyright_structure = SimpleNamespace()
license = SimpleNamespace()
license.synopsis = "GPLv3+"
copyright_structure.license = license

main_module = __import__(changelog.package)
(synopsis, long_description) = pydoc.splitdoc(pydoc.getdoc(main_module))


setup(
        name=changelog.package,
        version=str(changelog.version),
        packages=find_packages(exclude=["test"]),

        # Setuptools metadata.
        maintainer=maintainer_name,
        maintainer_email=maintainer_email,
        zip_safe=False,
        setup_requires=[
            "python-debian",
            ],
        test_suite="unittest2.collector",
        tests_require=[
            "unittest2 >=0.5.1",
            "testtools",
            "mock >=1.3",
            ],
        install_requires=[
            "setuptools",
            "unittest2 >=0.5.1",
            "testtools",
            "mock >=1.3",
            ],

        # PyPI metadata.
        author=author_name,
        author_email=author_email,
        description=synopsis,
        license=license.synopsis,
        keywords="test double fake mock filesystem subprocess".split(),
        url=control_structure['homepage'],
        long_description=long_description,
        classifiers=[
            # Reference: http://pypi.python.org/pypi?%3Aaction=list_classifiers
            "Development Status :: 3 - Alpha",
            "License :: OSI Approved :: GNU General Public License v3 or later (GPLv3+)",
            "Operating System :: POSIX",
            "Programming Language :: Python :: 2.7",
            "Programming Language :: Python :: 3.3",
            "Programming Language :: Python :: 3.4",
            "Programming Language :: Python :: 3.5",
            "Intended Audience :: Developers",
            "Topic :: Software Development :: Testing",
            ],
        )


# Local variables:
# coding: utf-8
# mode: python
# End:
# vim: fileencoding=utf-8 filetype=python :
