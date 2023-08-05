| |Build Status|
| |Coverage Status|
| |Scrutinizer Code Quality|
| |PyPI Version|
| |PyPI Downloads|

Getting Started
===============

Git Dependency Manager (``gdm``) is a language-agnostic "dependency
manager" using Git. It aims to serve as a submodules replacement and
provides advanced options for managing versions of nested Git
repositories.

Requirements
------------

-  Python 3.4+
-  Latest version of Git (with `stored
   credentials <http://stackoverflow.com/questions/7773181>`__)
-  OSX/Linux (with a decent shell for Git)

Installation
------------

``gdm`` can be installed with pip:

.. code:: sh

    $ pip install gdm

or directly from the source code:

.. code:: sh

    $ git clone https://github.com/jacebrowning/gdm.git
    $ cd gdm
    $ python setup.py install

Setup
-----

Create a configuration file (``gdm.yml`` or ``.gdm.yml``) in the root of
your working tree:

.. code:: yaml

    location: .gdm
    sources:
    - repo: https://github.com/kstenerud/iOS-Universal-Framework
      dir: framework
      rev: Mk5-end-of-life
    - repo: https://github.com/jonreid/XcodeCoverage
      dir: coverage
      rev: master
      link: Tools/XcodeCoverage

Ignore the dependency storage location:

.. code:: sh

    $ echo .gdm >> .gitignore

Basic Usage
===========

See the available commands:

.. code:: sh

    $ gdm --help

Updating Dependencies
---------------------

Get the latest versions of all dependencies:

.. code:: sh

    $ gdm update

which will essentially:

#. create a working tree at *root*/``location``/``dir``
#. fetch from ``repo`` and checkout the specified ``rev``
#. symbolically link each ``location``/``dir`` from *root*/``link`` (if
   specified)
#. repeat for all nested working trees containing a configuration file
#. record the actual commit SHAs that were checked out (with ``--lock``
   option)

where ``rev`` can be:

-  all or part of a commit SHA: ``123def``
-  a tag: ``v1.0``
-  a branch: ``master``
-  a ``rev-parse`` date: ``'develop@{2015-06-18 10:30:59}'``

Restoring Previous Versions
---------------------------

Display the specific revisions that are currently installed:

.. code:: sh

    $ gdm list

Reinstall these specific versions at a later time:

.. code:: sh

    $ gdm install

Deleting Dependencies
---------------------

Remove all installed dependencies:

.. code:: sh

    $ gdm uninstall

Advanced Options
================

See the full documentation at
`git-dependency-manager.info <http://git-dependency-manager.info/interfaces/cli/>`__.

.. |Build Status| image:: https://travis-ci.org/jacebrowning/gdm.svg?branch=develop
   :target: https://travis-ci.org/jacebrowning/gdm
.. |Coverage Status| image:: http://img.shields.io/coveralls/jacebrowning/gdm/master.svg
   :target: https://coveralls.io/r/jacebrowning/gdm
.. |Scrutinizer Code Quality| image:: http://img.shields.io/scrutinizer/g/jacebrowning/gdm.svg
   :target: https://scrutinizer-ci.com/g/jacebrowning/gdm/?branch=master
.. |PyPI Version| image:: http://img.shields.io/pypi/v/GDM.svg
   :target: https://pypi.python.org/pypi/GDM
.. |PyPI Downloads| image:: http://img.shields.io/pypi/dm/GDM.svg
   :target: https://pypi.python.org/pypi/GDM
