#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""Command-style functions to work with `~sciexp2.launchgen`.

The typical workflow to work with `~sciexp2.launchgen` is::

    import sciexp2.launchgen

    launchgen = sciexp2.launchgen.Launchgen()
    launchgen.out = ...
    ...
    launchgen.execute(...)
    ...
    launchgen.params(var1 = sciexp2.launchgen.defer("var2"))
    ...
    launchgen.pack(...)
    ...
    launchgen.find_files(...)
    ...
    launchgen.launcher(...)

Using this module provides a simplified command-style environment for such a
common workflow, where a `~sciexp2.launchgen.Launchgen` object has been
instantiated as ``default_launchgen`` and all its methods (together with the
`~sciexp2.launchgen.defer` routine) have been put in the namespace::

    from sciexp2.launchgen.env import *

    default_launchgen.out = ...
    ...
    execute(...)
    ...
    params(var1 = defer("var2"))
    ...
    pack(...)
    ...
    find_files(...)
    ...
    launcher(...)

The helper function `~sciexp2.launcher.file_contents` is also provided,
together with `~sciexp2.common.filter.Filter` and an instance of
`~sciexp2.common.filter.PFilter` named `v_` to help streamlining the writing of
filters.

"""

from __future__ import print_function
from __future__ import absolute_import

__author__ = "Lluís Vilanova"
__copyright__ = "Copyright 2013, Lluís Vilanova"
__license__ = "GPL version 3 or later"

__maintainer__ = "Lluís Vilanova"
__email__ = "vilanova@ac.upc.edu"


__all__ = []


def _env_add(name, value):
    __all__.append(name)
    globals()[name] = value


def _env_setup():
    import sciexp2.launchgen
    import sciexp2.common.filter

    _env_add("Launchgen", sciexp2.launchgen.Launchgen)
    default_launchgen = sciexp2.launchgen.Launchgen()
    _env_add("default_launchgen", default_launchgen)
    for m in dir(default_launchgen):
        if m[0] != "_":
            _env_add(m, getattr(default_launchgen, m))
    _env_add("file_contents", sciexp2.launchgen.file_contents)
    _env_add("defer", sciexp2.launchgen.defer)
    _env_add("Filter", sciexp2.common.filter.Filter)
    _env_add("v_", sciexp2.common.filter.PFilter())

_env_setup()
