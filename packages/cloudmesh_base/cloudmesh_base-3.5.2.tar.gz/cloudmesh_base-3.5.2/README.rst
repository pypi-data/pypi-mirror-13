cloudmesh_base 
==============

A set of helper functions that are used in cloudmesh but are also
useful for other projects.

You can install it in one of two ways.

Instalation from pip
----------------------

::

   pip install cloudmesh_base


Installation from Source
--------------------------------

::

   mkdir -p github/cloudmesh
   cd github/cloudmesh
   git clone https://github.com/cloudmesh/base.git
   cd base
   pip install -r requirements.txt
   python setup.py install
  

   

Provided Functionality
----------------------------------------------------------------------

* ConfigDict -- an ordered dictionary to read configurations from YAML
  files
* Shell -- a convenient wrapper to python sh so that pylint does not
  complain all the time when importing commands from sh
* dotdict -- a simple dict with dot notation
* gitinfo -- get some information about authors and their statistics
  for a git repository
* menu -- a simple ascii menu so we can chose easily from options
* ping -- a simple ping (see also Shell)
* ssh_config -- a simple tool to read ./ssh/config into a dict
* stopwatch -- a simple stopwatch to measure times
* tables -- a simple table printer that prins dicts in a uniform table
* util -- a number of useful functions including yn_choice, banner,
  path_expand, introspecting and printing the method name at runtime,
  copy files, replace dict values in a string similar but less
  complicated to .format, read a file to a string, write a string to a file
* hostlist -- a repackaged version of hostlist to accociate it with Parameter
  parsing
  

Source Code
----------------------------------------------------------------------

* https://github.com/cloudmesh/base

