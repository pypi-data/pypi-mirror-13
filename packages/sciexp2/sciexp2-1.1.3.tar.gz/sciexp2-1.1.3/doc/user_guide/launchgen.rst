.. _launchgen:

Experiment creation --- `~sciexp2.launchgen`
============================================

The ultimate objective of the `~sciexp2.launchgen` module is to define a set of experiments and create a self-contained directory with all the files necessary for running these experiments. The reason to make it self-contained is that this directory can then be moved into the system(s) where the experiments must be run (e.g., a cluster).

For the sake of making the description more tangible, this guide will show how to generate experiments to evaluate all benchmarks on a simple benchmark suite, where each benchmark is run with different arguments inside a simulator that uses different configuration parameters (specified in a configuration file). Thus, each experiment will be defined by the tuple containing the benchmark identifiers plus the different configuration parameter permutations defined by the user. The initial file organization is the following::

  .
  |- mysimulator       # source code for the simulator
  |  |- Makefile
  |  `- mysim.c
  |- mysim.cfg.in      # template configuration file for the simulator
  `- mybenchsuite      # benchmark suite
     |- 1.foo          # source code for a specific benchmark
     |  |- source.c
     |  `- Makefile
     |- 2.bar
     |  |- source.c
     |  `- Makefile
     |- 3.baz
     |  |- source.c
     |  `- Makefile
     |- README         # files that can be ignored
     `- NEWS

The roadmap to create an ``experiments`` directory that will contain all the necessary pieces for our example is the following:

#. Prepare the output directory by eliminating any previous contents of the ``experiments`` directory.

#. Execute external programs to compile the simulator and the benchmarks.

#. Dynamically discover the available benchmarks.

#. Copy files for the simulator and each of the selected benchmarks into the ``experiments`` directory.

#. Define different sets of arguments to run the benchmarks with different inputs.

#. Define different configuration parameter combinations for the simulator.

#. Generate files from templates by :term:`translating <translation>` variable references with their values, producing the simulator configuration file for each set of simulation parameters, and generating scripts to execute each of the simulations.

Of course, this is just one example, and there is no specific order in which you must use the described methods.


Script preparation
------------------

In order to avoid some typing in the script, the `sciexp2.launchgen.env` module can be used. It instantiates a default `~sciexp2.launchgen.Launchgen` object and puts its methods as top-level functions (together with a few other goodies)::

  #!/usr/bin/env python
  # -*- python -*-

  from sciexp2.launchgen.env import *

  # file contents ...

This "default" instance is available as the ``default_launchgen`` variable.


Directory preparation
---------------------

First, we set the output directory on the `~sciexp2.launchgen.Launchgen.out` attribute to ``./experiments``, where all files will be generated, and use `~sciexp2.launchgen.Launchgen.execute` to run a shell command that removes all its previous contents (both executions are equivalent)::

  default_launchgen.out = "./experiments"
  execute("rm -Rf %s" % default_launchgen.out)
  execute("rm", "-Rf", default_launchgen.out)

Note that relative paths start at the directory from where our script is being executed, as well as external commands are also executed from there.

.. note::

   It can be beneficial to *not* remove the output directory, as methods  `~sciexp2.launchgen.Launchgen.pack`,  `~sciexp2.launchgen.Launchgen.generate` and  `~sciexp2.launchgen.Launchgen.launcher` (see below) already take care of overwriting destination files only of their contents are outdated; for example, running make on the files inside the output directory will behave properly if the source files copied into that directory have not changed since they were last transferred.


Compile and copy the simulator
------------------------------

As there is only one simulator, the compilation can be executed right away, and after that the resulting binary can be copied into the output directory with `~sciexp2.launchgen.Launchgen.pack`::

  execute("make", "-C", "./mysimulator")
  # copied into 'experiments/bin/mysim'
  pack("./mysimulator/mysim", "bin/mysim")


Find, compile and copy benchmarks
---------------------------------

As hard-coding the list of benchmarks is not desirable, it is much better to dynamically detect them with `~sciexp2.launchgen.Launchgen.find_files`::

  find_files("./mybenchsuite/[0-9]*\.@benchmark@/",
             v_.benchmark != 'bar')

The first argument is an :term:`expression` to find all benchmark directories, and the following is a list of filters (in this case with a single element) to narrow which of these directories we're interested in (in this case, all but *baz*). Note that the filter uses the special variable `v_`, which is provided by the `sciexp2.launchgen.env` module as an instance of `~sciexp2.common.filter.PFilter` (instead, we could also have used a string for the filter: ``"benchmark != 'bar'"``).

The result is that the `~sciexp2.launchgen.Launchgen.contents` attribute is extended with one :term:`instance` for each of the found files that match the given expression and filters (directories, in this case), where such instances are :term:`extracted <extraction>` from the given expression by using the paths found by `~sciexp2.launchgen.Launchgen.find_files`::

  >>> default_launchgen
  Launchgen([Instance({'benchmark': 'foo', 'FILE': './mybenchsuite/1.foo/'}),
             Instance({'benchmark': 'baz', 'FILE': './mybenchsuite/3.baz/'})])

Note that the trailing slash in the expression prevents the match of the `txt` files in the ``./mybenchsuite`` directory, as well as the specified :term:`filter` prevents the matching of the ``2.bar`` benchmark.

Then, we call ``make`` into each of the selected benchmarks, and copy the resulting binaries into the output directory::

  # results in executing the following commands:
  #   make -C ./mybenchsuite/1.foo/
  #   make -C ./mybenchsuite/3.baz/
  execute("make", "-C", "@FILE@")

  # results in the following copies:
  #   ./mybenchsuite/1.foo/foo -> ./experiments/benchmarks/foo
  #   ./mybenchsuite/3.baz/baz -> ./experiments/benchmarks/baz
  pack("@FILE@/@benchmark@", "benchmarks/@benchmark@")

See that both command execution and file copying use :term:`expressions <expression>`, and the actual operations are performed on the :term:`expansion` of such expressions for each of the instances we have.


.. note::

   Higher level methods based on `~sciexp2.launchgen.Launchgen.find_files` are available for finding and parsing specific contents (e.g., `SPEC <http://www.spec.org>`_ benchmarks or `SimPoint <http://cseweb.ucsd.edu/~calder/simpoint/>`_ results). See `~sciexp2.launchgen.Launchgen` for details.


Define experiment parameters
----------------------------

Defining the experiment parameters is one of the heavy-weight operations, which is encapsulated in the `~sciexp2.launchgen.Launchgen.params` method. First of all, we want each benchmark to execute with different arguments, which are benchmark specific::

  FOO_ARGS = ["small", "big"]
  with select(v_.benchmark == 'foo') as s:
      s.params(argset=len(FOO_ARGS),
               args=FOO_ARGS)

  import math
  BAZ_ARG1 = range(2)
  BAZ_ARG2 = range(2)
  with select(v_.benchmark == 'baz') as s:
      s.params((v_.arg1 != 0) | (v_.arg2 != 0),
               argset=range(len(BAZ_ARG1) * len(BAZ_ARG2)),
               args="@arg1@ @arg2@ @arg3@",
               arg1=BAZ_ARG1,
               arg2=BAZ_ARG2,
               arg3=defer(math.log, defer("arg1") + defer("arg2"), 2),
               )

First, we select a subset of the contents with `~sciexp2.launchgen.Launchgen.select`, which returns a view to that subset so that we can operate on it; although it is not necessary, using Python's ``with`` statement can improve code readability in these cases. Then, for the *foo* benchmark we define two different arguments. The case of the the *baz* benchmark is more complex, as we define its argument list (``args``) as a string that contains the values of three other arguments: ``arg1`` and ``arg2`` have all integer values from zero to two (`range` is a Python built-in that returns all numbers in the specified numeric range), while ``arg3`` is the logarithm in base two of the two previous arguments (function `~sciexp2.launchgen.defer` is used to defer the call to `math.log` until the parameter permutation is performed, when the actual values for *arg1* and *arg2* are known). Note that the parameters for the *baz* benchmark contain a filter to ignore the combinations where both ``arg1`` and ``arg2`` are zero (as the logarithm is infinite). In both cases, we also generate the ``argset`` variable that will later help us in uniquely identifying each of the benchmark's argument sets.

.. warning::

   The *programmatic filter* used in the example above is implemented by overloading certain operations. As the logical *and* and logical *or* cannot be overloaded, it uses the bit-wise *and* and bit-wise *or* instead, which have a different operator precedence; thus parentheses must be used to evaluate the expression in the proper order.

This results in taking the previous contents and substituting each of its elements with some new elements that contain new variables for each of the parameter combinations specified in the calls to the `~sciexp2.launchgen.Launchgen.params` method (it actually performs the *cartesian product*)::

  >>> default_launchgen
  Launchgen([Instance({'argset': 0, 'args': 'small', 'benchmark': 'foo', 'FILE': './mybenchsuite/1.foo/'}),
             Instance({'argset': 1, 'args': 'big', 'benchmark': 'foo', 'FILE': './mybenchsuite/1.foo/'}),
             Instance({'argset': 0, 'args': '0 1 0', 'arg1': 0, 'arg2': 1, 'arg3': 0, 'benchmark': 'baz', 'FILE': './mybenchsuite/3.baz/'}),
             Instance({'argset': 1, 'args': '1 0 0', 'arg1': 1, 'arg2': 0, 'arg3': 0, 'benchmark': 'baz', 'FILE': './mybenchsuite/3.baz/'}),
             Instance({'argset': 2, 'args': '1 1 1', 'arg1': 1, 'arg2': 1, 'arg3': 1, 'benchmark': 'baz', 'FILE': './mybenchsuite/3.baz/'})])

The values (right-hand-side) of one variable (the left-hand-side on each parameter argument) can either be a single element or a sequence of elements, where each element can be any of:

  - *Immediate values*: In the case of strings, they are treated as :term:`expressions <expression>`, which are :term:`translated <translation>`.

  - *The* `~sciexp2.launchgen.defer` *function*: Used when the literal value is necessary (e.g., no stringification) for operating later with it (e.g., an integer).

In addition to the benchmark arguments, we also need to define the simulation parameters::

  params(v_.l1 <= v_.l2,
         v_.l1_assoc <= v_.l2_assoc,
         cores=range(1, 5),
         l1=[2**x for x in range(1,  6)], # size in KB
         l2=[2**x for x in range(1, 10)],
         l1_assoc=[1, 2, 4],
         l2_assoc=[1, 2, 4, 8],
        )

.. note::

   As can be seen from the previous examples, multiple calls to `~sciexp2.launchgen.Launchgen.params` keep updating the contents. If this is not desired, either different `~sciexp2.launchgen.Launchgen` objects must be explicitly used, or the argument ``append=True`` can be passed to append new entries instead of recombining them with the existing contents.


Generate simulator configuration files
--------------------------------------

The contents of a `~sciexp2.launchgen.Launchgen` can be used to generate files from an input template, by substituting variable references with the specific values on each instance. In this example, the contents of the ``mysim.cfg.in`` file are::

  cores = @cores@
  l1_size  = @l1@         # Bytes
  l1_assoc = @l1_assoc@
  l2_size  = @l2@         # Bytes
  l2_assoc = @l2_assoc@

The target here is to generate one simulator configuration file for each combination of simulation parameters we have in our contents, which is achieved through the `~sciexp2.launchgen.Launchgen.generate` method::

  generate("mysim.cfg.in", "conf/@cores@-@l1@-@l1_assoc@-@l2@-@l2_assoc@.cfg",
           # convert from KB into B
           l1=defer("l1") * 1024,
           l2=defer("l2") * 1024,
          )

What `~sciexp2.launchgen.Launchgen.generate` does is, for each possible expansion of the second argument (which is an expression), take the file in the first argument (which could also be an expression), and use the instance corresponding to that expansion to :term:`translate <translation>` the file contents (the input file is, in fact, treated as a gigantic string whose contents are then translated).

It is important to note that `~sciexp2.launchgen.Launchgen.generate` can also perform parameter recombination like `~sciexp2.launchgen.Launchgen.params`, which we use to translate the values for *l1* and *l2* "in-place", as the configuration file expects bytes (while we defined these parameters as kilo-bytes). Although the same could be accomplished by first invoking `~sciexp2.launchgen.Launchgen.params` and then `~sciexp2.launchgen.Launchgen.generate` (without any parameter arguments), the difference is that `~sciexp2.launchgen.Launchgen.generate` does not update the contents with its results, which only exist during the file generation process. This can be helpful to keep the contents "clean" of intermediate variables and values by only defining them during the generation of specific files (as is the case for the *l1* and *l2* variables in the example).

.. warning ::

   For each possible simulation parameter combination, there exist multiple benchmark/argument combinations. That is, there are multiple instances in the contents that expand to the output file expression. When such things happen, the output file will only be generated once with the first instance expanding to that expression, and subsequent instances will simply show the message "*Skipping already generated file*".


Generate an execution script for each experiment
------------------------------------------------

The final step is to generate some scripts to actually run the selected benchmarks with each of the simulation parameter combinations. This could be accomplished by using `~sciexp2.launchgen.Launchgen.generate`, but the `~sciexp2.launchgen.Launchgen.launcher` method is an extension of it that already has some pre-defined templates, as well as also produces some extra metadata for the :program:`launcher` program, that can be later used to execute the experiments.

The first thing to do is to determine which of the pre-defined templates will be used by looking at the output of :program:`launchgen`'s :option:`--list-templates` option. Each of the templates has some variables that must be filled-in by the user, which are shown by :program:`launchgen`'s :option:`--show-template` option, as well as also has an associated execution system.

In this example we will use the *shell* template, which looking at the output of the ``launchger -T shell`` we can see that the *CMD* variable needs to be defined, which contains the actual command-line that will execute whatever we want::

  launcher("shell", "jobs/@ID@.sh",
           # save some typing by defining these once and for all
           ID="@benchmark@-@argset@-@SIMID@",
           SIMID="@cores@-@l1@-@l1_assoc@-@l2@-@l2_assoc@",

           DONE="res/@ID@.done",
           FAIL="res/@ID@.fail",

           CMD="""
  # Python multi-line strings can be used here to write commands in multiple lines
  ./bin/mysim -config conf/@SIMID@.cfg -output @DONE@ -bench ./benchmarks/@benchmark@ @args@
  """,
          )

The first two arguments are almost the same as in `~sciexp2.launchgen.Launchgen.generate` (except that the first argument -- `template` -- is not an expression for a set of input files, but the name of a valid template for :program:`launcher`), just like the trailing parameters (where *CMD* is contained).

Additionally, the file *jobs.jd* will be generated, and the example provides values for the *DONE* and *FAIL* variables, all of which are later used by the :program:`launcher` program to detect if an experiment has been run and, if so, whether it finished correctly. If not specified, these two variables will be given some default value (see `~sciexp2.launchgen.Launchgen.launcher`).

In this case, the variable *CMD* contains the command-line to run the simulator with the specified configuration file, as well as a specific benchmark along with its arguments. It also instructs the simulator to save its output in the value of the *DONE* variable.

.. note::

   In order to save some typing, templates may provide default values. In this case there is no need to provide any value for these variables, but the default can be overridden by simply setting such variable, just like any other.

.. note::

   In some cases it might be useful to set `~sciexp2.launchgen.Launchgen.launcher`'s *export* argument, which will make the variables listed in it available to the :program:`launcher` program (default to the variables present in the *to_expr* argument). These variables can then be used to select which experiments :program:`launcher` should operate on.

.. note::

   If specified, variable *DEPENDS* is interpreted as a list of variables that `~sciexp2.launcher` will check to establish whether a job needs reexecution (i.e., the files identified by these variables are newer than *DONE*). This list always contains *LAUNCHER*. Coupled with the behaviour of the file-copying and -generation methods, `~sciexp2.launcher` will always keep track of what experiments get out-of-date.


Writing new templates
---------------------

Sometimes using some of the pre-defined templates is not enough, but the ability to use the result with :program:`launcher` is still desirable (e.g., query the state of experiments, run a specific sub-set of experiments, etc.). In such cases, the contents of a template can be overridden by creating a new file with the same name as the template (e.g. ``shell.tpl`` in the previous example, stored in the directory from where the example script is executed).

For even greater flexibility, brand new templates can be created by writing a new template description file (e.g., ``new-template-name.dsc``, which defines default values and the execution system, among others), as well as the optional template definition file (e.g., ``new-template-name.tpl``).

All these files can reside in any of the directories in the `~sciexp2.templates.SEARCH_PATH`, which by default includes the directory from where the script is executed.

.. seealso:: `sciexp2.templates`


Wrap-up
-------

To wrap things up, here's the complete file covering the whole example::

  #!/usr/bin/env python
  # -*- python -*-

  import math

  from sciexp2.launchgen.env import *

  # reset output directory
  default_launchgen.out = "./experiments"
  execute("rm", "-Rf", default_launchgen.out)

  # compile & copy simulator
  execute("make", "-C", "./mysimulator")
  pack("./mysimulator/mysim", "bin/mysim")

  # find & compile & copy benchmarks
  find_files("./mybenchsuite/[0-9]*\.@benchmark@/",
             v_.benchmark != 'bar')
  execute("make", "-C", "@FILE@")
  pack("@FILE@/@benchmark@", "benchmarks/@benchmark@")


  # benchmark arguments
  FOO_ARGS = ["small", "big"]
  BAZ_ARG1 = range(2)
  BAZ_ARG2 = range(2)
  with select(v_.benchmark == 'foo') as s:
      s.params(argset=len(FOO_ARGS),
               args=FOO_ARGS)
  with select(v_.benchmark == 'baz') as s:
      s.params((v_.arg1 != 0) | (v_.arg2 != 0),
               argset=range(len(BAZ_ARG1) * len(BAZ_ARG2)),
               args="@arg1@ @arg2@ @arg3@",
               arg1=BAZ_ARG1,
               arg2=BAZ_ARG2,
               arg3=defer(math.log, defer("arg1") + defer("arg2"), 2),
               )

  # simulation parameters
  params(v_.l1 <= v_.l2,
         v_.l1_assoc <= v_.l2_assoc,
         cores=range(1, 5),
         l1=[2**x for x in range(1,  6)], # size in KB
         l2=[2**x for x in range(1, 10)],
         l1_assoc=[1, 2, 4],
         l2_assoc=[1, 2, 4, 8],
        )

  # simulator config file
  generate("mysim.cfg.in", "conf/@cores@-@l1@-@l1_assoc@-@l2@-@l2_assoc@.cfg",
           # convert from KB into B
           l1=defer("l1") * 1024,
           l2=defer("l2") * 1024,
          )

  # generate execution scripts
  launcher("shell", "jobs/@ID@.sh",
           # save some typing by defining these once and for all
           ID="@benchmark@-@argset@-@SIMID@",
           SIMID="@cores@-@l1@-@l1_assoc@-@l2@-@l2_assoc@",

           CMD="""
  # Python multi-line strings can be used here to write commands in multiple lines
  ./bin/mysim -config conf/@SIMID@.cfg -output @DONE@ -bench ./benchmarks/@benchmark@ @args@
  """,
          )

Although this might look unnecessarily long, `~sciexp2.launchgen.Launchgen`'s ability to concisely specify parameter permutations and apply filters on them can keep large parameter explorations under control.
