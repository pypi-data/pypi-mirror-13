========================
Watcher Metering vSphere
========================

Introduction
============

Watcher Metering vSphere provides a set of metric-pulling drivers extending the
`Watcher Metering`_ project which is used to collect system metrics from a
`vSphere datacenter`_ before publishing them to a given store.

To sum up, Watcher Metering service is composed by 2 modules:

- The ``Agent`` who collects the desired metrics and sends it to a publisher.
- The ``Publisher`` who gathers measurements from one or more agent and pushes
  them to the desired store.

Drivers easily extend metrics collecting features of Agent (we use `stevedore`_ library for managing plugins).

This project is part of the Watcher_ project.

.. _Watcher Metering: https://github.com/b-com/watcher-metering
.. _Watcher: https://wiki.openstack.org/wiki/Watcher
.. _stevedore: http://git.openstack.org/cgit/openstack/stevedore
.. _vSphere datacenter: http://pubs.vmware.com/vsphere-60/index.jsp?topic=%2Fcom.vmware.wssdk.apiref.doc%2Fright-pane.html

Getting started
===============

System requirements
-------------------

Watcher Metering packages must be installed before installing the drivers.
Please follow the installation procedure of the `Watcher Metering`_ project first.

Installation
------------

To install this package, just use *pip*:

.. code-block:: shell

    # pip install python-watcher_metering_vsphere


Activate a driver
-----------------

Within your Watcher Metering Agent configuration file ``/etc/watcher-metering/watcher-metering-agent.conf``,
add the name of the driver entry point, in the ``[agent]`` section,  you wish to enable.

As an example, if you wish to acticate both the ``vsphere_mem_usage`` and the
``vsphere_cpu_usage`` drivers, just edit the aforementioned configuration file like
this:

.. code-block:: ini

     [agent]
     driver_names =
        vsphere_mem_usage,
        vsphere_cpu_usage

After updating the configuration file, you have to `restart the Watcher Metering Agent`_.

.. _restart the Watcher Metering Agent: https://github.com/b-com/watcher-metering/blob/master/doc/source/deploy/installation.rst#command

Driver configuration
====================

To find out about the available drivers, please refer to the `vSphere drivers configuration`_ page

Each driver can be also configurable by adding a dedicated section named
``[metrics_driver.driver_name]`` in a configuration file loaded by the Watcher
Metering Agent. Such a file is self documented, so you will find in it all
driver configuration documentation.

You will find a sample by editing the file `etc/watcher-metering-vsphere/watcher-metering-vsphere.conf.sample`_

.. _vSphere drivers configuration: https://forge.b-com.com/www/indeed-ccl/doc/watcher-metering-vsphere/deploy/configuration.html
.. _etc/watcher-metering/watcher-metering-vsphere.conf.sample: etc/watcher-metering/watcher-metering-vsphere.conf.sample
