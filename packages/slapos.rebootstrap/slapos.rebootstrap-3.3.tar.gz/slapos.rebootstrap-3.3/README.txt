Rerun buildout with a python provided by buildout
===============================================

Buildout 2.0 no-longer supports using multiple versions of Python in a
single buildout. This extension makes it possible to use 'yet another
single' version of python, by building a specified python part and its
dependencies first then reinvoking buildout with the executable.

Usage
-----

A part to build python is required. You need to specify it by `python`
parameter in `buildout` section, just same as buildout 1.x. The python
section must provide executable option that gives the path to a Python
executable.

And add slapos.rebootstrap to `extensions` parameter in `buildout` section.

Use whatever python to bootstrap and run buildout. If this extension
detects that sys.executable used to run buildout is different than
executable provided in python section, it will try to find this
executable. If it does not exists, it will install this section and
then reinstall buildout using new python executable. Later buildout
run will continue using new python.

Example profile and invocation
------------------------------
::

  [buildout]
  extensions = slapos.rebootstrap
  python = slapospython
  
  parts =
    realrun
  
  [slapospython]
  recipe = plone.recipe.command
  stop-on-error = true
  command = mkdir -p ${buildout:parts-directory}/${:__section_name__}/bin &&
    cp -f /usr/bin/python ${:executable}
  
  [realrun]
  recipe = plone.recipe.command
  command =
    echo Running with python ${buildout:executable}
  update-command = ${:command}

After bootstrapping and running this buildout it will print:

Running with python /path/to/buildout/parts/slapospython/bin/slapospython

Running tests
-------------

Test for this package can be run as simple as:

 $ python setup.py test

Please keep in mind that clean python environment is required -- the best one is
provided by buildout or virtualenv *WITHOUT* site packages.
