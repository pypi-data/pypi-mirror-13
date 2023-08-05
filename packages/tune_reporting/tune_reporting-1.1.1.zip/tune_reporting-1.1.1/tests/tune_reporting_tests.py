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

import sys
import unittest

from test_advertiser_report_log_clicks import TestAdvertiserReportLogClicks
from test_advertiser_report_log_event_items import TestAdvertiserReportLogEventItems
from test_advertiser_report_log_events import TestAdvertiserReportLogEvents
from test_advertiser_report_log_installs import TestAdvertiserReportLogInstalls
from test_advertiser_report_log_postbacks import TestAdvertiserReportLogPostbacks
from test_advertiser_report_actuals import TestAdvertiserReportActuals
from test_advertiser_report_cohort_retention import TestAdvertiserReportCohortRetention
from test_advertiser_report_cohort_values import TestAdvertiserReportCohortValues

def suite(api_key):
    suite = unittest.TestSuite()

    suite.addTest(TestAdvertiserReportLogClicks(api_key))
    suite.addTest(TestAdvertiserReportLogEventItems(api_key))
    suite.addTest(TestAdvertiserReportLogEvents(api_key))
    suite.addTest(TestAdvertiserReportLogInstalls(api_key))
    suite.addTest(TestAdvertiserReportLogPostbacks(api_key))
    suite.addTest(TestAdvertiserReportActuals(api_key))
    suite.addTest(TestAdvertiserReportCohortRetention(api_key))
    suite.addTest(TestAdvertiserReportCohortValues(api_key))

    return suite

if __name__ == '__main__':
    try:
        if len(sys.argv) > 1:
            api_key = sys.argv.pop()

    except Exception as exc:
        print("Exception: {0}".format(exc))
        raise

    runner = unittest.TextTestRunner()

    test_suite = suite(api_key)

    runner.run(test_suite)
