========================================
Configuring the Metering vSphere Drivers
========================================

This document is continually updated and reflects the latest available code.

Service overview
================

This module can be used by the `Watcher Metering`_ Agent to periodically
collect metrics from a vSphere datacenter.


Activate a vSphere driver
=========================

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

After updating the configuration file, you have to restart the `Watcher Metering`_.

.. _`Watcher Metering`: https://github.com/b-com/watcher-metering/


vSphere Driver configuration
============================

Here is a list of vsphere drivers currently implemented in this project:

.. drivers-table::


Each driver can be also configurable by adding a dedicated section named
``[metrics_driver.driver_name]`` in a configuration file loaded by the Watcher
Metering Agent. Such a file is self documented, so you will find in it all
driver configuration documentation.

You will find a sample by editing the file ``etc/watcher-metering-vsphere/watcher-metering-vsphere.conf.sample``

Once the configuration has been made, you can run the agent. To do so, you can
use the following command:

.. code-block:: shell

    $ watcher-metering-agent \
        --config-file=/etc/watcher-metering/agent.conf
        --config-file=/etc/watcher-metering/watcher-metering-vsphere.conf
