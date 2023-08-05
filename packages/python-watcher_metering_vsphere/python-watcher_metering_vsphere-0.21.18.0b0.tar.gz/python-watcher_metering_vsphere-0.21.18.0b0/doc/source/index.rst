===============================================================
Welcome to the Watcher Metering vSphere developer documentation
===============================================================

Introduction
============

Watcher Metering vSphere provides a set of metric-pulling drivers extending the
`Watcher Metering`_ project which is used to collect system metrics from a
`vSphere datacenter`_ before publishing them to a given store.

To do so, it is composed of two elements:

- The ``Agent`` who collects the desired metrics and sends it to a publisher.
  The ``Agent`` is meant to run on each monitored host (container, VM, ...)
- The ``Publisher`` who gathers measurements from one or more agent and pushes
  them to the desired store. The currently supported stores are Riemann
  (for CEP) and Ceilometer.

This package is part of the `Watcher Metering`_ project.

.. _python-watcher_metering: https://pypi.python.org/pypi/python-watcher_metering
.. _Watcher Metering: https://pypi.python.org/pypi/python-watcher_metering
.. _Watcher: http://factory.b-com.com/www/watcher/watcher/doc/build/html/
.. _wiki: https://wiki.openstack.org/wiki/Watcher
.. _vSphere datacenter: http://pubs.vmware.com/vsphere-60/index.jsp?topic=%2Fcom.vmware.wssdk.apiref.doc%2Fright-pane.html


Developer Guide
===============

API References
--------------

.. toctree::
    :maxdepth: 2

    api/reference


Admin Guide
===========

Installation
------------

.. toctree::
  :maxdepth: 1

  deploy/installation
  deploy/configuration


Indices and tables
==================

* :ref:`genindex`
* :ref:`modindex`
* :ref:`search`
