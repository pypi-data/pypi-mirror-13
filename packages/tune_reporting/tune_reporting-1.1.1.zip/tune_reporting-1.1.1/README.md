<h2>tune-reporting-python</h2>
<h2>TUNE Reporting SDK for Python 2.7 and 3.0</h2>
<h3>Incorporate TUNE Reporting services.</h3>
<h4>Update:  $Date: 2015-12-11 20:56:46 $</h4>
<h4>Version: 1.0.9</h4>
===

<a id="TOP"></a>
### Table of Contents

<ul>
    <li><a href="#sdk_overview">Overview</a>
        <ul>
            <li><a href="#sdk_overview_available">Available TUNE Reporting SDKs</a></li>
            <li><a href="#sdk_overview_mobile">TUNE SDKs for Mobile Apps</a></li>
            <li><a href="#sdk_overview_dev_community">Developers Community</a></li>
        </ul>
    </li>
    <li><a href="#sdk_install">SDK Installation</a>
        <ul>
            <li><a href="#sdk_install_prereq">Prerequisites</a>
                <ul>
                    <li><a href="#sdk_install_prereq_env">Environment</a></li>
                    <li><a href="#sdk_install_prereq_ini">python.ini</a></li>
                    <li><a href="#sdk_install_prereq_apikey">Environment</a></li>
                </ul>
            </li>
            <li><a href="#sdk_install_choices">Choices</a>
                <ul>
                    <li><a href="#sdk_install_method_pypi_pip">Composer</a></li>
                    <li><a href="#sdk_install_method_zip">ZIP</a></li>
                    <li><a href="#sdk_prerequisites_api_key">Environment</a></li>
                </ul>
            </li>
            <li><a href="#sdk_install_config">Configuration</a></li>
        </ul>
    </li>

    <li><a href="#sdk_code_samples">SDK Code Samples</a>
        <ul>
            <li><a href="#sdk_code_samples_examples">Examples</a></li>
            <li><a href="#sdk_code_samples_unittests">Unittests</a></li>
        </ul>
    </li>

    <li><a href="#sdk_gendoc">SDK Generated Documentation</a>
        <ul>
            <li><a href="#sdk_gendoc_doxygen">Doxygen</a></li>
            <li><a href="#sdk_gendoc_sphinx">Sphinx</a></li>
        </ul>
    </li>

    <li><a href="#sdk_advertiser_reporting_overview">Advertiser Reporting Overview</a>
    </li>

    <li><a href="#sdk_license">MIT License</a>
    </li>

    <li><a href="#sdk_issues">SDK Issues</a>
    </li>
</ul>

<p>
<a href="#TOP">
<img alt="Return to Top" src="https://raw.githubusercontent.com/MobileAppTracking/tune-reporting-python/master/docs/images/b_top.gif" border="0">
</a>
</p>

<!-- Overview -->

<a id="sdk_overview" name="sdk_overview"></a>
### Overview

The **TUNE Reporting SDKs** addressed in this posting are for creating hosted applications which require handling requests to **TUNE Reporting API services** with utility focus is upon Advertiser Reporting endpoints.

The second goal of the SDKs is to assure that our customers’ developers are using best practices in gathering reports in the most optimal way.

<a id="sdk_overview_available" name="sdk_overview_available"></a>
#### Available TUNE Reporting SDKs

Supported programming languages for TUNE Reporting SDKs are:

<ul>
    <li><b>PHP</b>: <a href="https://github.com/MobileAppTracking/tune-reporting-php" target="_blank">tune-reporting-php</a></li>
    <li><b>Python</b>: <a href="https://github.com/MobileAppTracking/tune-reporting-python" target="_blank">tune-reporting-python</a></li>
    <li><b>Java</b>: <a href="https://github.com/MobileAppTracking/tune-reporting-java" target="_blank">tune-reporting-java</a></li>
    <li><b>Node.js</b>: <a href="https://github.com/MobileAppTracking/tune-reporting-node" target="_blank">tune-reporting-node</a></li>
</ul>

<a id="sdk_overview_mobile" name="sdk_overview_mobile"></a>
#### TUNE SDKs for Mobile Apps

The **TUNE Reporting SDKs** should absolutely not be included within Mobile Apps.

All information pertaining to **TUNE SDKs for Mobile Apps** are found [here](http://developers.mobileapptracking.com/sdks/).

<a id="sdk_overview_dev_community" name="sdk_overview_dev_community"></a>
#### Developers Community

Developer Community portal for MobileAppTracking™ (MAT), the industry leader in mobile advertising attribution and analytics. From API documentation to best practices, get everything you need to be successful with MAT.

[https://developers.mobileapptracking.com](https://developers.mobileapptracking.com)

Full developer information on TUNE Reporting SDKs can be found here:

[https://developers.mobileapptracking.com/tune-reporting-sdks/](https://developers.mobileapptracking.com/tune-reporting-sdks/)

<p>
<a href="#TOP">
<img alt="Return to Top" src="https://raw.githubusercontent.com/MobileAppTracking/tune-reporting-python/master/docs/images/b_top.gif" border="0">
</a>
</p>

<!-- Installation -->

<a id="sdk_install" name="sdk_install"></a>
### SDK Installation

This section detail what is required to use this SDK and how to install it for usage.

<a id="sdk_install_prereq" name="sdk_install_prereq"></a>
#### Installation Prerequisites

<a id="sdk_install_prereq_env" name="sdk_install_prereq_env"></a>
##### Environment

These are the basic requirements to use this SDK:

    * Python 2.7 or Python 3.0

<a id="sdk_install_prereq_apikey" name="sdk_install_prereq_apikey"></a>
##### Generate API Key

To use SDK to access Advertiser Reporting endpoints of TUNE Reporting API, it requires a MobileAppTracking API Key: [Generate API Key](http://developers.mobileapptracking.com/generate-api-key/).

<a id="sdk_install_choices" name="sdk_install_choices"></a>
#### Installation Choices

You can install this either via **PyPi pip** or by downloading the **ZIP** source.

<a id="sdk_install_method_pypi_pip" name="sdk_install_method_pypi_pip"></a>
##### Via PyPi using pip:

*tune_reporting* module is in *PyPi*: [link](https://pypi.python.org/pypi/tune_reporting/)
PyPi registered package: [TUNE client library](https://pypi.python.org/pypi/tune/1.0.1)

Install from PyPi using [pip](http://www.pip-installer.org/en/latest/), a
package manager for Python.

```bash
    $ pip install --upgrade tune-reporting
```

You may need to run the above commands with `sudo`.

Don't have pip installed? Try installing it, by running this from the command
line:

```bash
    $ curl https://raw.github.com/pypa/pip/master/contrib/get-pip.py | python
```

<a id="sdk_install_method_zip" name="sdk_install_method_zip"></a>
##### Via ZIP file:

[Click here to download the source code
(.zip)](https://github.com/MobileAppTracking/tune-reporting-python/archive/master.zip) for `tune-reporting-python`.

```bash
    python setup.py install
```

You may need to run the above commands with `sudo`.

<a id="sdk_install_config" name="sdk_install_config"></a>
#### TUNE Reporting SDK Configuration

##### SDK Configuration file

In the root folder, the TUNE Reporting SDK configuration is set within file ```./config/tune_reporting_sdk.config```.

With generated API_KEY from TUNE MobileAppTracking Platform account, replace `API_KEY`.

```
[TUNE_REPORTING]
# TUNE MobileAppTracking Platform generated API Key. Replace UNDEFINED.
tune_reporting_auth_key_string=UNDEFINED
# TUNE Reporting Authentication Type: api_key OR session_token.
tune_reporting_auth_type_string=api_key
# Validate use TUNE Reporting API fields used within action parameters.
tune_reporting_validate_fields_boolean=false
# TUNE reporting export status sleep (seconds).
tune_reporting_export_status_sleep_seconds=10
# TUNE reporting export fetch timeout (seconds).
tune_reporting_export_status_timeout_seconds=240
# Verbose output for debugging purposes when fetching report download url.
tune_reporting_export_status_verbose_boolean=false
```

##### SDK Configuration class

The TUNE Reporting SDK reads configuration through class ```SdkConfig``` with the
provided path to SDK configuration file.

```python
    dirname = os.path.split(__file__)[0]
    dirname = os.path.dirname(dirname)
    filepath = os.path.join(dirname, "config", SdkConfig.SDK_CONFIG_FILENAME)

    abspath = os.path.abspath(filepath)

    sdk_config = SdkConfig(filepath=abspath)
```

By default, configuration is assumed using ```api_key``` authentication type.

To override 'api_key' authentication type, then use ```SdkConfig::setApiKey()```:

```python
    sdk_config->set_api_key(api_key);
```

To override authentication type using ```session_token```, then use ```SdkConfig::setSessionToken()```:

```python
    sdk_config->set_session_token(session_token);
```

If you wish to generate your own session_token, class ```SessionAuthentication``` is provided:

```python
    session_authenticate = SessionAuthenticate()
    response = session_authenticate.api_key(api_key)
    session_token = response.data
```

and you're good to go!

<p>
<a href="#TOP">
<img alt="Return to Top" src="https://raw.githubusercontent.com/MobileAppTracking/tune-reporting-python/master/docs/images/b_top.gif" border="0">
</a>
</p>

<!-- SDK Code Samples -->

<a id="sdk_code_samples" name="sdk_code_samples"></a>
### SDK Code Samples

<a id="sdk_code_samples_examples" name="sdk_code_samples_examples"></a>
#### Examples

Run the following script to view execution of all examples:

```bash
    make examples api_key=[API_KEY]
```

<a id="sdk_code_samples_unittests" name="sdk_code_samples_unittests"></a>
#### Unittests

Run the following script to view execution of all unittests:

```bash
    make tests api_key=[API_KEY]
```

<!-- Generated Documentation -->

<a id="sdk_gendoc" name="sdk_gendoc"></a>
### SDK Generated Documentation

SDK code is well commented and to see full documentation of its source using the provided Makefile commands that initiate code documentation generators.

<a id="sdk_gendoc_doxygen" name="sdk_gen_doc_doxygen"></a>
#### Doxygen

The following will generate <a href="http://en.wikipedia.org/wiki/Doxygen" title="Doxygen" target="_blank">Doxygen</a> from Python codebase:

This code documentation generation requires installation of [Doxygen](http://www.stack.nl/~dimitri/doxygen/index.html).

```bash
    make docs-doxygen
```

<a id="sdk_gendoc_sphinx" name="sdk_gen_doc_pythondoc"></a>
#### Sphinx

Run the following script to generate [Sphnix]("http://en.wikipedia.org/wiki/Sphinx_(documentation_generator)") documentation from Python codebase:

This code documentation generation requires installation of [Sphinx](http://sphinx-doc.org/).

```bash
    make docs-sphinx
```

<p>
<a href="#TOP">
<img alt="Return to Top" src="https://raw.githubusercontent.com/MobileAppTracking/tune-reporting-python/master/docs/images/b_top.gif" border="0">
</a>
</p>

<p>&nbsp;</p>
<a id="sdk_advertiser_reporting_overview" name="sdk_advertiser_reporting_overview"></a>
### Advertiser Reporting Overview

The utility focus of the SDKs is upon the <a href="/advertiser-reporting-endpoints/">Advertiser Reporting endpoints</a>. The second goal of the SDKs is to assure that our customers' developers are using best practices in gathering reports in the most optimal way.

The endpoints interfaced by TUNE API SDKs provide access in gathering four types of reports:

<dl>
<dt>Log Reports</dt>
<dd>
Log reports provide measurement records for each Click, Install, Event, Event Item and Postback. Instead of being aggregated, the data is on a per transaction / request basis. MobileAppTracking&trade; (MAT) uses these logs to generate the aggregated data for the Actuals and Cohort reports. Note that we don’t provide Log reports for Impressions and Opens currently.

Advertiser Reporting classes that perform Log Reports are:
<ul>
    <li><code>AdvertiserReportLogClicks</code>: <a href="http://developers.mobileapptracking.com/management-api/explorer/root/endpoint/#/advertiser__stats__clicks/">/advertiser/stats/clicks/</a></li>
    <li><code>AdvertiserReportLogEventItems</code>:<a href="http://developers.mobileapptracking.com/management-api/explorer/root/endpoint/#/advertiser__stats__event__items/">/advertiser/stats/event/items/</a></li>
    <li><code>AdvertiserReportLogEvents</code>:<a href="http://developers.mobileapptracking.com/management-api/explorer/root/endpoint/#/advertiser__stats__events/">/advertiser/stats/events/</a></li>
    <li><code>AdvertiserReportLogInstalls</code>:<a href="http://developers.mobileapptracking.com/management-api/explorer/root/endpoint/#/advertiser__stats__installs/">/advertiser/stats/installs/</a></li>
    <li><code>AdvertiserReportLogPostbacks</code>:<a href="http://developers.mobileapptracking.com/management-api/explorer/root/endpoint/#/advertiser__stats__postbacks/">/advertiser/stats/postbacks/</a></li>
</ul>

</dd>
<dt>Actuals Report</dt>
<dd>
The Actuals report gives you quick insight into the performance of your apps and advertising partners (publishers). Use this report for reconciliation, testing, debugging, and ensuring that all measurement and attribution continues to operate smoothly. MAT generates this report by aggregating all the logs of each request (MAT updates the report every 5 minutes).

Actuals report endpoint include: <a href="http://developers.mobileapptracking.com/management-api/explorer/root/endpoint/#/advertiser__stats/">/advertiser/stats/</a>: Reports' class <a href="#sdk-advertiser-report-actuals"><code>AdvertiserReportActuals</code></a>

Advertiser Reporting class that perform Actuals Reports is:
<ul>
    <li><code>AdvertiserReportActuals</code>: <a href="http://developers.mobileapptracking.com/management-api/explorer/root/endpoint/#/advertiser__stats/">/advertiser/stats/</a></li>
</ul>
</dd>
<dt>Cohort Report</dt>
<dd>
The Cohort report analyzes user behavior back to click date time (Cohort by Click) or to install date time (Cohort by Install). Depending on whether you view the results based on click or install, the data in the report is vastly different.

Advertiser Reporting class that perform Cohort Reports is:
<ul>
    <li><code>AdvertiserReportCohortValue</code>: <a href="http://developers.mobileapptracking.com/management-api/explorer/root/endpoint/#/advertiser__stats__ltv">/advertiser/stats/ltv</a></li>
</ul>
</dd>
<dt>Retention Report</dt>
<dd>
The Retention report shows you how many of your installed users open or engage with your app over time (how users continue to get value from the app). AdvertiserReportCohortRetention reports are particularly good for evaluating the quality of users as opposed to the quantity of users (as in the case of user acquisition campaigns). For more information about retention reports, please visit <a href="http://support.mobileapptracking.com/entries/42179044-Running-AdvertiserReportCohortRetention-Reports">Running AdvertiserReportCohortRetention Reports</a>.

Advertiser Reporting class that perform Retention Reports are:
<ul>
    <li><code>AdvertiserReportCohortRetention</code>: <a href="http://developers.mobileapptracking.com/management-api/explorer/root/endpoint/#/advertiser__stats__retention">/advertiser/stats/retention</a></li>
</ul>
</dd>
</dl>

<p>
<a href="#TOP">
<img alt="Return to Top" src="https://raw.githubusercontent.com/MobileAppTracking/tune-reporting-python/master/docs/images/b_top.gif" border="0">
</a>
</p>

<!-- Licenses -->

<a id="sdk_license" name="sdk_license"></a>
### License

[MIT License](http://opensource.org/licenses/MIT)

<a id="sdk_issues" name="sdk_issues"></a>
### Reporting Issues

Report issues using the [Github Issue Tracker](https://github.com/MobileAppTracking/tune-reporting-python/issues) or Email [sdk@tune.com](mailto:sdk@tune.com).
