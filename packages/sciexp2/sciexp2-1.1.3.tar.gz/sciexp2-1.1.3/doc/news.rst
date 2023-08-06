.. _news:

Changes in SciExp²
==================

Brief description of changes introduced on each version. For a list of the resolved issues on each version please see the :home:`roadmap` page and enable the "`Show completed versions`" option on the sidebar.


1.1.3
-----

.. rubric:: External compatibility breaks

.. rubric:: New features

* Add method `sciexp2.data.DataIndexer.as_tuple`.

.. rubric:: Improvements

* Improve output file initialization in the shell template.
* Ignore empty variable values in argument ``DEPENDS`` of `sciexp2.launchgen.Launchgen.launcher` (closes :issue:`298`).
* Do not warn when `sciexp2.data.io.lazy` receives only non-lazy arguments.

.. rubric:: Bug fixes

* Fix boolean negation operator in `~sciexp2.common.filter.Filter`.
* Fix `~sciexp2.data.Data.ravel`.

.. rubric:: Documentation

.. rubric:: Internals


1.1.2
-----

.. rubric:: External compatibility breaks

.. rubric:: New features

.. rubric:: Improvements

* Allow setting `~sciexp2.data.meta.Dim` ticks to ``None``.
* Remove most limitations of assignments to `sciexp2.data.meta.Dim.expression` and `sciexp2.data.meta.Dim` contents.
* Generalize the following functions to work with any type of arrays: `sciexp2.data.append`, `sciexp2.data.concatenate`, `sciexp2.data.copy`, `sciexp2.data.delete`, `sciexp2.data.drop_fields`, `sciexp2.data.imag`, `numpy.lib.recfunctions.merge_arrays`, `sciexp2.data.ravel`, `sciexp2.data.real`, `numpy.lib.recfunctions.rename_fields`.
* Improve output file initialization in the shell template.
* Ignore empty variable values in argument ``DEPENDS`` of `sciexp2.launchgen.Launchgen.launcher` (closes :issue:`298`).

.. rubric:: Bug fixes

* Properly escape `sciexp2.data.meta.Dim.expression` values to avoid confusing the user's string with parts of a regular expression.
* Fix boolean negation operator in `~sciexp2.common.filter.Filter`.
* Fix `~sciexp2.data.Data.ravel`.

.. rubric:: Documentation

.. rubric:: Internals

* Fix hard resets on `sciexp2.common.instance.InstanceGroup.cache_reset`.
* Fix `sciexp2.data.DataDims` copies.
* Implement consistent named axis selection (``axis`` argument in numpy function) when using multiple array arguments.
* Follow `numpy`'s exception format when using a non-existing field name.


1.1.1
-----

.. rubric:: External compatibility breaks

* Remove argument ``filters`` in `sciexp2.launchgen.Launchgen.expand` in favour of `sciexp2.launchgen.Launchgen.select` (closes :issue:`300`).
* Deprecate argument ``export`` in `sciexp2.launchgen.Launchgen.launcher` in favour of new value ``EXPORTS`` in argument ``values`` (closes :issue:`301`).

.. rubric:: New features

.. rubric:: Improvements

.. rubric:: Bug fixes

* Fix filter optimization (breaks construction from multiple filters).
* Allow comparing variables in `~sciexp2.common.filter.PFilter` with strings (fixes :issue:`302`, as a refinement of :issue:`278`).
* Do not complain when about empty views when using `sciexp2.launchgen.Launchgen` methods (fixes :issue:`296`).

.. rubric:: Documentation

* Clarify use cases of ``files`` sub-command in :program:`launcher`.
* Clarify how variables are substituted in `sciexp2.launchgen.Launchgen.params`.

.. rubric:: Internals

* Fix representation of strings in `~sciexp2.common.filter.Filter` objects (was breaking escape sequences, used in regular expressions).


1.1
---

.. rubric:: External compatibility breaks

* Remove `sciexp2.data.Data.dim_sort` and ``dim_sort`` argument in `sciexp2.data.Data.reshape` in favour of `sciexp2.data.meta.Dim.sort`.
* Remove unused "filter override" operator.
* Deprecate "add" operation in `~sciexp2.common.filter.Filter` in favour of "and".
* Forbid `~sciexp2.data.Data` indexing with intermediate results from `~sciexp2.data.DataIndexer`.

.. rubric:: New features

* Allow sorting `sciexp2.data.Data` arrays using `sciexp2.data.meta.Dim.sort` (closes :issue:`279`).
* Add filter syntax to check variable existence (``exists(VAR)``; closes :issue:`262`).
* Add ``--inverse`` argument in :program:`launcher` to easily invert the job state selection (closes :issue:`287`).
* Add `sciexp2.data.meta.Dim.values` and  `sciexp2.data.meta.Dim.unique_values` to easily retrieve per-variable values (closes :issue:`290`).
* Add `sciexp2.launchgen.Launchgen.translate` and `sciexp2.launchgen.Launchgen.expand` to translate and expand expressions from instances (closes :issue:`276`).
* Add `sciexp2.data.Data.idata` attribute to allow immediate dimension-oblivious indexing (shortcut to `sciexp2.data.Data.indexer`; closes :issue:`282`).

.. rubric:: Improvements

* Auto-optimize filter matching.
* Using `sciexp2.launchgen.LaunchgenView.select_inverse` works properly on nested views (only inverts the last selection).
* Allow `sciexp2.launchgen.Launchgen.pack` to dereference symbolic links (closes :issue:`280`).
* Allow `sciexp2.data.Data.indexer` to accept `~sciexp2.common.filter.PFilter` instances (closes :issue:`284`).
* Allow arbitrary values to be returned by functions used through `sciexp2.data.io.lazy` and similar (closes :issue:`285`).
* Simplify use of variables in the ``files`` sub-command of :program:`launcher` (closes :issue:`281`).
* Allow selecting multiple dimensions in `sciexp2.data.DataDims` and `sciexp2.data.DataIndexer`.

.. rubric:: Bug fixes

* Fix bug in string representation for `sciexp2.common.filter.Filter`.
* Fix indexing in `~sciexp2.data.meta.Dim` when using filters as a start and/or stop slice.
* Fix management of ``DONE`` and ``FAIL`` files in the shell template.
* Fix merging of `~sciexp2.common.filter.PFilter` with strings (closes :issue:`278`).
* Fix result of "or" operation in `~sciexp2.common.filter.Filter`.
* Fix array element-wise comparison (metadata is ignored for now).
* Make indexing logic more robust (closes :issue:`283`).

.. rubric:: Documentation

.. rubric:: Internals

* Add method `sciexp2.common.utils.OrderedSet.copy`.
* Add methods `sciexp2.common.utils.OrderedSet.sorted` and `sciexp2.common.utils.OrderedSet.sort`.
* Add method `sciexp2.common.instance.InstanceGroup.sorted`.
* Implement `sciexp2.common.instance.InstanceGroup.sort` as in-place sorting.
* Auto-optimize simple boolean filter expressions.
* Drop argument ``allowed`` in `~sciexp2.common.filter.Filter` (use `~sciexp2.common.filter.Filter.validate` instead).
* Drop method `sciexp2.common.filter.Filter.constant`.
* Provide exception check callback for missing variable references in `~sciexp2.common.instance.InstanceGroup.select` and `~sciexp2.common.instance.InstanceGroup.expand`.
* Drop argument ``allow_unknown`` from `sciexp2.common.filter.Filter.match`; handle from clients instead.
* Never return an `~numpy.ndarray` in `~sciexp2.data.meta.Data._get_indexes` (work around NumPy bug `#6564 <https://github.com/numpy/numpy/issues/6564>`_).
* Allow variables in `~sciexp2.common.utils.find_files` to span more than one directory (closes :issue:`288`).


1.0.2
-----

.. rubric:: External compatibility breaks

.. rubric:: New features

.. rubric:: Improvements

* Show progress message when building new dimensions in `sciexp2.data.Data.reshape`.
* Improve performance of `sciexp2.data.Data.reshape`.

.. rubric:: Bug fixes

* Fix spurious ignored `AttributeError` exceptions when using `~sciexp2.common.progress`.

.. rubric:: Documentation

.. rubric:: Internals


1.0.1
-----

.. rubric:: External compatibility breaks

.. rubric:: New features

.. rubric:: Improvements

* Return ``None`` in `sciexp2.data.meta.Dim.index` when dimension is not associated.

.. rubric:: Bug fixes

* Fix `sciexp2.data.meta.Dim` association when indexing.

.. rubric:: Documentation

.. rubric:: Internals


1.0
---

.. rubric:: External compatibility breaks

* Move dimension-related classes to `sciexp2.data.meta` (with shortened names).
* `sciexp2.data.meta.Dim` constructor no longer performs copies, use `sciexp2.data.meta.Dim.copy` instead.
* Remove argument `copy_dims` from `~sciexp2.data.Data`.
* Remove methods `sciexp2.data.Data.dim` and `sciexp2.data.Data.dim_index` in favour of `sciexp2.data.Data.dims` and `sciexp2.data.meta.Dim.index`, respectively.
* Remove method `sciexp2.data.Data.iteritems`.
* Remove attribute `sciexp2.data.meta.Dim.contents`.
* Remove deprecated (since 0.18) argument `promote` in in data extraction routines (`sciexp2.data.io`).

.. rubric:: New features

* Add `sciexp2.data.meta.Dim.instances` attribute to access the instances of a dimension.
* Add `sciexp2.data.meta.Dim.translate` and `sciexp2.data.meta.Dim.extract`.
* Add `sciexp2.data.DataDims` to query and manipulate collections of dimension metadata objects.
* Allow `~sciexp2.data.meta.Dim` objects with missing ticks or empty expression (closes :issue:`243`).
* Allow `~sciexp2.data.Data` objects with empty dimension metadata (closes :issue:`242`).
* All views of a `~sciexp2.data.Data` object have consistent metadata.
* Allow element and ``expression`` assignments to `~sciexp2.data.meta.Dim` objects (closes :issue:`236`).
* Unhandled `~numpy.ndarray` methods now return a `~sciexp2.data.Data` object without metadata.
* Add `~sciexp2.data.Data.indexer` to facilitate alignment of indexes to dimensions.

.. rubric:: Improvements

* Export `~sciexp2.data.io.lazy_wrap`, `~sciexp2.data.io.lazy_wrap_realize` and `~sciexp2.data.io.lazy_wrap_checkpoint` through `sciexp2.data.env`.
* Return a `~sciexp2.data.Data` when using `~numpy.newaxis` or advanced indexing.
* Allow ``axis`` `numpy.ufunc` argument with multiple values (closes :issue:`274`).
* Let ``keepdims`` `numpy.ufunc` argument return a `~sciexp2.data.Data` object (closes :issue:`275`).
* Return a `~sciexp2.data.Data` object with empty metadata when broadcasting to a `~numpy.ndarray` argument.

.. rubric:: Bug fixes

* Fixed indexing results on `sciexp2.data.meta.Dim.instances`.

.. rubric:: Documentation

* Add a quick example of all modules in the introduction.
* Document array and metadata indexing and manipulation in the user guide.

.. rubric:: Internals

* Move free functions for `~sciexp2.data.Data` objects into `sciexp2.data._funcs`.
* Rename `sciexp2.data.meta.ExpressionError` as `~sciexp2.data.meta.DimExpressionError`.
* Refactor dimension expression logic into `sciexp2.data.meta.DimExpression`.
* Add `~sciexp2.common.progress.progressable_simple` to wrap container iterations with a progress indicator.
* Sanitize `sciexp2.data.meta.Dim` construction.
* Remove the ``EXPRESSION`` internal variable from dimension metadata, making it smaller at the expense of more complex expression lookups (closes :issue:`231`).
* Remove the ``INDEX`` internal variable from dimension metadata, making it smaller at the expense of more costly index lookups.
* Allow constructing views of `sciexp2.data.meta.Dim` objects.


Older versions
--------------

:ref:`news-old`.
