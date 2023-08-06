#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""SciExp² version information."""

__author__ = "Lluís Vilanova"
__copyright__ = "Copyright 2013-2016, Lluís Vilanova"
__license__ = "GPL version 3 or later"

__maintainer__ = "Lluís Vilanova"
__email__ = "vilanova@ac.upc.edu"


__version_info__ = (1, 1, 3)
__version__ = ".".join([str(i) for i in __version_info__])


CLASSIFIERS = [
    "Development Status :: 4 - Beta",
    "Environment :: Console",
    "Intended Audience :: Science/Research",
    "License :: OSI Approved :: GNU General Public License (GPL)",
    "Programming Language :: Python",
    "Topic :: Scientific/Engineering",
]


_description = "Scientific Experiment Exploration framework"

# taken from doc/introduction.rst
_long_description = """\
SciExp² (aka *SciExp square* or simply *SciExp2*) stands for *Scientific
Experiment Exploration*, which contains a comprehensive framework for easing
the workflow of creating, executing and evaluating experiments.

The driving idea behind the provided abstractions is that of the need for quick
and effortless *design-space exploration*. That is, the definition and
evaluation of experiments that are based on the permutation of different
parameters in the design space.

The framework is available in the form of Python modules which can be
integrated into your own applications, but also comes with some interfaces to
allow for quick writing without having to import a whole set of modules and
instantiate objects of their corresponding classes.
"""


NAME = "sciexp2"
VERSION = __version__
DESCRIPTION = _description
LONG_DESCRIPTION = _long_description
AUTHOR = __author__
AUTHOR_EMAIL = __email__
MAINTAINER = __maintainer__
MAINTAINER_EMAIL = __email__
URL = "https://projects.gso.ac.upc.edu/projects/sciexp2"
LICENSE = "GNU General Public License (GPL) version 3 or later"
PACKAGES = ["sciexp2", "sciexp2.common", "sciexp2.launchgen", "sciexp2.system",
            "sciexp2.data", "sciexp2.data.io"]
PACKAGE_DATA = {"sciexp2": ["templates/*.dsc", "templates/*.tpl"]}
SCRIPTS = ["launcher"]
REQUIRES = ["python (>=2.7)", "numpy", "ply", "ipython", "six"]
PROVIDES = ["sciexp2"]

INSTALL_REQUIRES = [req.replace("(", "").replace(")", "") for req in REQUIRES]
