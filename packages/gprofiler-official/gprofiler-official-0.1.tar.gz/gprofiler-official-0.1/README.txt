
gprofiler-official
==================

The official Python interface to the g:Profiler [1] toolkit for enrichment
analysis of functional (GO and other) terms. 

Installation on Linux using pip
-------------------------------

The pip tool [4] is the recommended method of installing Python packages.

Optionally create a virtual environment [2]::

$ virtualenv2 myenv
$ source myenv/bin/activate

Install the software with pip, see [3] for instructions::

$ pip install gprofiler-official

Make sure that the installed gprofiler.py script is on your $PATH. When using
a virtual environment as shown above, this should happen automatically.

Run an example query::

$ gprofiler.py -o scerevisiae "swi4 swi6"

For detailed usage instructions, see::

$ gprofiler.py --help

Installation on Linux using the tarball
---------------------------------------

You may simply download the tarball from gprofiler-official PyPI page [5],
extract it and use the gprofiler.py script without installation. The script is
designed to be lightweight and not require any 3rd party modules. For detailed
usage instructions, see::

$ gprofiler.py --help

Installation on other platforms
-------------------------------

Please see [3] for package installation instructions on various platforms.

* [1] http://biit.cs.ut.ee/gprofiler
* [2] http://docs.python-guide.org/en/latest/dev/virtualenvs/
* [3] https://python-packaging-user-guide.readthedocs.org/en/latest/installing/
* [4] https://pip.pypa.io/en/stable/
* [5] https://pypi.python.org/pypi/gprofiler-official

