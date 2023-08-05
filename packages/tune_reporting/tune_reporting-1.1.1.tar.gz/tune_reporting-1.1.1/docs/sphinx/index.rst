.. tune_api_python documentation master file, created by
   sphinx-quickstart on Sat Nov  1 08:46:22 2014.
   You can adapt this file completely to your liking, but it should at least
   contain the root `toctree` directive.

Tune Reporting API SDK for Python documentation
===========================================

    :package: `tune-reporting-python <https://github.com/MobileAppTracking/tune-reporting-python>`_
    :label: Tune Reporting API SDK for Python 2.7 and 3.0
    :purpose: Incorporate Tune Reporting API services.
    :update:  $Date: 2015-07-30 12:49:27 $
    :version: 1.0.6

-------------------
Contents:
-------------------

.. toctree::
   :maxdepth: 2

Indices and tables
####################

* :ref:`genindex`
* :ref:`modindex`
* :ref:`search`

Overview
####################

The utility focus of the SDKs is upon the Advertiser Reporting endpoints.

Even though the the breadth of the Management API goes beyond just reports, it is these endpoints that our customers primarily access.

The second goal of the SDKs is to assure that our customers’ developers are using best practices in gathering reports in the most optimal way.

Please see documentation here: `Tune Reporting API SDKs <https://developers.mobileapptracking.com/tune-api-sdks>`_

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

Install from PyPi using package manager for Python: `pip <http://www.pip-installer.org/en/latest/>`_

.. code-block:: bash
    :linenos:

    $ pip install tune_reporting


Don't have pip installed? Try installing it, by running this from the command
line:

.. code-block:: bash
    :linenos:

    $ curl https://raw.github.com/pypa/pip/master/contrib/get-pip.py | python

Via ZIP file:
********************

you can download the source code: `ZIP <https://github.com/MobileAppTracking/tune-reporting-python/zipball/master>`_.

.. code-block:: bash
    :linenos:

    $ python setup.py install

You may need to run the above commands with `sudo`.

Code Samples
####################

SDK Examples
********************

Run the following script to view execution of all examples:

.. code-block:: bash
    :linenos:

    $ make installs
    $ make api_key=[API_KEY] examples

SDK Unittests
********************

Run the following script to view execution of all unittests:

.. code-block:: bash
    :linenos:

    $ make tests-installs
    $ make api_key=[API_KEY] tests

SDK Document
********************

Run the following script to generate Doxygen-based documentation:

.. code-block:: bash
    :linenos:

    $ make docs

Requires installation of `Doxygen <http://www.stack.nl/~dimitri/doxygen/index.html>`_.

License
####################

`MIT License <http://opensource.org/licenses/MIT>`_.

Reporting Issues
####################

We would love to hear your feedback.

Report issues using the `Github Issue Tracker  <https://github.com/MobileAppTracking/tune-reporting-python/issues>`_.


or Email: `sdk@tune.com <mailto:sdk@tune.com>`_
