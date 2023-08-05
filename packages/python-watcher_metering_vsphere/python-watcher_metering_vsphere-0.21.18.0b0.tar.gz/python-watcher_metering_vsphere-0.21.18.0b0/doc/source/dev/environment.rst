..

===========================================
Setting up a Driver development environment
===========================================

Prerequisites
=============

This document assumes you are using Ubuntu or Fedora, and that you have the following tools available on your system:

- Python_ 2.7 and 3.4
- git_
- setuptools_
- pip_
- msgfmt (part of the gettext package)
- virtualenv and virtualenvwrapper_

**Reminder**: If you're successfully using a different platform, or a
different version of the above, please document your configuration here!

.. _Python: http://www.python.org/
.. _git: http://git-scm.com/
.. _setuptools: http://pypi.python.org/pypi/setuptools
.. _virtualenvwrapper: https://virtualenvwrapper.readthedocs.org/en/latest/install.html

Getting the latest code
=======================

Make a clone of the code from our `Git repository`:

.. code-block:: bash

    $ git clone ssh://gitolite@forge.b-com.com/indeed-ccl/WATCHER/watcher-metering-vsphere.git

When that is complete, you can:

.. code-block:: bash

    $ cd watcher-metering-vsphere

Installing dependencies
=======================

Watcher maintains two lists of dependencies::

    requirements.txt
    test-requirements.txt

The first is the list of dependencies needed for running Watcher, the second list includes dependencies used for active development and testing of Watcher itself.

These dependencies can be installed from PyPi_ using the Python tool pip_.

.. _PyPi: http://pypi.python.org/
.. _pip: http://pypi.python.org/pypi/pip

However, your system *may* need additional dependencies that `pip` (and by
extension, PyPi) cannot satisfy. These dependencies should be installed
prior to using `pip`, and the installation method may vary depending on
your platform.

* Ubuntu 14.04:

  .. code-block:: bash

      $ sudo apt-get install python-dev libxml2-dev libxslt-dev

* Fedora 19+:

  .. code-block:: bash

      $ sudo yum install python-devel libxml-devel libxslt-devel


PyPi Packages and VirtualEnv
----------------------------

We recommend establishing a virtualenv to run Watcher within. virtualenv
limits the Python environment to just what you're installing as dependencies,
useful to keep a clean environment for working on Watcher.

.. code-block:: bash

    $ mkvirtualenv vsphere
    $ git clone ssh://gitolite@forge.b-com.com/indeed-ccl/WATCHER/watcher-metering-vsphere.git

    # Use 'python setup.py' to link Watcher into Python's site-packages
    $ cd watcher-metering-vsphere && python setup.py install

    # Install the dependencies for running Watcher
    $ pip install -r ./requirements.txt

    # Install the dependencies for developing, testing, and running Watcher
    $ pip install -r ./test-requirements.txt

This will create a local virtual environment in the directory ``$WORKON_HOME``.
The virtual environment can be disabled using the command:

.. code-block:: bash

    $ deactivate

You can re-activate this virtualenv for your current shell using:

.. code-block:: bash

    $ workon vsphere

For more information on virtual environments, see virtualenv_.

.. _virtualenv: http://www.virtualenv.org/


Run unit tests
==============
All unit tests should be run using tox. To run the unit tests under py27 and also run the pep8 tests:

.. code-block:: bash

    $ workon vsphere
    (watcher) $ pip install tox

    (watcher) $ cd watcher-metering-vsphere
    (watcher) $ tox -epep8 -epy27

When you're done, deactivate the virtualenv:

.. code-block:: bash

    $ deactivate

Build the Watcher documentation
===============================
you can easily build the HTML documentation from ``doc/source`` files, by using tox:

.. code-block:: bash

    $ workon vsphere

    (watcher) $ cd watcher-metering-vsphere
    (watcher) $ tox -edocs

The HTML files are available into ``doc/build`` directory.


Configure the drivers
=====================
Watcher modules requires a configuration file. There is a sample configuration file that can be used to get started:

.. code-block:: bash

  $ cp etc/watcher-metering/watcher-metering-vsphere.conf.sample /etc/watcher-metering/vsphere.conf

The defaults are enough to get you going, but you can make any changes if needed.


Activate the  Drivers
=====================
To run your vSphere driver, you have to use a `Watcher Metering`_ Agent:

.. code-block:: bash

    $ workon vsphere

    (watcher) $ $ watcher-metering-agent \
        --config-file=/etc/watcher-metering/agent.conf
        --config-file=/etc/watcher-metering/vsphere.conf


.. _`Watcher Metering`: https://github.com/b-com/watcher-metering
