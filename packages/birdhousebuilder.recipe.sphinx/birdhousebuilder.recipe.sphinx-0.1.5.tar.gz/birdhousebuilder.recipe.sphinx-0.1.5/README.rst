******************************
birdhousebuilder.recipe.sphinx
******************************

.. image:: https://travis-ci.org/bird-house/birdhousebuilder.recipe.sphinx.svg?branch=master
   :target: https://travis-ci.org/bird-house/birdhousebuilder.recipe.sphinx
   :alt: Travis Build

.. contents::

Introduction
************

Buildout Recipe to setup Sphinx Documentation for `Birdhouse <http://bird-house.github.io/>`_ Components.

The recipe is based on https://pypi.python.org/pypi/collective.recipe.sphinxbuilder

Usage
*****

The recipe requires that Anaconda is already installed. It assumes that the default Anaconda location is in your home directory ``~/anaconda``. Otherwise you need to set the ``ANACONDA_HOME`` environment variable or the Buildout option `anaconda-home`.

The recipe builds an initial docs folder for Sphinx in `docs`. 
The recipe configures `sphinx-autoapi` to generate the api reference documetation from the source code. 

The recipe depends on ``birdhousebuilder.recipe.conda`` and ``zc.recipe.egg``

Supported Options
=================

The recipe supports the following options:

**project** (default: `MyBird`)
    Specify the project name.

**author** (default: `Birdhouse`)
    Specify the author of the project.

**version** (default: `0.1`)
    Specify the version of the project.

**use_autoapi** (default: `true`)
    Set to `fals` if you don't want to use the `sphinx-autoapi`.  
  
**src** (default: `.`)    
    Specify path to source folder which will be used by `sphinx-autoapi`.

Example Usage
=============

Set up the docs for the project `Emu`:

.. code-block:: ini

  [buildout]
  parts = sphinx

  anaconda-home = /home/myself/anaconda

  [sphinx]
  recipe = birdhousebuilder.recipe.sphinx
  project = Emu
  version = 0.2
  src = emu
    





