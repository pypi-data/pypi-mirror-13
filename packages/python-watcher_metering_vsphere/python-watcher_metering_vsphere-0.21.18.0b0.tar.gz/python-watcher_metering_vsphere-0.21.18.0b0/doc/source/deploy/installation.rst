..

=======================================
Installing the vSphere metering drivers
=======================================

This document describes how to install Watcher Metering Drivers for vSphere in order
to use it. If you are intending to develop on or with Watcher, please read :doc:`../dev/environment`.

Prerequisites
-------------

The source install instructions specifically avoid using platform specific
packages, instead using the source for the code and the Python Package Index
(PyPi_).

.. _PyPi: http://pypi.python.org/pypi

It's expected that your system already has python2.7_, latest version of pip_, and git_ available.

.. _python2.7: http://www.python.org
.. _pip: http://www.pip-installer.org/en/latest/installing.html
.. _git: http://git-scm.com/

Your system shall also have some additional system libraries:

  On Ubuntu (tested on 14.04LTS):

  .. code-block:: bash

    $ sudo apt-get install python-dev libxml2-dev libxslt-dev

  On Fedora-based distributions e.g., Fedora/RHEL/CentOS/Scientific Linux (tested on CentOS 7.1):

  .. code-block:: bash

    $ sudo yum install gcc python-devel libxml-devel libxslt-devel


Installing from Source
----------------------

Clone the module repository:

.. code-block:: bash

    $ git clone ssh://gitolite@forge.b-com.com/indeed-ccl/WATCHER/watcher-metering-vsphere.git
    $ cd watcher-metering-vsphere

Install the Watcher modules:

.. code-block:: bash

    # python setup.py install


You will find sample configuration file in ``etc/watcher-metering``:

* ``watcher-metering-vsphere.conf.sample``

Install the Watcher modules dependencies:

.. code-block:: bash

    # pip install -r requirements.txt

From here, refer to :doc:`configuration` to declare such drivers as a new ones into `Watcher Metering Agent`_ and to configure it. Once configured, you should be able to run again the Watcher Metering Agent by issuing these commands:

.. code-block:: bash

    $ watcher-metering-agent \
        --config-file=/etc/watcher-metering/agent.conf
        --config-file=/etc/watcher-metering/watcher-metering-vsphere.conf

By default, this will show logging on the console from which it was started.


.. _`Watcher Metering Agent`: https://github.com/b-com/watcher-metering

Installing from packages: PyPI
--------------------------------

Watcher package is available on PyPI repository. To install Watcher on your system:

.. code-block:: bash

    $ pip install python-watcher_metering_drivers

The driver and its dependencies will be automatically installed on your system.

Once installed, you still need to declare such drivers as a new ones into `Watcher Metering Agent`_ and to configure it, which you can find described in :doc:`configuration`.
