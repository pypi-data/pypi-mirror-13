[![Build Status](https://travis-ci.org/jacebrowning/gdm.svg?branch=develop)](https://travis-ci.org/jacebrowning/gdm)
[![Coverage Status](http://img.shields.io/coveralls/jacebrowning/gdm/master.svg)](https://coveralls.io/r/jacebrowning/gdm)
[![Scrutinizer Code Quality](http://img.shields.io/scrutinizer/g/jacebrowning/gdm.svg)](https://scrutinizer-ci.com/g/jacebrowning/gdm/?branch=master)
[![PyPI Version](http://img.shields.io/pypi/v/GDM.svg)](https://pypi.python.org/pypi/GDM)
[![PyPI Downloads](http://img.shields.io/pypi/dm/GDM.svg)](https://pypi.python.org/pypi/GDM)

Getting Started
===============

Git Dependency Manager (`gdm`) is a language-agnostic "dependency manager" using Git. It aims to serve as a submodules replacement and provides advanced options for managing versions of nested Git repositories.

Requirements
------------

* Python 3.4+
* Latest version of Git (with [stored credentials](http://stackoverflow.com/questions/7773181))
* OSX/Linux (with a decent shell for Git)

Installation
------------

`gdm` can be installed with pip:

```sh
$ pip install gdm
```

or directly from the source code:

```sh
$ git clone https://github.com/jacebrowning/gdm.git
$ cd gdm
$ python setup.py install
```

Setup
-----

Create a configuration file (`gdm.yml` or `.gdm.yml`) in the root of your working tree:

```yaml
location: .gdm
sources:
- repo: https://github.com/kstenerud/iOS-Universal-Framework
  dir: framework
  rev: Mk5-end-of-life
- repo: https://github.com/jonreid/XcodeCoverage
  dir: coverage
  rev: master
  link: Tools/XcodeCoverage
```

Ignore the dependency storage location:

```sh
$ echo .gdm >> .gitignore
```

Basic Usage
===========

See the available commands:

```sh
$ gdm --help
```

Updating Dependencies
---------------------

Get the latest versions of all dependencies:

```sh
$ gdm update
```

which will essentially:

1. create a working tree at _root_/`location`/`dir`
2. fetch from `repo` and checkout the specified `rev`
3. symbolically link each `location`/`dir` from _root_/`link` (if specified)
4. repeat for all nested working trees containing a configuration file
5. record the actual commit SHAs that were checked out (with `--lock` option)

where `rev` can be:

* all or part of a commit SHA: `123def`
* a tag: `v1.0`
* a branch: `master`
* a `rev-parse` date: `'develop@{2015-06-18 10:30:59}'`

Restoring Previous Versions
---------------------------

Display the specific revisions that are currently installed:

```sh
$ gdm list
```

Reinstall these specific versions at a later time:

```sh
$ gdm install
```

Deleting Dependencies
---------------------

Remove all installed dependencies:

```sh
$ gdm uninstall
```

Advanced Options
================

See the full documentation at [git-dependency-manager.info](http://git-dependency-manager.info/interfaces/cli/).
