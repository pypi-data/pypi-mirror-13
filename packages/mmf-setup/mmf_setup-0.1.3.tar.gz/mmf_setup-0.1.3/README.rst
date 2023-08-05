.. -*- rst -*- -*- restructuredtext -*-

.. This file should be written using the restructure text
.. conventions.  It will be displayed on the bitbucket source page and
.. serves as the documentation of the directory.

.. |virtualenv.py| replace:: ``virtualenv.py``
.. _virtualenv.py: https://raw.github.com/pypa/virtualenv/master/virtualenv.py

.. |EPD| replace:: Enthough Python Distribution
.. _EPD: http://www.enthought.com/products/epd.php
.. _Anaconda: https://store.continuum.io/cshop/anaconda
.. _Conda: http://docs.continuum.io/conda
.. _Miniconda: http://conda.pydata.org/miniconda.html

.. _Enthought: http://www.enthought.com
.. _Continuum Analytics: http://continuum.io

.. _Spyder: https://code.google.com/p/spyderlib/
.. _Wakari: https://www.wakari.io
.. _Canopy: https://www.enthought.com/products/canopy/

.. _mercurial: http://mercurial.selenic.com/
.. _virtualenv: http://www.virtualenv.org/en/latest/
.. _IPython: http://ipython.org/
.. _Ipython notebook: \
   http://ipython.org/ipython-doc/dev/interactive/htmlnotebook.html
.. _NBViewer: http://nbviewer.ipython.org
.. |pip| replace:: ``pip``
.. _pip: http://www.pip-installer.org/
.. _git: http://git-scm.com/
.. _github: https://github.com
.. _RunSnakeRun: http://www.vrplumber.com/programming/runsnakerun/
.. _GSL: http://www.gnu.org/software/gsl/
.. _pygsl: https://bitbucket.org/mforbes/pygsl
.. _Sphinx: http://sphinx-doc.org/
.. _SciPy: http://www.scipy.org/
.. _Mayavi: http://code.enthought.com/projects/mayavi/
.. _NumPy: http://numpy.scipy.org/
.. _Numba: https://github.com/numba/numba#readme
.. _NumbaPro: http://docs.continuum.io/numbapro/
.. _Blaze: http://blaze.pydata.org
.. _Python: http://www.python.org/
.. _matplotlib: http://matplotlib.org/
.. _Matlab: http://www.mathworks.com/products/matlab/
.. _MKL: http://software.intel.com/en-us/intel-mkl
.. _Intel compilers: http://software.intel.com/en-us/intel-compilers
.. _Bento: http://cournape.github.com/Bento/
.. _pyaudio: http://people.csail.mit.edu/hubert/pyaudio/
.. _PortAudio: http://www.portaudio.com/archives/pa_stable_v19_20111121.tgz
.. _MathJax: http://www.mathjax.org/
.. _reStructuredText: http://docutils.sourceforge.net/rst.html
.. _Emacs: http://www.gnu.org/software/emacs/
.. _Pymacs: https://github.com/pinard/Pymacs
.. _Ropemacs: http://rope.sourceforge.net/ropemacs.html
.. _PyPI: https://pypi.python.org/pypi

.. _FFTW: http://www.fftw.org
.. _EC2: http://aws.amazon.com/ec2/
.. _QT: http://qt.digia.com

.. |site.USER_BASE| replace:: ``site.USER_BASE``
.. _site.USER_BASE: https://docs.python.org/2/library/site.html#site.USER_BASE


.. default-role:: math

.. This is so that I can work offline.  It should be ignored on bitbucket for
.. example.

.. sidebar:: Sidebar

   .. contents::

===========
 mmf_setup
===========
This meta-project provides an easy way to install all of the python
tools I typically use.  It also serves as a fairly minimal example of
setting up a package the |pip|_ can install, and specifying
dependencies.

In particular, I structure it for the following use-cases:

1. Rapid installation and configuration of the tools I need.  For
   example, I often use [Sage Mathcloud](cloud.sagemath.com).
   Whenever I create a new project, I need to perform some
   initialization.  With this project, it is simply a matter of using
   |pip|_ to install this package, and then using some of the tools.
2. Initial setup of a python distribution on a new computer.  This is
   a little more involved since one needs to first install python (I
   recommend using Miniconda_) and then updating the tools.
3. A place to document various aspects of installing and setting up
   python and related tools.  Some of this is old, but kept here for
   reference.


====================
 Quickstart (TL;DR)
====================

1. Install this package from the source directory, PyPI_, etc. with
   one of the following:

  * **Directly from PyPI** (*This will only work once the project is published on PyPI.*)

   ``pip install --user mmf_setup``

  * **From Source**

    ``pip install --user hg+https://bitbucket.org/mforbes/python_setup``

  * **From Local Source** (*Run this from the source directory after you unpack it.*)

   ``pip install --user .``

  Note: these can be run without the ``--user`` flag if you want to
  install them system-wide rather than into |site.USER_BASE|_.

2. To get the notebook tools for Jupyter (IPython) notebooks, execute
   the following as a code cell in your notebook and then trust the
   notebook with ``File/Trust Notebook``::

       import mmf_setup; mmf_setup.nbinit()

   This will download and enable the calico extensions, as well as set
   the theme which is implemented in the output cell so it is stored
   for use online such as when rendered through NBViewer_.  One can
   specify different themes. (Presently only ``theme='default'`` and
   ``theme='mmf'`` are supported.)

3. To use the shell tools, source the ``mmf_setup`` file:

    ``. mmf_setup``

    This will add a custom ``hgrc`` file to your ``HGRCPATH`` which
    provides commands for committing clean notebooks such as ``hg
    ccommit`` and ``hg cstatus``.


==================
 Installing Tools
==================

The following code will download and install the `Calico notebook
extensions`__ from `here`__::

      import mmf_setup.notebook_configuration
      mmf_setup.notebook_configuration.install_extensions()

======================
 Mercurial (hg) Tools
======================

If you source the output of the ``mmf_setup`` script::

   . mmf_setup

then your ``HGRCPATH`` will be amended to include this projects
``hgrc`` file which does the following:

1. Adds some useful extensions.
2. Adds the following commands:

   * ``hg lga`` (or ``hg lg``): provides a nice concise graphical
     display of the repo.
   * ``hg cstatus`` (or ``hg cst``):
   * ``hg cdiff``: same for ``hg diff``
   * ``hg cediff``: same for ``hg ediff``
   * ``hg crecord``: same for ``hg record``.  Note, this does not
     function like commit - it will not record the notebooks with the
     full output.
   * ``hg ccommit`` (or ``hg ccom``): same for ``hg com`` but also
     commits the full version of the notebooks with output as a new
     node off the present node with the message ``OUT: Automatic commit of
     output``.  The files in the repository will be left with the
     clean commit as the parent so this output commit will be dangling
     unless you want to include it.

Developer Notes
---------------

There are a couple of subtle points here that should be mentioned.

* I explored both ``(un)shelve`` and ``commit/strip`` versions of
  saving the current state.  While the former allows for shorter
  aliases, it can potentially trigger merges, so we use the latter.
* I sometimes write commit hook.  These should only be run on the real
  commit, so we define the alias ``_commit`` which will bypass the
  hooks as `discussed here`__.
* The list of files to strip is generated by ``hg status -man``.  This
  only includes added or modified files.  This, if a notebook was
  commited with output (using ``hg com``) then it will not be
  stripped.
* Our approach of ``. mmf_setup`` sets ``HGRCPATH`` but if this was
  not set before, then this will skip the default search.  As such, we
  insert ``~/.hgrc`` if ``HGRCPATH`` was not previously set.  This is
  not ideal, but short of sticking an ``%include`` statement in the
  users ``~/.hgrc`` file, or creating an ``hg`` alias, I do not see a
  robust solution.  Note: we only insert ``~/.hgrc`` if ``HGRCPATH``
  is not defined - I ran into problems when always inserting it since
  this can change the order of precedence.
* Chain commands with semicolons ``;`` not ``&&`` so that things are
  restored even if a command fails.  (For example, ``hg ccom`` with a
  notebook that only has output changes used to fail early.)

__ https://selenic.com/pipermail/mercurial-devel/2011-December/036480.html


Notes
=====

Various notes about python, IPython, etc. are stored in the docs folder.



__ http://jupyter.cs.brynmawr.edu/hub/dblank/public/Jupyter%20Help.ipynb#2.-Installing-extensions
__ https://bitbucket.org/ipre/calico/downloads/
