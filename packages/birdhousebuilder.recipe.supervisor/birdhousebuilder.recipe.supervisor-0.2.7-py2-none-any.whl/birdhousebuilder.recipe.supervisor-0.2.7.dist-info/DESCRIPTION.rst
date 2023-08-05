**********************************
birdhousebuilder.recipe.supervisor
**********************************

.. contents::

Introduction
************

``birdhousebuilder.recipe.supervisor`` is a `Buildout`_ recipe to configure `Supervisor`_ services with `Anaconda`_.
This recipe is used by the `Birdhouse`_ project. 

.. _`Buildout`: http://buildout.org/
.. _`Anaconda`: http://continuum.io/
.. _`Supervisor`: http://supervisord.org/
.. _`Birdhouse`: http://bird-house.github.io/


Usage
*****

The recipe requires that Anaconda is already installed. It assumes that the default Anaconda location is in your home directory ``~/anaconda``. Otherwise you need to set the ``ANACONDA_HOME`` environment variable or the Buildout option ``anaconda-home``.

The recipe will install the ``supervisor`` package from a conda channel in a conda environment named ``birdhouse``. The location of the birdhouse environment is ``.conda/envs/birdhouse``. It deploys a supervisor configuration of a given service. The configuration will be deployed in the birdhouse enviroment ``~/.conda/envs/birdhouse/etc/supervisor/conf.d/myapp.conf``. Supervisor can be started with ``~/.conda/envs/birdhouse/etc/init.d/supervisord start``.

The recipe depends on ``birdhousebuilder.recipe.conda``.

Supported options
=================

This recipe supports the following options:

**anaconda-home**
   Buildout option with the root folder of the Anaconda installation. Default: ``$HOME/anaconda``.
   The default location can also be set with the environment variable ``ANACONDA_HOME``. Example::

     export ANACONDA_HOME=/opt/anaconda

   Search priority is:

   1. ``anaconda-home`` in ``buildout.cfg``
   2. ``$ANACONDA_HOME``
   3. ``$HOME/anaconda``

Buildout options for ``supervisord``:

**supervisor-port**
   Buildout option to set the supervisor port. Default is 9001.

**supervisor-host**
   Buildout option to set supervisor host. Default is 127.0.0.1.

**supervisor-username**
   Buildout option to set username for http monitor access. Default: None

**supervisor-password**
   Buildout option to set password for http monitor access. Default: None

**supervisor-use-monitor**
   Buildout option wheather to enable http monitor interface. Default: true

**supervisor-loglevel**
   Buildout option for supervisor log level. Default: info

Buildout part options for the program section:

**program**
   The name of the supervisor service.

**command**
   The command to start the service.

**directory**
   The directory where the command is started.

**priority**
   The priority to start service (optional). Default is 999.

**autostart**
    Start service automatically (optional). Default is ``true``.

**autorestart**
    Restart service automatically (optional). Default is ``false``.

**stdout_logfile**
    logfile for stdout (optional). Default is ``~/.conda/envs/birdhouse/var/log/supervisor/${program}.log``

**stderr_logfile**
    logfile for stderr (optional). Default is ``~/.conda/envs/birdhouse/var/log/supervisor/${program}.log``

**startsecs**
    Seconds the service needs to be online before marked as ``started`` (optional). Default is 1.

**stopwaitsecs**
    Seconds to wait before killing service (optional). Default 10.

**killasgroup**
    Kill also child processes (optional). Default ``false``.

.. note::

   The ``DAEMON_OPTS`` environment variable can be used to set additional start parameters for supervisord. 
   For example ``DAEMON_OPTS=-n`` to start supervisord in foreground.

Example usage
=============

The following example ``buildout.cfg`` installs a Supervisor configuration for ``myapp`` web application::

  [buildout]
  parts = myapp

  anaconda-home = /opt/anaconda
  supervisor-host = 127.0.0.1
  supervisor-port = 9001
  supervisor-use-monitor = true

  [myapp]
  recipe = birdhousebuilder.recipe.supervisor
  program = myapp
  command = ${buildout:bin-directory}/gunicorn -b unix:///tmp/myapp.socket myapp:app 
  directory = /tmp





Authors
*******

Carsten Ehbrecht ehbrecht at dkrz.de

Changes
*******

0.2.7 (2015-12-22)
==================

* cleaned up configuration files.
* added more supervisord options: host, port, username, password, use_monitor.

0.2.6 (2015-12-07)
==================

* remove supervisor config files after uninstall.

0.2.5 (2015-09-21)
==================

* added DAEMON_OPTS env variable to set additional parameters when starting supervisord.

0.2.4 (2015-07-15)
==================

* added ``stopsignal`` option.
* fixed ``stopasgroup`` option.

0.2.2 (2015-06-25)
==================

* cleaned up templates.
* added user and chown option.

0.2.1 (2015-05-18)
==================

* added more options for program configuration.
* setting default logfile name for service.

0.2.0 (2015-02-24)
==================

* installing in conda enviroment ``birdhouse``.
* using ``$ANACONDA_HOME`` environment variable.
* separation of anaconda-home and installation prefix.

0.1.5 (2015-01-22)
==================

* bugfix: var/log/supervisor directory is now created.

0.1.4 (2014-12-06)
==================

* Don't update conda on buildout update.

0.1.3 (2014-07-31)
==================

* Updated documentation.

0.1.2 (2014-07-24)
==================

* Removed workaround "kill nginx".

0.1.1 (2014-07-22)
==================

* Not using supervisor-host option.

0.1.0 (2014-07-10)
==================

* Initial Release.


