#!/usr/bin/env python
# -*- coding: utf-8 -*-
#
#  Copyright (c) 2015 TUNE, Inc.
#  All rights reserved.
#
#  Permission is hereby granted, free of charge, to any person obtaining a copy
#  of this software and associated documentation files (the "Software"), to deal
#  in the Software without restriction, including without limitation the rights
#  to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
#  copies of the Software, and to permit persons to whom the Software is
#  furnished to do so, subject to the following conditions:
#
#  The above copyright notice and this permission notice shall be included in
#  all copies or substantial portions of the Software.
#
#  THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
#  IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
#  FITNESS FOR A PARTICULAR PURPOSE AND NON-INFRINGEMENT. IN NO EVENT SHALL THE
#  AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
#  LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
#  OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN
#  THE SOFTWARE.
#
#  Python 2.7
#
#  @category  Tune_Reporting
#  @package   Tune_Reporting_Python
#  @author    Jeff Tanner <jefft@tune.com>
#  @copyright 2015 TUNE, Inc. (http://www.tune.com)
#  @license   http://opensource.org/licenses/MIT The MIT License (MIT)
#  @version   $Date: 2015-12-11 20:56:46 $
#  @link      https://developers.mobileapptracking.com @endlink
#

import datetime
import os.path
import sys
import traceback

try:
    from tune_reporting import (
        SdkConfig,
        SessionAuthenticate
        )
except ImportError as exc:
    sys.stderr.write("Error: failed to import module ({})".format(exc))
    raise

from example_advertiser_report_actuals import ExampleAdvertiserReportActuals
from example_advertiser_report_cohort_values import ExampleAdvertiserReportCohortValues
from example_advertiser_report_cohort_retention import ExampleAdvertiserReportCohortRetention

from example_advertiser_report_log_clicks import ExampleAdvertiserReportLogClicks
from example_advertiser_report_log_event_items import ExampleAdvertiserReportLogEventItems
from example_advertiser_report_log_events import ExampleAdvertiserReportLogEvents
from example_advertiser_report_log_installs import ExampleAdvertiserReportLogInstalls
from example_advertiser_report_log_postbacks import ExampleAdvertiserReportLogPostbacks

if __name__ == '__main__':
    try:
        if len(sys.argv) < 2:
            raise ValueError(
                "Provide API Key to execute TUNE Advertiser Reporting examples {}.".format(sys.argv[0])
                )

        api_key = sys.argv[1]
        # api_key
        if not api_key or (len(api_key) < 1):
            raise ValueError("Parameter 'api_key' is not defined.")

        print(" api_key:")
        print(api_key)

        session_authenticate = SessionAuthenticate()
        response = session_authenticate.api_key(api_key)
        session_token = response.data

        print(" session_token:")
        print(session_token)
        # session_token
        if not session_token or (len(session_token) < 1):
            raise ValueError("Parameter 'session_token' is not defined.")

        example = ExampleAdvertiserReportActuals()
        example.run(session_token, "session_token")

        example = ExampleAdvertiserReportCohortValues()
        example.run(session_token, "session_token")

        example = ExampleAdvertiserReportCohortRetention()
        example.run(session_token, "session_token")

        example = ExampleAdvertiserReportLogClicks()
        example.run(session_token, "session_token")

        example = ExampleAdvertiserReportLogEventItems()
        example.run(session_token, "session_token")

        example = ExampleAdvertiserReportLogEvents()
        example.run(session_token, "session_token")

        example = ExampleAdvertiserReportLogInstalls()
        example.run(session_token, "session_token")

        example = ExampleAdvertiserReportLogPostbacks()
        example.run(session_token, "session_token")

    except Exception as exc:
        print("Exception: {0}".format(exc))
        raise
