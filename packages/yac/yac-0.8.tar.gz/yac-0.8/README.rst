=======================
yac - portable services
=======================

A service, running on your VPC, from nothing to ka-ching, in a few minutes.

-  Have access to an AWS VPC?
-  Want to run a service on your VPC using Docker containers?
-  Have a few spare minutes?

Quick Start
-----------

Install the cli:

.. code-block:: sh

    $ pip install yac

Find a service:

.. code-block:: sh

    $ yac service --find=confluence

Print a service:

.. code-block:: sh

    $ yac stack intranet atlassian/confluence:latest

What is yac?
------------

    *  A workflow system that does for services what docker did for
   applications
        *  docker helped make it easy to find, run, define, and share individual
   applications
        *  yac does the same for services
    *  A cli app that lets you easily find, run, define, and share web
   service templates
        *  yac registry works just like the docker registry
        *  services are defined as templates in json
        *  services templates can be browsed, instantiated, registered, and
   cloned via the yac registry
    *  A happy place for service developers, cloud administrators, and service providers

What is a service?
------------------

*  An application that provides some useful function
*  An application that can be implemented using one of more Docker
   containers

Intruiged?
==========

Read more at `yac stacks`_ on atlassian.net.

.. _yac stacks: https://yac-stacks.atlassian.net/wiki/display/YAC/Your+Automated+Cloud


Want to contribute?
===================

Repo
----

clone from `yac on bitbucket`

.. _ yac on bitbucket: https://bitbucket.org/thomas_b_jackson/yac

Testing
-------

Get unit tests to pass

.. code-block:: sh

    python -m unittest discover yac/tests
