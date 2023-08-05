"""tune report_reader_base
"""
#!/usr/bin/env python
# -*- coding: utf-8 -*-
#
#  report_reader_base.py
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
#  @version   $Date: 2015-01-05 19:38:53 $
#  @link      https://developers.mobileapptracking.com @endlink
#

from abc import ABCMeta, abstractproperty


class ReportReaderBase(object):
    """Base Abstract class."""

    __metaclass__ = ABCMeta

    __report_url = None
    __report_data = None
    __row_count = None

    #  The constructor
    #  @param str report_url Download report URL
    #                         of requested report to be exported.
    def __init__(self, report_url):
        """Constructor

            :param str report_url: Download report URL.
        """
        if not report_url or \
           not isinstance(report_url, str) or \
           len(report_url) < 1:
            raise ValueError("Parameter 'report_url' is not defined.")

        self.__report_url = report_url
        self.__report_data = None

    @abstractproperty
    def read(self):
        """Get property for TuneManagementRequest Action Name."""
        return

    @property
    def report_url(self):
        """REPORT_URL of completed report on SQS."""
        return self.__report_url

    @property
    def data(self):
        """Provide created reader populated with file data."""
        return self.__report_data

    @data.setter
    def data(self, value):
        """Provide data value."""
        self.__report_data = value

    @property
    def count(self):
        """Count number of row within gather file data.

            :return: Count
            :rtype: int
        """
        return self.__row_count

    @count.setter
    def count(self, value):
        """Provide data value."""
        self.__row_count = value
