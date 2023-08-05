TUNE SDK for Python documentation
===========================================

    :package: `tune-reporting-python <https://github.com/MobileAppTracking/tune-reporting-python>`_
    :label: TUNE SDK for Python 2.7 and 3.0
    :purpose: Incorporate TUNE services.
    :update:  $Date: 2015-12-11 20:56:46 $
    :version: 1.0.9

Overview
####################

Python helper library for TUNE services.

The utility focus of this SDK is upon the Advertiser Reporting endpoints.

The second goal of the SDKs is to assure that our customers’ developers are using best practices in gathering reports in the most optimal way.

Please see documentation here: `TUNE SDKs <https://developers.mobileapptracking.com/tune-api-sdks>`_

Requirements
####################

Prerequisites
********************

    * Python 2.7 or Python 3.0

Generate API Key
********************

To use SDK, it requires you to `Generate API Key <http://developers.mobileapptracking.com/generate-api-key/>`_

Installation
####################

You can install `tune-reporting-python` via PyPi or by installing from source.

Via PyPi using pip:
********************

*tune_reporting* module is in *PyPi*: `link <https://pypi.python.org/pypi/tune_reporting/>`_

Install from PyPi using package manager for Python: `pip <http://www.pip-installer.org/en/latest/>`_

.. code-block:: bash
    :linenos:

    pip install --upgrade tune-reporting

You may need to run the above commands with *sudo*.

Don't have pip installed? Try installing it, by running this from the command
line:

.. code-block:: bash
    :linenos:

    curl https://raw.github.com/pypa/pip/master/contrib/get-pip.py | python

Via ZIP file:
********************

you can download the source code: `ZIP <https://github.com/MobileAppTracking/tune-reporting-python/zipball/master>`_.

.. code-block:: bash
    :linenos:

    python setup.py install

You may need to run the above commands with `sudo`.

Code Samples
####################

SDK Examples
********************

Run the following script to view execution of all examples:

.. code-block:: bash
    :linenos:

    make installs
    make API_KEY=[API_KEY] examples

SDK Unittests
********************

Run the following script to view execution of all unittests:

.. code-block:: bash
    :linenos:

    make tests-installs
    make API_KEY=[API_KEY] tests

SDK Documentation -- Sphinx
****************************

The following will generate `Sphinx <http://en.wikipedia.org/wiki/Sphinx_(documentation_generator)>`_ documentation from Python codebase:

.. code-block:: bash
    :linenos:

    make tests-installs
    make docs-sphinx

SDK Documentation -- Doxygen
****************************

The following will generate `Doxygen <http://en.wikipedia.org/wiki/Doxygen>`_ documentation from Python codebase:

.. code-block:: bash
    :linenos:

    make tests-installs
    make docs-doxygen

Requires installation of `Doxygen <http://www.stack.nl/~dimitri/doxygen/index.html>`_.

License
####################

`MIT License <http://opensource.org/licenses/MIT>`_.

Reporting Issues
####################

We would love to hear your feedback.

Report issues using the `Github Issue Tracker  <https://github.com/MobileAppTracking/tune-reporting-python/issues>`_.


or Email: `sdk@tune.com <mailto:sdk@tune.com>`_
