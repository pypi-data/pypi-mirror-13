devpi-client: commands for python packaging and testing
===============================================================

The "devpi" command line tool is typically used in conjunction
with `devpi-server <http://pypi.python.org/pypi/devpi-server>`_.
It allows to upload, test and install packages from devpi indexes.
See http://doc.devpi.net for quickstart and more documentation.

* `issue tracker <https://bitbucket.org/hpk42/devpi/issues>`_, `repo
  <https://bitbucket.org/hpk42/devpi>`_

* IRC: #devpi on freenode, `mailing list
  <https://groups.google.com/d/forum/devpi-dev>`_ 

* compatibility: {win,unix}-py{26,27,33}





Changelog
=========

2.4.0 (2016-1-29)
------------------

- fix issue291: transfer file modes with vcs exports.  Thanks Sergey
  Vasilyev for the report.

- new option "--index" for "install", "list", "push", "remove", "upload" and
  "test" which allows to use a different than the current index without using
  "devpi use" before

- set ``index`` in ``[search]`` section of ``pip.cfg`` when writing cfgs, to
  support ``pip search``


2.3.2 (2015-11-11)
------------------

- fix git submodules for devpi upload. ``.git`` is a file not a folder for
  submodules. Before this fix the repository which contains the submodule was
  found instead, which caused a failure, because the files aren't tracked there.

- new option "devpi upload --setupdir-only" which will only
  vcs-export the directory containing setup.py. You can also
  set "setupdirs-only = 1" in the "[devpi:upload]" section
  of setup.cfg for the same effect.  Thanks Chad Wagner for the PR.


2.3.1 (2015-09-10)
------------------

- fix issue259: print server errors in client


2.3.0 (2015-07-09)
------------------

- fix issue247: possible password leakage to log in devpi-client

- new experimental "-d|--detox" option to run tests via the "detox" distributed testing
  tool instead of "tox" which runs test environments one by one.

- address issue246: make sure we use vcs-export also for building docs (and
  respect --no-vcs for all building activity)

- address issue246: copy VCS repo dir to temporary upload dir to help
  with setuptools_scm. Warn if VCS other than hg/git are used because
  we don't copy the repo in that case for now and thus cause incompatibility
  with setuptools_scm.

- (new,experimental) read a "[devpi:upload]" section from a setup.cfg file
  with a "formats" setting that will be taken if no "--formats" option
  is specified to "devpi upload".  This allows to specify the default
  artefacts that should be created along with a project's setup.cfg file.
  Also you can use a ``no-vcs = True`` setting to induce the ``--no-vcs``
  option.


2.2.0 (2015-05-13)
------------------

- improve internal testing mechanics

- fix regression for "devpi list -f" output which would fail when trying
  to present failures with recent devpi-server versions/tox outputs.

- fix issue222: fix help string

- fix issue190: introduce support for testing universal wheels (platform/interpreter
  specific wheels are not supported yet because they require tox support).  
  Testing a wheel requires that there also is an sdist next to it so
  that tox.ini and the tests can be discovered from it.  Note that this
  means your tox testrun setup must be able to run tests against an
  installed version of the package, not the sdist-inplace version.  If
  your tests reside in a subfolder that has no __init__.py this should
  usually be the case (at least with pytest).

- add experimental "refresh" command to invalidate the pypi release list cache
  of packages.

- show index configuration settings added by plugins in devpi-server >= 2.2.0.


