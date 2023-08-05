=========================
Watcher Metering Grid5000
=========================

Introduction
============

Watcher Metering Grid5000 provides a set of metric-pulling drivers extending the
`Watcher Metering`_ project which is used to collect system metrics from the
Grid5000 datacenters (see http://api.grid5000.fr) before publishing them to a given store.

To sum up, Watcher Metering service is composed by 2 modules:

- The ``Agent`` who collects the desired metrics and sends it to a publisher.
- The ``Publisher`` who gathers measurements from one or more agent and pushes
  them to the desired store.

Drivers easily extend metrics collecting features of Agent (we use `stevedore`_ library for managing plugins).

This project is part of the Watcher_ project.

.. _Watcher Metering: https://github.com/b-com/watcher-metering
.. _Watcher: https://wiki.openstack.org/wiki/Watcher
.. _stevedore: http://git.openstack.org/cgit/openstack/stevedore

Getting started
===============

Installation: :doc:./doc/source/deploy/installation.rst
