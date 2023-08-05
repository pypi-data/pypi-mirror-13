"""
TUNE Advertiser Report JSON Reader
=======================
"""
#!/usr/bin/env python
# -*- coding: utf-8 -*-
#
#  report_reader_json.py
#
#  Copyright (c) 2015 TUNE, Inc.
#  All rights reserved.
#
#  Permission is hereby granted, free of charge, to any person obtaining
#  a copy of this software and associated documentation files
#  (the "Software"), to deal in the Software without restriction, including
#  without limitation the rights to use, copy, modify, merge, publish,
#  distribute, sublicense, and/or sell copies of the Software, and to permit
#  persons to whom the Software is furnished to do so, subject to the
#  following conditions:
#
#  The above copyright notice and this permission notice shall be included in
#  all copies or substantial portions of the Software.
#
#  THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
#  IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
#  FITNESS FOR A PARTICULAR PURPOSE AND NON-INFRINGEMENT. IN NO EVENT SHALL
#  THE AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
#  LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING
#  FROM, OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER
#  DEALINGS IN THE SOFTWARE.
#
#  Python 2.7 and 3.0
#
#  @category  Tune_Reporting
#  @package   Tune_Reporting_Python
#  @author    Jeff Tanner <jefft@tune.com>
#  @copyright 2015 TUNE, Inc. (http://www.tune.com)
#  @license   http://opensource.org/licenses/MIT The MIT License (MIT)
#  @version   $Date: 2015-04-09 17:36:25 $
#  @link      https://developers.mobileapptracking.com @endlink
#

import json

from .report_reader_base import (
    ReportReaderBase
)
from tune_reporting.base.service import (
    TuneServiceProxy
)


## Helper class for reading reading remote JSON file
#
class ReportReaderJSON(ReportReaderBase):
    """Helper class for reading reading remote JSON file"""

    #  The constructor
    #  @param str report_url Download report URL
    #                         of requested report to be exported.
    def __init__(self, report_url):
        """The constructor.

            :param str report_url: Report URL to be downloaded.
        """
        ReportReaderBase.__init__(self, report_url)

    #  Using provided report download URL, extract JSON contents.
    #
    def read(self):
        """Read JSON data provided remote path report_url."""
        self.data = None

        proxy = TuneServiceProxy(self.report_url)

        if proxy.execute():
            utf8_report_content = proxy.response.read().decode('utf-8')
            self.data = json.loads(utf8_report_content)
            self.count = len(self.data)

    def pretty_print(self, limit=0):
        """Pretty print exported data.

            :param int limit: Number of rows to print.
        """
        print("Report REPORT_URL: {}".format(self.report_url))
        print("Report total row count: {}".format(self.count))
        if self.count > 0:
            print("------------------")
            rows = list(self.data)
            i = 0
            for row in enumerate(rows):
                i = i + 1
                print("{}. {}".format(i, str(row)))
                if (limit > 0) and (i >= limit):
                    break
            print("------------------")
