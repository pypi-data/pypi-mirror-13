*****************************
birdhousebuilder.recipe.solr
*****************************

.. contents::

Introduction
************

``birdhousebuilder.recipe.solr`` is a `Buildout`_ recipe to install and configure `Solr`_ with `Anaconda`_. ``Solr`` will be deployed as a `Supervisor`_ service.
 
This recipe is used by the `Birdhouse`_ project. 

.. _`Buildout`: http://buildout.org/
.. _`Anaconda`: http://continuum.io/
.. _`Supervisor`: http://supervisord.org/
.. _`Solr`: https://lucene.apache.org/solr/
.. _`Birdhouse`: http://bird-house.github.io/


Usage
*****

The recipe requires that Anaconda is already installed. It assumes that the default Anaconda location is in your home directory ``~/anaconda``. Otherwise you need to set the ``ANACONDA_HOME`` environment variable or the Buildout option ``anaconda-home``.

It installs the ``solr`` package from a conda channel in a conda environment named ``birdhouse``. The location of the birdhouse environment is ``.conda/envs/birdhouse``. It deploys a `Supervisor`_ configuration for ``Solr`` in ``~/.conda/envs/birdhouse/etc/supervisor/conf.d/solr.conf``. Supervisor can be started with ``~/.conda/envs/birdhouse/etc/init.d/supervisor start``.

By default ``Solr`` will be available on http://localhost:8983/solr.

The recipe depends on ``birdhousebuilder.recipe.conda`` and ``birdhousebuilder.recipe.supervisor``.

Supported options
=================

The recipe supports the following options:

``anaconda-home``
   Buildout option with the root folder of the Anaconda installation. Default: ``$HOME/anaconda``.
   The default location can also be set with the environment variable ``ANACONDA_HOME``. Example::

     export ANACONDA_HOME=/opt/anaconda

   Search priority is:

   1. ``anaconda-home`` in ``buildout.cfg``
   2. ``$ANACONDA_HOME``
   3. ``$HOME/anaconda``

``hostname``
   The hostname of the ``Solr`` service (nginx). Default: ``localhost``

``http_port``
   The http port of the ``Solr`` service (nginx). Default: ``8983``



Example usage
=============

The following example ``buildout.cfg`` installs ``Solr`` with Anaconda::

  [buildout]
  parts = solr

  anaconda-home = /home/myself/anaconda

  [solr]
  recipe = birdhousebuilder.recipe.solr
  hostname = localhost
  http-port = 8983

After installing with Buildout start the ``Solr`` service with::

  $ cd /home/myself/.conda/envs/birdhouse
  $ etc/init.d/supervisord start  # start|stop|restart
  $ bin/supervisorctl status      # check that pycsw is running

Open your browser with the following URL:: 

  http://localhost:8983/solr





