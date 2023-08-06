#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""Progress indicators.

By default, messages are printed into `sys.stderr` (can be changed with
`set_file`), only if the provided level is greater than the one in `level`.

The available levels are: `LVL_NONE`, `LVL_MARK`, `LVL_PROGRESS` (the default),
`LVL_INFO`, `LVL_VERBOSE` and `LVL_DEBUG`.

In order to add the minimum amount of overhead, progress indicators are updated
at a maximum speed of `SPEED` (in seconds).

"""

from __future__ import print_function
from __future__ import absolute_import

__author__ = "Lluís Vilanova"
__copyright__ = "Copyright 2008-2014, Lluís Vilanova"
__license__ = "GPL version 3 or later"

__maintainer__ = "Lluís Vilanova"
__email__ = "vilanova@ac.upc.edu"


import collections
import datetime
import inspect
import itertools
import math
import numbers
import os
import six
import sys
import threading
import types


LVL_NONE = 0                      #: No progress indication.
LVL_MARK = 1                      #: Mark beginning/end of progress indication
LVL_PROGRESS = 2                  #: Show progress indication.
LVL_INFO = 3                      #: Show additional information.
LVL_VERBOSE = 4                   #: Be verbose when progressing.
LVL_DEBUG = 5                     #: Show debugging information.

_LEVEL = LVL_PROGRESS
_FILE = None
_INTERACTIVE = False


def set_file(fobj):
    global _FILE
    _FILE = fobj
    global _INTERACTIVE
    if hasattr(_FILE, "fileno") and os.isatty(fobj.fileno()):
        _INTERACTIVE = True
    else:
        _INTERACTIVE = False

set_file(sys.stderr)


def level(level=None):
    """Get/set the current progress indication level."""
    if level is not None:
        if level < LVL_NONE or LVL_DEBUG < level:
            raise ValueError("Invalid progress level %r" % level)
        global _LEVEL
        _LEVEL = level
    return _LEVEL


def _log(fmt, *args, **kwargs):
    with _print_lock:
        print(fmt, *args,  end="", file=_FILE, **kwargs)

_print_lock = threading.Lock()


def _logclean(length):
    global _LOGCLEAN
    _LOGCLEAN = (" " * length) + "\r"

_LOGCLEAN = ""


def log(level, fmt, *args, **kwargs):
    """Log message with given level."""
    if level > _LEVEL:
        return
    if _INTERACTIVE:
        _log(_LOGCLEAN)
    _log(fmt, *args, **kwargs)


def info(fmt, *args, **kwargs):
    log(LVL_INFO, fmt, *args, **kwargs)


def verbose(fmt, *args, **kwargs):
    log(LVL_VERBOSE, fmt, *args, **kwargs)


def debug(fmt, *args, **kwargs):
    log(LVL_DEBUG, fmt, *args, **kwargs)


#: Speed (in seconds) at which to update progress indicators.
SPEED = 0.2


def _block_get_length(count, length, delta):
    """Get a new block length.

    Smooths sudden changes by not allowing deltas beyond 50%.

    """
    new_length = count / (delta.total_seconds() / SPEED)
    new_length = int(math.ceil(new_length))
    if new_length > length:
        max_length = int(math.ceil(length * 1.5))
        return min(new_length, max_length)
    else:
        max_length = int(math.floor(length * 0.5))
        return max(new_length, max_length)


class Message:
    """A simple progress indicator.

    Parameters
    ----------
    msg : string, optional
        Message to prefix to the progress indicator.

    """

    def __init__(self, total=None, msg=""):
        self._interactive = _INTERACTIVE
        self._msg = " %s" % msg
        if self._interactive:
            self._msg += "\r"
            _log(self._msg)
        else:
            _log(self._msg + "\n")
        self._clean = False
        self._logclean = len(self._msg)
        _logclean(self._logclean)

    def __call__(self, increment=1):
        pass

    def _cleanup(self):
        if self._clean:
            return
        self._clean = True
        if self._interactive:
            length = len(self._msg)
            _log((" " * length) + "\r")
        else:
            _log(self._msg + " done.\n")

    def __enter__(self):
        return self

    def __exit__(self, *args, **kwargs):
        self._cleanup()

    def __del__(self):
        """Delete the progress indicator from screen."""
        self._cleanup()


class Counter:
    """A counting progress indicator.

    Parameters
    ----------
    total : int
        Objective progress count.
    msg : string, optional
        Message to prefix to the progress indicator.

    """

    def __init__(self, total, msg=""):
        self._interactive = _INTERACTIVE
        self._total = total
        self._count = 0
        self._block_last_time = datetime.datetime.now()
        self._block_length = 1
        self._block_count = 0
        self._fmt_msg = " " + msg
        self._fmt = "%s  %%%%%dd / %%d" % (
            self._fmt_msg, len(str(self._total)))
        self._fmt = self._fmt % self._total
        self._clean = False
        if self._interactive:
            self._update = self._update_interactive
        else:
            self._update = self._update_noninteractive
        self._logclean = len(self._fmt % 0)
        _logclean(self._logclean)

    def __call__(self, increment=1):
        """Increment the progress indicator by the given number."""
        if level() < LVL_PROGRESS:
            return

        self._block_count += increment
        if self._block_count >= self._block_length:
            now = datetime.datetime.now()
            delta = now - self._block_last_time
            self._block_last_time = now
            self._block_length = _block_get_length(self._block_count,
                                                   self._block_length,
                                                   delta)
            self._count += self._block_count
            self._block_count = 0
            self._update()

    def _update_interactive(self):
        _log((self._fmt + "\r") % self._count)

    def _update_noninteractive(self):
        _log((self._fmt + "\n") % self._count)

    def _cleanup(self):
        if self._clean:
            return
        self._clean = True
        if self._interactive:
            length = len(self._fmt % 0)
            _log((" " * length) + "\r")
        else:
            _log(self._fmt_msg + " done.\n")

    def __enter__(self):
        return self

    def __exit__(self, *args, **kwargs):
        self._cleanup()

    def __del__(self):
        """Delete the progress indicator from screen."""
        self._cleanup()


class Spinner:
    """A spinning (unbounded) progress indicator.

    Parameters
    ----------
    msg : string, optional
        Message to prefix to the progress indicator.

    """

    _SPINS = "-\\|/"

    def __init__(self, msg=""):
        self._interactive = _INTERACTIVE
        self._count = 0
        self._block_last_time = datetime.datetime.now()
        self._block_length = 1
        self._block_count = 0
        self._fmt_msg = " " + msg
        self._fmt = self._fmt_msg + " %s"
        self._clean = False
        if self._interactive:
            self._update = self._update_interactive
        else:
            self._update = self._update_noninteractive
        self._logclean = len(self._fmt % 0)
        _logclean(self._logclean)

    def __call__(self, increment=1):
        """Increment the progress indicator by the given number."""
        if level() < LVL_PROGRESS:
            return

        self._block_count += increment
        if self._block_count >= self._block_length:
            now = datetime.datetime.now()
            delta = now - self._block_last_time
            self._block_last_time = now
            self._block_length = _block_get_length(self._block_count,
                                                   self._block_length,
                                                   delta)
            self._count += 1
            self._count %= len(Spinner._SPINS)
            self._block_count = 0
            self._update()

    def _update_interactive(self):
        _log((self._fmt + "\r") % Spinner._SPINS[self._count])

    def _update_noninteractive(self):
        _log(self._fmt_msg + "\n")

    def _cleanup(self):
        if self._clean:
            return
        self._clean = True
        if self._interactive:
            length = len(self._fmt % " ")
            msg = (" " * length) + "\r"
            _log(msg)
        else:
            _log(self._fmt_msg + " done.\n")

    def __enter__(self):
        return self

    def __exit__(self, *args, **kwargs):
        self._cleanup()

    def __del__(self):
        """Delete the progress indicator from screen."""
        self._cleanup()


class Null:
    """A "null" progress indicator.

    """

    def __init__(self, *args, **kwargs):
        self._logclean = 0
        _logclean(self._logclean)

    def __call__(self, *args, **kwargs):
        pass

    def _cleanup(self):
        pass

    def __enter__(self):
        return self

    def __exit__(self, *args, **kwargs):
        pass

    def __del__(self):
        pass


def _progressable_get_func_wrapper(func, other, progr):
    def wrapper(self, *args, **kwargs):
        res = func(other, *args, **kwargs)
        progr()
        return res
    return wrapper


def _progressable_get_iter_wrapper(func, other, progr):
    def wrapper(self, *args, **kwargs):
        otheriter = func(other, *args, **kwargs)

        class _ProgressableIterator (other.__class__):
            def __init__(self):
                pass

            def __iter__(self):
                return self

            def next(self):
                return self.__next__()

            def __next__(self):
                res = next(otheriter)
                progr()
                return res

            def __getattr__(self, attr):
                try:
                    return getattr(otheriter, attr)
                except:
                    return getattr(other, attr)

            def __setattr__(self, attr, val):
                setattr(otheriter, attr, val)

        return _ProgressableIterator()
    return wrapper


class Progressable:
    """Indicates objects returned by `progressable`."""
    pass


def progressable(other, progr, funcs=[], iters=[]):
    """Get a wrapper that invokes a progress indicator on some routines.

    Parameters
    ----------
    other
        Object to wrap.
    progr
        A progress indicator instance.
    funcs : list of str, optional
        List of routines in `other` to wrap.
    iters : list of str, optional
        List of routines in `other` that return an interator to wrap.

    Notes
    -----
    Argument `other` is also passed as the first argument to `get`, such that
    it can return a proper indicator.

    """
    assert len(funcs) > 0 or len(iters) > 0
    assert len(funcs) + len(iters) == len(set(funcs) | set(iters))

    class _Progressable (other.__class__, Progressable):
        def __init__(self):
            pass

        def __enter__(self):
            progr.__enter__()
            return self

        def __exit__(self, *args, **kwargs):
            progr.__exit__(*args, **kwargs)

        def __getattr__(self, attr):
            return getattr(other, attr)

        def __setattr__(self, attr, val):
            return other.__class__.__setattr__(other, attr, val)

    res = _Progressable()

    for func in itertools.chain(funcs, iters):
        if not hasattr(other, func):
            raise ValueError("Routine %s not found" % func)
        func_orig = getattr(other.__class__, func)
        if func in funcs:
            func_ = _progressable_get_func_wrapper(func_orig, other, progr)
        else:
            func_ = _progressable_get_iter_wrapper(func_orig, other, progr)
        setattr(_Progressable, func, func_)

    return res


def progressable_simple(contents, length, *args, **kwargs):
    """A simplified version of `progressable`.

    Creates a progress indicator from the given arguments.

    """
    if length is None:
        progr = get(contents, *args, **kwargs)
    else:
        progr = get(length, *args, **kwargs)

    if isinstance(contents, types.GeneratorType):
        class Wrapper (collections.Iterable, collections.Sized):
            def __iter__(self):
                return iter(contents)

            def __len__(self):
                return len(contents)

        res = Wrapper()
    else:
        res = contents

    return progressable(res, progr, iters=["__iter__"])


class Stack:
    """Stack of currently active progress indicators.

    Provides only static attributes and methods, in order to provide a
    program-wide stateful stack of progress indicators.
    """

    _STACK = []
    CURRENT = None
    """The currently active progress indicator."""

    @staticmethod
    def __call__(*args, **kwargs):
        """Call on the current (latest) progress indicator.

        Parameters
        ----------
        args, kwargs
            Arguments for ``__call__`` to the current progress indicator.
        """
        Stack.CURRENT(*args, **kwargs)

    @staticmethod
    def push(cls, *args, **kwargs):
        """Add a new progress indicator to the stack and make it current.

        Parameters
        ----------
        cls : callable
            Class object or function to construct the new progress indicator.
        args, kwargs
            Arguments to `cls`.
        """
        if not callable(cls):
            raise TypeError

        if level() < LVL_PROGRESS:
            obj = Null(*args, **kwargs)
        elif not _INTERACTIVE and cls != Null:
            obj = Message(*args, **kwargs)
        else:
            obj = cls(*args, **kwargs)

        Stack._STACK.append(obj)
        Stack.CURRENT = Stack._STACK[-1]
        return Stack.CURRENT

    @staticmethod
    def pop():
        """Remove the last progress indicator from the stack."""
        assert len(Stack._STACK) > 1
        res = Stack.CURRENT
        Stack._STACK.pop()
        Stack.CURRENT = Stack._STACK[-1]
        _logclean(Stack.CURRENT._logclean)
        return res

# Add a default null progress reporter
Stack.push(Null)


class UnpicklerStart:
    """Picklable proxy to a progress indicator.

    In order to provide a progress indicator when unpickling large objects, you
    can prefix the pickle stream with a `UnpicklerStart` instance and postfix
    it with its `UnpicklerStop` sister instance::

        def dump (self, file_obj):
            start = UnpicklerStart(len(self))
            pickle.dump((start, self, start.get_stop()), file_obj)

    When unpickled, the first will call `Stack.push` and the last will call
    `Stack.pop`, so that your object will be able to update the
    `~Stack.CURRENT` progress indicator by calling `Stack`.

    When pickled, it will also push a progress indicator for your code to use
    while pickling your large object.

    Parameters
    ----------
    args, kwargs
        Arguments for ``__init__`` to the progress indicator class.

    Notes
    -----
    The following keys in `kwargs` are reserved for UnpicklerStart
    itself:

    ================ ======== ===================================================
    Key              Type     Description
    ================ ======== ===================================================
    ``no_pickle``    boolean  Do not create a progress indicator while pickling
    ``cls_pickle``   callable Progress indicator class to use while pickling
    ``msg_pickle``   string   Message during pickling (otherwise use default)
    ``no_unpickle``  boolean  Do not create a progress indicator while unpickling
    ``cls_unpickle`` callable Progress indicator class to use while unpickling
    ``msg_unpickle`` string   Message during unpickling (otherwise use default)togg
    ================ ======== ===================================================

    By default both progress indicators are generated using some default
    messages.

    """

    def __init__(self, *args, **kwargs):
        no_pickle = kwargs.pop("no_pickle", False)
        cls_pickle = kwargs.pop("cls_pickle", get)
        msg_pickle = kwargs.pop("msg_pickle", "saving to file...")

        no_unpickle = kwargs.pop("no_unpickle", False)
        cls_unpickle = kwargs.pop("cls_unpickle", get)
        msg_unpickle = kwargs.pop("msg_unpickle", "loading from file...")

        if no_pickle:
            self._pickle = None
        else:
            pickle_kwargs = kwargs.copy()
            pickle_kwargs.setdefault("msg", msg_pickle)
            self._pickle = (cls_pickle, args, pickle_kwargs)

        if no_unpickle:
            self._unpickle = None
        else:
            unpickle_kwargs = kwargs.copy()
            unpickle_kwargs.setdefault("msg", msg_unpickle)
            self._unpickle = (cls_unpickle, args, unpickle_kwargs)

    def get_stop(self):
        """Get the sister `UnpicklerStop` object."""
        return UnpicklerStop(self._pickle is not None,
                             self._unpickle is not None)

    def __getstate__(self):
        contents = self.__dict__.copy()
        if self._pickle is not None:
            Stack.push(self._pickle[0],
                       *self._pickle[1],
                       **self._pickle[2])
        del contents["_pickle"]
        return contents

    def __setstate__(self, contents):
        self.__dict__.update(contents)
        if self._unpickle is not None:
            Stack.push(self._unpickle[0],
                       *self._unpickle[1],
                       **self._unpickle[2])


class UnpicklerStop:
    """Remove the progress indicators created by `UnpicklerStart`."""

    def __init__(self, do_pickle, do_unpickle):
        """
        Parameters
        ----------
        do_pickle, do_unpickle : boolean
            Remove a progress indicator after pickling / unpickling.
        """
        self._pickle = do_pickle
        self._unpickle = do_unpickle

    def __getstate__(self):
        contents = self.__dict__.copy()
        del contents["_pickle"]
        if self._pickle:
            progress = Stack.pop()
            progress._cleanup()
        return contents

    def __setstate__(self, contents):
        self.__dict__.update(contents)
        if self._unpickle:
            progress = Stack.pop()
            progress._cleanup()


def _get_with_level(cls, ignore_level, total_name, *args, **kwargs):
    if ignore_level:
        return cls
    lvl = level()
    if lvl >= LVL_PROGRESS:
        return cls(*args, **kwargs)
    if total_name is not None:
        assert len(args) == 0
        assert total_name in kwargs
        del kwargs[total_name]
    if lvl < LVL_MARK:
        return Null(*args, **kwargs)
    else:
        assert lvl == LVL_MARK
        return Message(*args, **kwargs)


def _get_ignore_level(*args, **kwargs):
    return get(*args, ignore_level=True, **kwargs)


def get(*args, **kwargs):
    """Return either a `Counter` or a `Spinner`.

    The type depends on wether the first argument is a number or an object
    whose length can be known.

    """
    ignore_lvl = kwargs.pop("ignore_level", False)

    try:
        cargs = inspect.getcallargs(Counter.__init__,
                                    *([None]+list(args)), **kwargs)
        del cargs["self"]
        first = cargs["total"]
    except:
        first = None
    if isinstance(first, six.string_types):
        # message in unnamed argument
        del cargs["total"]
        return _get_with_level(Spinner, ignore_lvl, None, **cargs)
    elif isinstance(first, numbers.Number):
        return _get_with_level(Counter, ignore_lvl, "total", **cargs)
    elif isinstance(first, collections.Sized):
        cargs["total"] = len(first)
        return _get_with_level(Counter, ignore_lvl, "total", **cargs)
    elif isinstance(first, collections.Iterable):
        # iterator
        del cargs["total"]
        return _get_with_level(Spinner, ignore_lvl, None, **cargs)
    else:
        return _get_with_level(Spinner, ignore_lvl, None, *args, **kwargs)


def get_pickle(*args, **kwargs):
    """Return an `UnpicklerStart` with either a `Counter` or a `Spinner`.

    The type depends on wether the first argument is a number or an object
    whose length can be known.

    """
    return UnpicklerStart(*args, **kwargs)
