Introduction
============

SciExp² (aka *SciExp square* or simply *SciExp2*) stands for *Scientific Experiment Exploration*, which contains a comprehensive framework for easing the workflow of creating, executing and evaluating experiments.

The driving idea behind SciExp² is the need for quick and effortless *design-space exploration*. It is divided into the following main pieces:

* **Launchgen**: Aids in the process of defining experiments as a permutation of different parameters in the design space, creating the necessary files to run them (configuration files, scripts, etc.).

* **Launcher**: Takes the result of `~sciexp2.launchgen` and integrates with some well-known execution systems (e.g., simple shell scripts or gridengine) to execute and keep track of the experiments (e.g., re-run failed experiments, or run those whose files have been updated). In addition, experiments can be operated through filters that know about the parameters used during experiment generation.

* **Data**: Aids in the process of collecting and analyzing the results of the experiments. Results are collected into arrays whose dimensions can be annotated by the user (e.g., to identify experiment parameters). It also provides functions to automatically extract experiment results into annotated arrays (implemented as `numpy` arrays with dimension metadata extensions).

The framework is available in the form of Python modules which can be easily integrated into your own applications or used as a scripting environment.


Quick example
-------------

As a quick example, we'll see how to generate scripts to run an application, run these scripts, and evaluate their results. First, we'll start by generating the per-experiment scripts in the ``experiments`` directory, which will basically execute ``my-program`` with different values of the ``--size`` argument, generating a CSV file with results for each experiment::


  #!/usr/bin/env python
  # -*- python -*-

  from sciexp2.launchgen.env import *

  l = Launchgen(out="experiments")
  l.pack("/path/to/my-program", "bin/my-program")
  l.params(size=[1, 2, 4, 8])
  l.launchgen("shell", "scripts/@size@.sh",
              CMD="bin/my-program --size=@size@ --out=results/@size@.csv")


The ``experiments`` directory now contains all the files we need. Then, we'll execute all the experiments with::

  ./experiments/jobs.jd submit

The relevant contents of the ``experiments`` directory after executing the experiments are thus::

  experiments
  |- bin
  |  `- my-program
  |- scripts
  |  |- 1.sh
  |  |- 2.sh
  |  |- 4.sh
  |  `- 8.sh
  `- results
     |- 1.csv
     |- 2.csv
     |- 4.csv
     `- 8.csv

Let's assume that ``my-program`` runs the same operation multiple times, and the output CSV files contain a line with the execution time for each of these runs, like::

  run,time(sec)
  0,3.2
  1,2.9
  ...

Finally, we'll gather the results of all experiments and print the average execution time across runs for each value of the ``size`` parameter::

  #!/usr/bin/env python
  # -*- python -*-

  from sciexp2.data.env import *

  # auto-extract all results
  d = extract_txt('experiments/results/@size@.csv',
                  fields_to_vars=["run"])
  # experiment size as first dimension, run number as second
  d = d.reshape(["size"], ["run"])
  # get mean of all runs (one mean per size)
  d = d.mean(axis="run")
  # print CSV-like mean of each size
  print("size, time")
  for foo in d.dims["size"]:
      print("%4d," % size, d[size])

The result could be something like::

  size, time
     1, 3.05
     2, 3.39
     4, 4.61
     8, 6.37
