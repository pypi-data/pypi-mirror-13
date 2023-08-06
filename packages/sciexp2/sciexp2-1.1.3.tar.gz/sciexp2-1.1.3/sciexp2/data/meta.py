#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""Dimension metadata containers."""

from __future__ import print_function
from __future__ import absolute_import

__author__ = "Lluís Vilanova"
__copyright__ = "Copyright 2009-2015, Lluís Vilanova"
__license__ = "GPL version 3 or later"

__maintainer__ = "Lluís Vilanova"
__email__ = "vilanova@ac.upc.edu"


import collections
import numbers
import numpy
import re
import six
import sys
import weakref

from sciexp2.common import progress
import sciexp2.common.filter
from sciexp2.common import pp
from sciexp2.common import varref
import sciexp2.common.instance
from sciexp2.common.instance import Instance


class DimExpressionError (Exception):
    """Invalid dimension expression."""
    def __init__(self, *args, **kwargs):
        super(DimExpressionError, self).__init__(*args, **kwargs)


class DimExpression(object):
    """Descriptor for a dimension expression

    Parameters
    ----------
    expression : str
        Expression describing each element.
    varre : str, optional
        Regular expression for variables in `expression` (default in "@"; see
        `sciexp2.common.varref.build_varre`).
    validate : list of str, optional
        Ensure all variables in `expression` appear in `validate`.

    Raises
    ------
    DimExpressionError
        Invaid expression.

    Examples
    --------
    >>> e = DimExpression("@a@ (@b@)")
    >>> e.variables
    ['a', 'b']
    >>> e.expression
    '@a@ (@b@)'
    >>> e.extract('1 (2)')
    Instance({'a': 1, 'b': 2})
    >>> e.translate({'a': 1, 'b': 2})
    '1 (2)'

    """
    def __init__(self, expression, varre=None, validate=None):
        if isinstance(expression, DimExpression):
            self.expression = str(expression.expression)
            if varre is not None:
                msg = "Cannot provide a DimExpression and varre at the same time"
                raise DimExpressionError(msg)
            self.varre = expression.varre
        else:
            self.expression = expression
            if varre is None:
                varre = "@"
            self.varre = varre

        def escape(expression):
            expr = expression
            expr = re.escape(expr).replace("\\@", "@")
            tokenizer = varref.Tokenizer(self.varre)
            res = []
            for is_variable, token in tokenizer.tokenize(expr):
                if is_variable:
                    # unescape non-alphanumeric characters in variable names
                    res.append("@%s@" % token.replace("\\", ""))
                else:
                    res.append(token)
            expr = "".join(res)
            if expr[-1] != "$":
                expr += "$"
            return expr
        true_expression = escape(self.expression)

        self.variables = varref.expr_get_vars(self.varre, self.expression)

        expr_regex = varref.expr_to_regexp(self.varre, self.expression)
        regex_vars = varref.regexp_get_names(expr_regex)
        if len(set(regex_vars) - set(self.variables)) > 0:
            msg = "A dimension expression cannot contain regexp named groups: %s"
            raise DimExpressionError(msg % self.expression)

        if len(self.variables) == 0:
            raise DimExpressionError(
                "Dimension expression contains no variables: " +
                str(self.expression))

        if validate is not None:
            for var in self.variables:
                if var not in validate:
                    msg = "Unknown variable %r in dimension expression: %s"
                    raise DimExpressionError(msg % (var, self.expression))

        self._xlator = varref.PrepDictXlator(self.varre)
        self._xlator.prepare(self.expression)

        self._extractor = sciexp2.common.instance.InstanceExtractor(
            true_expression, self.varre)

    def __eq__(self, other):
        return isinstance(other, DimExpression) and \
            self.expression == other.expression and \
            self.varre == other.varre

    def extract(self, source):
        """Extract an instance from the given string."""
        instance = self._extractor.extract(source)
        if instance is None:
            raise ValueError("Cannot extract expression %r from %r" %
                             (self.expression, source))
        # try to turn values into numbers
        for k, v in instance:
            instance[k] = sciexp2.common.utils.str2num(v)
        return instance

    def translate(self, instance):
        """Translate the given instance into a string."""
        return self._xlator.xlate(None, instance)


class Dim (pp.Pretty):
    """Map variable values to and from array indexes.

    Parameters
    ----------
    expression : str, optional
        Expression describing each element.
    contents : optional, optional
        Dimension contents (default is no contents).

    Attributes
    ----------
    expression
    variables
    indexes
    ticks
    instances
    values
    unique_values
    array
    index

    Notes
    -----
    If `expression` is not given, it will default to ``@var@``.

    Each element of `contents` must have one of the following formats:

    * `None`: the entry is left empty.

    * `str`: an instance will be extracted using the `expression` attribute.

    * `dict`: a dict-like object that must have, at least, entries for the
      variables in the `expression` attribute.

    When not `None`, any pair of elements must have a different expansion for
    `expression`.

    A dimension can be indexed with one of the following formats:

    * `int`: element at given position.

    * `str`: element with given tick.

    * `dict`: element with given variable values (can also be an `Instance`).

    If the stepping of a slice is a `str` or `dict`, it will be used as a
    filter to select the matching elements. The `dict` version is a performance
    optimization for filters that look for the specified variable values.

    Accessing a single element of a `Dim` returns None, but slicing it results
    in either a view to the original, or a brand new object. The type of result
    depends on the indexing used to slice it, following numpy's slicing rules.
    Also, using a filter while slicing always creates a new object.

    Assigning to a `Dim` object follows the same rules, and accepts the same
    values valid during construction.

    Examples
    --------

    >>> d = Dim('@a@-@b@', ['a1-b1', 'a1-b2', None, 'a2-b2', None])
    >>> d[1:-1]
    Dim('@a@-@b@', ['a1-b2', None, 'a2-b2'])
    >>> d['a1-b2':-1]
    Dim('@a@-@b@', ['a1-b2', None, 'a2-b2'])

    The stepping in a slice is used as a filter:

    >>> d[::"a == 'a1'"]
    Dim('@a@-@b@', ['a1-b1', 'a1-b2'])

    Using a `dict` (or `Instance`) is a performance-optimized version of
    indexing and filtering:

    >>> d[{'a': 'a1', 'b':'b2'}:-1]
    Dim('@a@-@b@', ['a1-b2', None, 'a2-b2'])
    >>> d[::{'a': 'a1'}]
    Dim('@a@-@b@', ['a1-b1', 'a1-b2'])

    Indexing on a single element returns `None`:

    >>> d[0] is d['a1-b1'] is d[1] is None
    True

    The same formats (`str` or `dict`) are supported when testing for
    existence:

    >>> 'a1-b1' in d
    True
    >>> Instance({'a': 'a1', 'b': 'b1'}) in d
    True
    >>> 'a1-b3' in d
    False
    >>> Instance({'a': 'a1', 'b': 'b3'}) in d
    False

    See also
    --------
    base

    """

    ##########################################################################
    # Construction
    ##########################################################################

    _DEFAULT_VAR = "var"
    _DEFAULT_EXPR = "@%s@" % _DEFAULT_VAR

    def __init__(self, expression=None, contents=None):
        # weakref to containing DataDims
        self.__dims = None
        # ultimate base Dim for which this is a view for (possibly indirectly)
        self._base = None
        # views of self (id(Dim), weakref(Dim)) (both direct and indirect)
        self._views = {}

        if expression is None:
            self._have_expression = False
            expression = self._DEFAULT_EXPR
        else:
            self._have_expression = True
        self._expression = DimExpression(expression)

        if contents is None:
            contents = []

        # fill-in contents
        self._group = sciexp2.common.instance.InstanceGroup(
            view_able=True,
            cache=True,
            cache_proactive=[],
            cache_others=self._expression.variables)
        self._indexes = {}

        if not isinstance(contents, progress.Progressable):
            contents = progress.progressable_simple(
                contents, None,
                msg="building dimension...")
        expressions = dict()
        with contents:
            for i in contents:
                instance, i_expression = self._as_instance(i)

                # check for repeated instances
                # NOTE: cannot use '_exists_instance' since we want to avoid
                #       using caching
                if len(instance) > 0:
                    if i_expression is None:
                        i_expression = self._expression.translate(instance)
                    if i_expression in expressions:
                        raise ValueError(
                            "repeated tick %r while adding %r" %
                            (i_expression, instance))
                    expressions[i_expression] = instance

                self._group.add(instance)
                self._indexes[instance] = len(self._indexes)

    def _exists_instance(self, instance, ignore=set()):
        for i in self._group.select(instance):
            if i not in ignore:
                return True
        return False

    def _as_instance(self, content):
        if isinstance(content, six.string_types):
            i_expression = content
            content = self._expression.extract(content)
        else:
            i_expression = None

        instance = Instance()
        if content is not None:
            try:
                instance = sciexp2.common.instance.Instance(
                    (key, val) for key, val in six.iteritems(content)
                    if key in self._expression.variables)
            except AttributeError:
                raise TypeError("dont know how to construct "
                                "a dimension element from: %r" % content)

        # check for missing variables
        missing = set(self._expression.variables) - set(instance.keys())
        if len(missing) > 0 and len(instance) > 0:
            raise KeyError("missing variable %r for: %r" %
                           (missing.pop(), content))

        return instance, i_expression

    @property
    def _dims(self):
        if self.__dims is None:
            return None
        else:
            return self.__dims()

    @_dims.setter
    def _dims(self, value):
        if value is None:
            self.__dims = None
        else:
            self.__dims = weakref.ref(value)

    def copy(self):
        """Return a deep copy of this dimension."""
        return Dim(self.expression if self._have_expression else None,
                   self._group)

    @property
    def expression(self):
        """An expandable expression where dimension elements are built from.

        Raises
        ------
        DimExpressionError
            Non-existing dimension expression.

        See also
        --------
        DimExpression

        Notes
        -----
        If a new value is assigned, ticks will be kept consistent.

        """
        if self._have_expression:
            return str(self._expression.expression)
        else:
            raise DimExpressionError("dimension has no expression")

    @expression.setter
    def expression(self, expression):
        have_expression = expression is not None
        if not have_expression:
            expression = self._DEFAULT_EXPR
        expression = DimExpression(expression)

        def change_expression(have_expression, expression):
            base = self.base or self
            base._have_expression = have_expression
            base._expression = expression
            for view in base._views.values():
                view()._have_expression = have_expression
                view()._expression = expression

        if self._have_expression:
            if have_expression:
                if set(expression.variables) != set(self.variables):
                    raise DimExpressionError(
                        "variable mismatch "
                        "(you can set 'expression' to None to reset)")
                change_expression(True, expression)
            else:
                base = self.base or self
                ticks = list(base.ticks)
                change_expression(False, expression)
                for tick, instance in zip(ticks, base._group):
                    instance.clear()
                    if tick is not None:
                        instance[self._DEFAULT_VAR] = tick
                self._group.cache_reset(hard=True)
                self._group.cache_set(True, [], expression.variables)
        else:
            base = self.base or self
            base_expression = base._expression
            change_expression(have_expression, expression)

            # calculate new instances; revert on error
            instances = []
            for instance in self._group:
                if len(instance) > 0:
                    try:
                        instance = self._as_instance(str(instance[self._DEFAULT_VAR]))[0]
                    except:
                        change_expression(False, base_expression)
                        raise
                instances.append(instance)

            # apply new instances
            for cur_instance, new_instance in zip(base._group, instances):
                cur_instance.clear()
                cur_instance.update(new_instance)
            self._group.cache_reset(hard=True)
            self._group.cache_set(True, [], expression.variables)

    def extract(self, source):
        """Return an instance from `source` using the dimension's `expression`.

        Examples
        --------
        >>> d = Dim("@entries@-@entry_size@",
        ...         ["1-8", "2-8", "2-16"])
        >>> d.extract("10-20")
        Instance({'entries': 10, 'entry_size': 20})

        Raises
        ------
        DimExpressionError
            Non-existing dimension expression.

        """
        if self._have_expression:
            return self._expression.extract(source)
        else:
            raise DimExpressionError("dimension has no expression")

    def translate(self, instance):
        """Translate `instance` into a string using the dimension's `expression`.

        Examples
        --------
        >>> d = Dim("@entries@-@entry_size@",
        ...         ["1-8", "2-8", "2-16"])
        >>> d.translate(Instance({'entries': 10, 'entry_size': 20}))
        '10-20'

        Raises
        ------
        DimExpressionError
            Non-existing dimension expression.

        """
        if self._have_expression:
            return self._expression.translate(instance)
        else:
            raise DimExpressionError("dimension has no expression")

    @property
    def variables(self):
        """List of variable names in `expression`.

        Raises
        ------
        DimExpressionError
            Non-existing dimension expression.

        """
        if self._have_expression:
            return list(self._expression.variables)
        else:
            raise DimExpressionError("dimension has no expression")

    ##########################################################################
    # Translation API
    ##########################################################################

    def _get_indexes(self, index):
        """Return the numeric index translation of names in `index`."""

        ##################################################
        # numeric indexes
        if isinstance(index, numbers.Real):
            if index >= len(self._group):
                raise IndexError("index (%d) out of range" % index)
            return index

        # NOTE: PFilter confuses `numpy.shape`
        if isinstance(index, sciexp2.common.filter.PFilter):
            index = index.realize()

        ##################################################
        # sequence of indexes (need further parsing)
        if isinstance(index, numpy.ndarray) or numpy.shape(index) != tuple():
            if not isinstance(index, numpy.ndarray):
                tolist = True
                index = numpy.array(index, dtype=object)
            else:
                tolist = False

            if numpy.issubdtype(index.dtype, numpy.bool) and \
               numpy.issubdtype(index.dtype, numpy.bool_):
                if index.ndim == 0:
                    raise ValueError(
                        "boolean index array should have 1 dimension")
                return [self._get_indexes(pos)
                        for pos, idx in enumerate(index)
                        if idx]

            elif index.ndim == 0:
                return self._get_indexes(index)

            else:
                res = numpy.ndarray(index.shape, dtype=int)
                for pos, idx in enumerate(index.flat):
                    try:
                        elem = self._get_indexes(idx)
                    except Exception as e:
                        _, _, exc_traceback = sys.exc_info()
                        new_e = IndexError(
                            "invalid index element %r in position %d"
                            "\n  [was] "
                            "%s: %s" % (idx, pos,
                                        e.__class__.__name__, e))
                        six.reraise(new_e.__class__, new_e, exc_traceback)
                    res.flat[pos] = elem
                if tolist:
                    # NOTE: work around numpy bug #6564
                    #       https://github.com/numpy/numpy/issues/6564
                    res = res.tolist()
                return res

        ##################################################
        # slice
        if isinstance(index, slice):
            def slice_index(index):
                if index is None:
                    return index
                if isinstance(index, numbers.Real):
                    # integer slicing accepts out-of-bounds indexes
                    return index
                return self._get_indexes(index)
            start = slice_index(index.start)
            stop = slice_index(index.stop)
            step = index.step

            if not (start is None or isinstance(start, int)) or \
               not (stop is None or isinstance(stop, int)):
                raise IndexError("invalid slice (%s)" % repr(index))

            if step is None or isinstance(step, int):
                return slice(start, stop, step)

            # string stepping -> filter
            try:
                filter_ = sciexp2.common.filter.Filter(step)
                filter_.validate(self._group)
            except Exception as e:
                _, _, exc_traceback = sys.exc_info()
                new_e = IndexError(
                    "invalid slice filter\n"
                    "%s: %s" % (e.__class__.__name__, e))
                six.reraise(new_e.__class__, new_e, exc_traceback)

            if start is None:
                start = 0
            assert isinstance(start, numbers.Real)
            if stop is None:
                stop = len(self._group)
            elif stop < 0:
                stop = len(self._group) + stop
            assert isinstance(stop, numbers.Real)
            return [self._indexes[idx] for idx in self._group.select(
                filter_, allow_unknown=True)
                    if start <= self._indexes[idx] and self._indexes[idx] < stop]

        ##################################################
        # label
        if isinstance(index, six.string_types):
            instance = self._get_from_expression(index)
            if instance is not None:
                return self._indexes[instance]

        ##################################################
        # instance in this dimension
        if isinstance(index, dict):
            if isinstance(index, Instance):
                # shortcut when indexing with existing instance
                indexes = self._indexes.get(index, None)
                if indexes is not None:
                    return indexes
            indexes = self._get_indexes(slice(None, None, index))
            if len(indexes) == 1:
                return indexes[0]

        ##################################################
        # filter (or else error)
        try:
            filter_ = sciexp2.common.filter.Filter(index)
        except TypeError:
            raise TypeError("invalid index type: " + repr(index))
        except sciexp2.common.filter.ParseError as e:
            raise IndexError("invalid filter: %r\n  "
                             "[was] %s: %s" % (index, e.__class__.__name__,
                                               str(e)))
        try:
            selected = list(self._group.select(filter_))
        except sciexp2.common.filter.FilterError as e:
            if e.args[0] == index:
                raise IndexError("unknown tick: %r" % index)
            else:
                raise IndexError("invalid filter: %r\n  "
                                 "[was] %s: %s" % (index, e.__class__.__name__,
                                                   str(e)))
        if len(selected) == 0:
            raise IndexError("filter has no matches: %r" % index)
        if len(selected) == 1:
            return self._indexes[selected[0]]
        else:
            raise IndexError("filter has multiple matches: %r" % index)

    def _get_from_expression(self, expression):
        try:
            instance = self._expression.extract(expression)
        except ValueError:
            return None
        # try using an instance as a filter
        try:
            results = list(self._group.select(instance))
        except sciexp2.common.filter.ParseError:
            pass
        else:
            if len(results) > 0:
                assert len(results) == 1
                return results[0]

        # fall back to reconstructing expression
        for instance in self._group:
            try:
                i_expression = self._expression.translate(instance)
            except varref.XlateError:
                continue
            if expression == i_expression:
                return instance
        return None

    ##########################################################################
    # Slicing
    ##########################################################################

    def __getslice__(self, start, stop):
        if start is 0:
            start = None
        if stop == sys.maxint:
            return self[start::]
        else:
            return self[start:stop:]

    def _view(self, index):
        indexes = self._get_indexes(index)
        if isinstance(indexes, slice):
            dim = Dim(self.expression if self._have_expression else None,
                      [])
            dim._base = self._base or self
            self._views[id(dim)] = weakref.ref(dim)

            if indexes.start is None and indexes.stop is None and \
               indexes.step is None:
                dim._group = self._group
                dim._indexes = self._indexes
            else:
                dim._group = self._group.view(indexes)
                dim._indexes = dict(
                    six.moves.zip(dim._group,
                                  six.moves.range(len(dim._group))))
        elif numpy.shape(indexes) == tuple():
            dim = None
        else:
            indexes_ = indexes
            if not isinstance(indexes_, numpy.ndarray):
                indexes_ = numpy.array(indexes, dtype=int)
            if indexes_.ndim > 1:
                raise TypeError(
                    "dimension indexes cannot have more than one dimension")
            with progress.progressable_simple(
                    (self._group.get_index(idx)
                     for idx in indexes_.flat),
                    indexes_, msg="slicing dimension...") as contents:
                dim = Dim(self.expression if self._have_expression else None,
                          contents)
        return dim, indexes

    def _assign(self, new_dim):
        base = self.base or self

        # reassign contents
        assert len(self._group) == len(new_dim._group)
        for i_old, i_new in zip(base._group, new_dim._group):
            for key in list(i_old.keys()):
                del i_old[key]
            i_old.update(i_new)

        # update expressions
        base._have_expression = new_dim._have_expression
        base._expression = new_dim._expression
        base._group.cache_reset()
        base._group.cache_set(True, proactive=[],
                              others=base._expression.variables)
        for dim in self._views.values():
            dim()._have_expression = new_dim._have_expression
            dim()._expression = new_dim._expression
            dim()._group.cache_reset()
            dim()._group.cache_set(True, proactive=[],
                                   others=self._expression.variables)

    def __getitem__(self, index):
        return self._view(index)[0]

    def __setslice__(self, start, stop, value):
        if start is 0:
            start = None
        if stop == sys.maxint:
            self[start::] = value
        else:
            self[start:stop:] = value

    def __setitem__(self, index, value):
        indexes = self._get_indexes(index)

        # homogeinize 'value' and record 'targets'
        if isinstance(indexes, slice):
            start = indexes.start
            if start is None:
                start = 0
            elif start < 0:
                start += len(self._group)

            stop = indexes.stop
            if stop is None:
                stop = len(self._group)
            elif stop < 0:
                stop += len(self._group)

            step = indexes.step
            if step is None:
                step = 1

            targets = []
            idx = start
            while idx < stop:
                targets.append(self._group.get_index(idx))
                idx += step
        elif numpy.shape(indexes) == tuple():
            value = [value]
            targets = [self._group.get_index(indexes)]
        else:
            targets = [self._group.get_index(idx)
                       for idx in indexes]
        try:
            len_value = len(value)
        except TypeError:
            len_value = 0
        if len(targets) != len_value:
            raise ValueError(
                "cannot assign sequence of size %d to slice of size %d" %
                (len_value, len(targets)))

        # actual updates
        base = self.base or self
        base._group.cache_prefetch()
        ignore = set(targets)
        expressions = set()
        for target, i in zip(targets, value):
            new_instance, new_expression = self._as_instance(i)
            if len(new_instance) > 0:
                if new_expression is None:
                    new_expression = self._expression.translate(new_instance)
                if base._exists_instance(new_instance, ignore) or \
                   new_expression in expressions:
                    raise ValueError("repeated tick %r while adding %r" %
                                     (new_expression, new_instance))
                target.update(new_instance)
                expressions.add(new_expression)
            else:
                target.clear()

        # reset caches
        base._group.cache_reset()
        for view in base._views.values():
            base._group.cache_reset()

    def __del__(self):
        # NOTE: __del__ can be called more than once
        #       (if object is resurrected during __del__)
        if self.base is not None and id(self) in self._base._views:
            del self._base._views[id(self)]

    @property
    def base(self):
        """The `Dim` object this one is a view of."""
        return self._base

    @property
    def indexes(self):
        """Return a `DimViewIndexes` for this dimension."""
        return DimViewIndexes(self)

    @property
    def ticks(self):
        """Return a `DimViewTicks` for this dimension."""
        return DimViewTicks(self)

    @property
    def instances(self):
        """Return a `DimViewInstances` for this dimension."""
        return DimViewInstances(self)

    @property
    def values(self):
        """Return a `DimViewValues` for this dimension."""
        return DimViewValues(self, unique=False)

    @property
    def unique_values(self):
        """Return a `DimViewValues` for this dimension (without repeated values)."""
        return DimViewValues(self, unique=True)

    @property
    def array(self):
        """The `Data` array this dimension is associated to."""
        if self._dims is None:
            return None
        else:
            return self._dims._array

    @property
    def index(self):
        """The index of this dimension in the associated `DataDims`."""
        if self._dims is None:
            return None
        return list(self._dims).index(self)

    ##########################################################################
    # (un)pickling
    ##########################################################################

    def __getstate__(self):
        if self._have_expression:
            expression = self.expression
            varre = self._expression.varre
        else:
            expression = self._DEFAULT_EXPR
            varre = None
        odict = self.__dict__.copy()
        odict["_expression"] = expression
        odict["_varre"] = varre
        del odict["_%s__dims" % self.__class__.__name__]
        del odict["_base"]
        del odict["_views"]
        return odict

    def __setstate__(self, odict):
        self._expression = DimExpression(odict["_expression"], odict["_varre"])
        del odict["_expression"]
        del odict["_varre"]
        self.__dict__.update(odict)
        self._dims = None
        self._base = None
        self._views = {}

    ##########################################################################
    # Miscellaneous
    ##########################################################################

    def __contains__(self, index):
        """Return whether an elment named 'index' exists."""
        if isinstance(index, six.string_types) or isinstance(index, dict):
            try:
                self._get_indexes(index)
                return True
            except IndexError:
                return False
        else:
            raise TypeError("not a string or dict")

    def __len__(self):
        """The length of this dimension."""
        return len(self._group)

    def __iter__(self):
        for i in self._group:
            try:
                yield self._expression.translate(i)
            except varref.XlateError:
                yield None

    def _repr_pretty_(self, p, cycle):
        with self.pformat(p, cycle, name="Dim"):
            if self._have_expression:
                p.text(repr(self.expression))
            else:
                p.text(repr(None))
            p.text(",")
            p.breakable()
            p.pretty(list(self))

    def __repr__(self):
        return pp.Pretty.__repr__(self)

    def sorted(self, *args, **kwargs):
        """Same as `sort`, but returns a sorted copy."""
        res = self.copy()
        res.sort(*args, **kwargs)
        return res

    def sort(self, *spec):
        """Sort dimension elements in-place.

        Parameters
        ----------
        spec : list
            Sequence of sorting specifications.

        Raises
        ------
        DimExpressionError
            Dimension has no expression.

        Notes
        -----
        Each element in `spec` can have one of the following formats:

        * ``(str, callable)``
            Sort values of variable ``str`` using the `cmp`-like function
            ``callable``, accepting pairs of variable values.

        * ``(str, list)``
            Sort values of variable ``str`` according to the provided list.

        * ``(str, True)``
            Sort values of variable ``str`` lexicographically.

        * ``callable``
            Sort all dimension instances using the `cmp`-like function
            ``callable``, accepting pairs of dimension instances.

        * ``list``
            Sort all dimension instances accoring to the given tick list.

        * ``str``
            Sort values of variable ``str`` lexicographically.

        * ``True``
            Sort all dimension instances lexicographically.

        For every pair of instances, sorting will stop at the first `spec`
        element with a non-zero result.

        Sorting on a dimension view will only affect the elements contained in
        it (i.e., will affect views of that view, but not elements in the base
        dimension that the view is not referencing).

        Sorting on a dimension that has an associated array will also sort the
        array contents accordingly.

        """
        # default sorting functions
        def sort_instance_from_func(sort_func):
            def func(i1, i2):
                if len(i1) == 0:
                    i1 = None
                if len(i2) == 0:
                    i2 = None
                return sort_func(i1, i2)
            return func

        def sort_var_from_func(var, sort_func):
            def func(i1, i2):
                v1 = i1[var] if i1 is not None else None
                v2 = i2[var] if i2 is not None else None
                return sort_func(v1, v2)
            return sort_instance_from_func(func)

        def sort_var_from_list(contents, var):
            def func(v1, v2):
                idx1 = contents.index(v1)
                idx2 = contents.index(v2)
                return cmp(idx1, idx2)
            return sort_var_from_func(var, func)

        def sort_var_lex(var):
            return sort_var_from_func(var, cmp)

        def sort_tick_from_func(sort_func):
            def func(i1, i2):
                if i1 is None:
                    v1 = None
                else:
                    v1 = self.translate(i1)
                if 21 is None:
                    v2 = None
                else:
                    v2 = self.translate(i2)
                return sort_func(v1, v2)
            return sort_instance_from_func(func)

        def sort_tick_from_list(contents):
            def func(v1, v2):
                try:
                    idx1 = contents.index(v1)
                    idx2 = contents.index(v2)
                except:
                    raise
                return cmp(idx1, idx2)
            return sort_tick_from_func(func)

        # normalize 'spec'
        def get_variables(idx, elem):
            try:
                return self.variables
            except DimExpressionError as e:
                _, _, exc_traceback = sys.exc_info()
                new_e = DimExpressionError(
                    "spec %d references variables on empty expression: %r"
                    "\n  [was] "
                    "%s: %s" % (idx, elem,
                                e.__class__.__name__, e))
                six.reraise(new_e.__class__, new_e, exc_traceback)

        def normalize(spec):
            res = []
            for idx, s in enumerate(spec):
                elem = s

                if isinstance(s, six.string_types):
                    s = (s, True)
                elif s is True:
                    for var in get_variables(idx, elem):
                        s = sort_var_lex(var)
                        res.append((var, s))
                    continue
                elif callable(s):
                    s = (None, s)

                if not isinstance(s, tuple):
                    if not isinstance(s, collections.Iterable):
                        raise TypeError("spec %d has invalid format: %r" %
                                        (idx, elem))
                    s = (None, s)
                s = list(s)

                if len(s) != 2:
                    raise TypeError("spec %d has invalid format: %r" %
                                    (idx, elem))

                if s[0] is not None and s[0] not in get_variables(idx, elem):
                    raise ValueError(
                        "spec %d references non-existing variable: %r" %
                        (idx, s[0]))

                if s[1] is True:
                    s[1] = sort_var_lex(s[0])
                elif not callable(s[1]):
                    if not isinstance(s[1], collections.Iterable):
                        raise ValueError("spec %d has invalid format: %r" %
                                         (idx, elem))
                    if not isinstance(s[1], list):
                        s[1] = list(s[1])

                    if s[0] is None:
                        s[1] = sort_tick_from_list(list(s[1]))
                    else:
                        s[1] = sort_var_from_list(list(s[1]), s[0])
                else:
                    if s[0] is None:
                        s[1] = sort_instance_from_func(s[1])
                    else:
                        s[1] = sort_var_from_func(s[0], s[1])

                # check for repeated elements
                if s[0] in dict(res):
                    if s[0] is None:
                        raise ValueError(
                            "spec %d uses repeated non-variable format: %s" %
                            (idx, elem))
                    else:
                        raise ValueError(
                            "spec %d uses repeated variable name: %s" %
                            (idx, elem))

                res.append(s)

            return res
        spec = normalize(spec)

        # merged sorting function
        def sort_func(i1, i2):
            for elem in spec:
                res = elem[1](i1, i2)
                if res != 0:
                    return res
            return 0

        self._group.sort([], cmp=sort_func)

        if self.array is not None:
            old_indexes = list(self._indexes[i] for i in self._group)

        # update indexes
        def update_indexes(dim):
            for idx, instance in enumerate(dim._group):
                if instance in self._indexes:
                    dim._indexes[instance] = idx
        base = self.base if self.base is not None else self
        update_indexes(base)
        for view in base._views.values():
            update_indexes(view())

        if self.array is not None:
            self.array._sort(self, old_indexes)


class DimViewIndexes:
    """A view to the numeric indexes of a `Dim`.

    Examples
    --------
    >>> d = Dim("@entries@-@entry_size@",
    ...         ["1-8", None, "2-8", "2-16"])
    >>> list(d.indexes)
    [0, 1, 2, 3]
    >>> d.indexes[2]
    2
    >>> d.indexes["2-8"]
    2
    >>> d.indexes[1:]
    [1, 2, 3]
    >>> d.indexes[1:-1]
    [1, 2]
    >>> d.indexes[::"entries==2"]
    [2, 3]
    >>> d.indexes[[["1-8", 1], ["2-8", "1-8"]]]
    [[0, 1], [2, 0]]

    """
    def __init__(self, dimension, expand_slice=True):
        self.dimension = dimension
        self._expand_slice = expand_slice

    def __len__(self):
        return len(self.dimension)

    def __iter__(self):
        for i in self.dimension._group:
            yield self.dimension._indexes[i]

    def __getslice__(self, start, stop):
        if start is 0:
            start = None
        if stop == sys.maxint:
            return self[start::]
        else:
            return self[start:stop:]

    def __getitem__(self, index):
        indexes = self.dimension._get_indexes(index)

        if isinstance(indexes, slice) and self._expand_slice:
            return range(*indexes.indices(len(self.dimension)))
        else:
            if isinstance(indexes, numpy.ndarray):
                return indexes.tolist()
            else:
                return indexes


class DimViewTicks:
    """A view to the ticks of a `Dim`.

    Examples
    --------
    >>> d = Dim("@entries@-@entry_size@",
    ...         ["1-8", None, "2-8", "2-16"])
    >>> list(d.ticks)
    ['1-8', None, '2-8', '2-16']
    >>> d.ticks[1]
    >>> d.ticks[2]
    '2-8'
    >>> d.ticks["2-8"]
    '2-8'
    >>> d.ticks[1:]
    [None, '2-8', '2-16']
    >>> d.ticks[1:-1]
    [None, '2-8']
    >>> d.ticks[::"entries==2"]
    ['2-8', '2-16']
    >>> d.ticks[[["1-8", 1], ["2-8", "1-8"]]]
    [['1-8', None], ['2-8', '1-8']]

    """
    def __init__(self, dimension):
        self.dimension = dimension

    def __len__(self):
        return len(self.dimension)

    def _xlate(self, value):
        try:
            return self.dimension._expression.translate(value)
        except varref.XlateError:
            return None

    def __iter__(self):
        for i in self.dimension._group:
            yield self._xlate(i)

    def __getslice__(self, start, stop):
        if start is 0:
            start = None
        if stop == sys.maxint:
            return self[start::]
        else:
            return self[start:stop:]

    def __getitem__(self, index):
        indexes = self.dimension.indexes[index]

        def xlate(instance):
            if len(instance) == 0:
                return None
            else:
                return self._xlate(instance)

        assert not isinstance(indexes, slice)
        if numpy.shape(indexes) != tuple():
            if not isinstance(indexes, numpy.ndarray):
                indexes = numpy.array(indexes, dtype=object)
            for idx, elem in enumerate(indexes.flat):
                instance = self.dimension._group.get_index(elem)
                indexes.flat[idx] = xlate(instance)
            return indexes.tolist()

        else:
            assert isinstance(indexes, numbers.Integral)
            instance = self.dimension._group.get_index(indexes)
            return xlate(instance)


class DimViewInstances:
    """A view to the instances of a `Dim`.

    .. warning::

       You should not modify the instances returned by this object.

    Examples
    --------
    >>> d = Dim("@entries@-@entry_size@",
    ...         ["1-8", None, "2-8", "2-16"])
    >>> list(d.instances)
    [Instance({'entries': 1, 'entry_size': 8}), None, Instance({'entries': 2, 'entry_size': 8}), Instance({'entries': 2, 'entry_size': 16})]
    >>> d.instances[1]
    >>> d.instances[2]
    Instance({'entries': 2, 'entry_size': 8})
    >>> d.instances["2-8"]
    Instance({'entries': 2, 'entry_size': 8})
    >>> d.instances[1:]
    [None, Instance({'entries': 2, 'entry_size': 8}), Instance({'entries': 2, 'entry_size': 16})]
    >>> d.instances[1:-1]
    [None, Instance({'entries': 2, 'entry_size': 8})]
    >>> d.instances[::"entries==2"]
    [Instance({'entries': 2, 'entry_size': 8}), Instance({'entries': 2, 'entry_size': 16})]
    >>> d.indexes[d.instances[::"entries==2"]]
    [2, 3]
    >>> d.ticks[d.instances[::"entries==2"]]
    ['2-8', '2-16']
    >>> d.instances[[["1-8", 1], ["2-8", "1-8"]]]
    [[Instance({'entries': 1, 'entry_size': 8}), None], [Instance({'entries': 2, 'entry_size': 8}), Instance({'entries': 1, 'entry_size': 8})]]

    """
    def __init__(self, dimension):
        self.dimension = dimension

    def __len__(self):
        return len(self.dimension)

    def __iter__(self):
        for i in self.dimension._group:
            if len(i) == 0:
                yield None
            else:
                yield i

    def __getslice__(self, start, stop):
        if start is 0:
            start = None
        if stop == sys.maxint:
            return self[start::]
        else:
            return self[start:stop:]

    def __getitem__(self, index):
        indexes = self.dimension.indexes[index]

        assert not isinstance(indexes, slice)
        if numpy.shape(indexes) != tuple():
            if not isinstance(indexes, numpy.ndarray):
                indexes = numpy.array(indexes, dtype=object)
            for idx, elem in enumerate(indexes.flat):
                instance = self.dimension._group.get_index(elem)
                if len(instance) == 0:
                    instance = None
                indexes.flat[idx] = instance
            return indexes.tolist()

        else:
            assert isinstance(indexes, numbers.Integral)
            instance = self.dimension._group.get_index(indexes)
            if len(instance) == 0:
                instance = None
            return instance


class DimViewValues(object):
    """A view to the variable values of a `Dim`.

    This can be used as a shortcut to processing the elements of
    `DimViewInstances`. If more than one variable name is specified, values are
    returned as tuples.

    Examples
    --------
    The list of values of a given variable retains the order of the dimension:

    >>> d = Dim("@a@-@b@-@c@",
    ...         ["%d-%d-%d" % (a, b, c)
    ...          for a in range(3)
    ...          for b in range(3, 6)
    ...          for c in range(6, 9)])
    >>> d                               # doctest: +ELLIPSIS
    Dim('@a@-@b@-@c@',
        ['0-3-6',
         '0-3-7',
         '0-3-8',
         ...,
         '2-5-6',
         '2-5-7',
         '2-5-8'])
    >>> d.values["a"]                   # doctest: +ELLIPSIS
    [0, 0, 0, ..., 2, 2, 2]
    >>> d.unique_values["a"]
    OrderedSet([0, 1, 2])

    Multiple variables can also be specified:

    >>> d.values["a", "c"]              # doctest: +ELLIPSIS +NORMALIZE_WHITESPACE
    [(0, 6), (0, 7), (0, 8),
     (0, 6), (0, 7), (0, 8),
     ...
     (2, 6), (2, 7), (2, 8),
     (2, 6), (2, 7), (2, 8)]
    >>> d.unique_values["a", "c"]
    OrderedSet([(0, 6),
                (0, 7),
                (0, 8),
                (1, 6),
                (1, 7),
                (1, 8),
                (2, 6),
                (2, 7),
                (2, 8)])

    Slices and regular indexes can also be used:

    >>> d.unique_values["b":-1]
    OrderedSet([(3,), (4,), (5,)])

    """
    def __init__(self, dimension, unique):
        self.dimension = dimension
        self.unique = unique

    def __getslice__(self, start, stop):
        if start is 0:
            start = None
        if stop == sys.maxint:
            return self[start::]
        else:
            return self[start:stop:]

    def __getitem__(self, index):
        variables = list(self.dimension.variables)

        def get_elem(elem, as_var):
            if isinstance(elem, six.string_types):
                try:
                    idx = variables.index(elem)
                except ValueError:
                    raise ValueError("unknown variable name %r" % elem)
                if not as_var:
                    elem = idx
            elif as_var:
                try:
                    elem = variables[elem]
                except ValueError:
                    raise ValueError("unknown variable name %r" % elem)
            return elem

        if isinstance(index, slice):
            slice_start = get_elem(index.start, False)
            slice_stop = get_elem(index.stop, False)
            index = slice(slice_start, slice_stop, index.step)
            index = tuple(range(*index.indices(len(variables))))

        if not isinstance(index, tuple):
            index = get_elem(index, True)
            if self.unique:
                res = sciexp2.common.utils.OrderedSet()
                for i in self.dimension._group:
                    res.add(i[index])
                return res
            else:
                res = []
                for i in self.dimension._group:
                    res.append(i[index])
                return res
        else:
            index = [get_elem(idx, True) for idx in index]
            if self.unique:
                res = sciexp2.common.utils.OrderedSet()
                for i in self.dimension._group:
                    res.add(tuple([i[idx] for idx in index]))
                return res
            else:
                res = []
                for i in self.dimension._group:
                    res.append(tuple([i[idx] for idx in index]))
                return res


__all__ = [
    "DimExpressionError", "DimExpression",
    "Dim",
    "DimViewIndexes", "DimViewTicks", "DimViewInstances", "DimViewValues",
]
