Installing
==========

It is recommendable to install SciExp² either as a system package or in the home directory, but you can always use it without installing.


From a Debian package
~~~~~~~~~~~~~~~~~~~~~

First, make sure you have package *apt-transport-https* installed::

  sudo apt-get install apt-transport-https

Then you can add the provided repository and install the packages::

  sudo sh -c 'echo "deb https://people.gso.ac.upc.edu/vilanova/packages/sciexp2/debian/ unstable main" > /etc/apt/sources.list.d/sciexp2.list'
  sudo apt-get update
  sudo apt-get install python-sciexp2 python-sciexp2-doc

If you want to install it in the system but cannot (or do not want to) use Debian packages, you should look elsewhere [#system]_.

.. [#system] http://docs.python.org/install/index.html


From the Python Package Index (PyPi)
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

The simplest system-agnostic way use SciExp² is by installing it from the official Python Package Index (https://pypi.python.org) using :program:`virtualenv` and :program:`pip` [#virtualenv]_.

Once you have both :program:`virtualenv` and :program:`pip` installed, you can create as many "environments" as you want (e.g., one for each different version of the SciExp² package if you want to test different versions)::

  virtualenv --system-site-packages ~/my-sciexp2
  . ~/my-sciexp2/bin/activate
  pip install sciexp2

If you want to ignore the python packages installed on the system, you can instead run::

  virtualenv ~/my-sciexp2
  . ~/my-sciexp2/bin/activate
  pip install sciexp2

And to install a specific version::

  virtualenv --system-site-packages ~/my-sciexp2
  . ~/my-sciexp2/bin/activate
  pip install "sciexp2==some_version"

Older versions are available in [#files]_, and can also be installed on a virtual Python environment::

  virtualenv --system-site-packages ~/my-sciexp2
  . ~/my-sciexp2/bin/activate
  pip install https://projects.gso.ac.upc.edu/.../SciExp²-some_version.tar.gz


.. [#virtualenv] http://www.pip-installer.org/en/latest/installing.html
.. [#files] https://projects.gso.ac.upc.edu/projects/sciexp2/files


From a source checkout
~~~~~~~~~~~~~~~~~~~~~~

You can also use a copy of the upstream repositories [#repos]_. By default it will use the latest stable version, but you can feel the thrill of using the latest and greatest development version by getting a checkout of the ``develop`` branch.

To install a checkout (of the stable branch), you can::

  git clone https://code.gso.ac.upc.edu/git/sciexp2
  cd sciexp2
  python ./setup.py sdist

  virtualenv --system-site-packages ~/my-sciexp2
  . ~/my-sciexp2/bin/activate
  pip install dist/sciexp2-some_version.tar.gz

.. [#repos]  https://projects.gso.ac.upc.edu/projects/sciexp2/repository


Running
=======

If you have installed SciExp² using :program:`pip`, just remember to activate your environment before using it::

  . ~/my-sciexp2/bin/activate
  # programs and paths are now properly set up

If you where too lazy to install it, or are using an always up-to-date checkout, just remember to modify the :data:`sys.path` variable from your script, or execute it with `PYTHONPATH <http://docs.python.org/2/using/cmdline.html#envvar-PYTHONPATH>`_ properly set to point to the directory that contains your copy of SciExp²::

  git clone https://code.gso.ac.upc.edu/git/sciexp2 ~/sciexp2
  PYTHONPATH=~/sciexp2 /path/to/my/script.py

.. note::

   Many potentially long operations provide a feedback in the form of progress indicators; you can control whether they are shown through the `sciexp2.common.progress.level` routine.


Integrating with make
~~~~~~~~~~~~~~~~~~~~~

If you have a system automated through :program:`make`, you probably want to make sure it always uses the same SciExp² version to avoid future version incompatibilities. Assuming your script ``do-something.py`` uses SciExp², you can use the following snippet in your makefile::

  all: deps/sciexp2
  	( . deps/sciexp2/bin/activate && ./do-something.py )

  # the ".done" file ensures a partial installation will not count as a success
  deps/sciexp2: deps/sciexp2/.done
  	$(RM) -R $@
        mkdir -p $(dir $@)
  	virtualenv --system-site-packages $@
  	( . $@/bin/activate && pip install "sciexp2==some_version" )
  	touch $<


Nicer testing and debugging of your code
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

`IPython <http://ipython.org>`_ is an interactive Python shell that can help you in interactively developing your code thanks to its dynamic object information [#info]_, as well as can help you visualizing and debugging errors on your code.

For starters, you can run your code with the :program:`ipython` binary and get prettified back-traces for free. You can also start it as ``ipython --pdb my-script.py`` and you will get into a debugging shell whenever an error occurs [#pdb]_.

Finally, you can add this anywhere in your code to start an IPython shell to interactively evaluate the state of your code, returning to its normal execution whenever you exit the shell [#embed]_::

  from IPython import embed
  embed()

.. [#info] http://ipython.org/ipython-doc/stable/interactive/reference.html#dynamic-object-information
.. [#pdb] http://ipython.org/ipython-doc/stable/interactive/reference.html#automatic-invocation-of-pdb-on-exceptions
.. [#embed] http://ipython.org/ipython-doc/stable/interactive/reference.html#embedding-ipython
