"""export.py
"""
#!/usr/bin/env python
# -*- coding: utf-8 -*-
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

import sys

from tune_reporting.base import (
    EndpointBase
)


## TUNE Reporting API endpoint '/export'
#
class Export(EndpointBase):
    """TUNE Reporting API endpoint '/export/'."""

    ## The constructor.
    #
    def __init__(self):
        """The constructor.
        """

        EndpointBase.__init__(
            self,
            controller="export",
            use_config=True
        )

    ## TuneManagementRequest status from export queue for report.
    #  When completed, url will be provided for downloading report.
    #
    #  @param str job_id   Job identifier assigned for report export.
    #  @return object @see TuneServiceResponse
    def download(self,
                 job_id):
        """
        Action 'download' for polling export queue for status information on
        request report to be exported.

            :param str job_id:   Job identifier assigned for report export.
            :return: TuneServiceResponse
        """
        if not job_id or len(job_id) < 1:
            raise ValueError("Parameter 'job_id' is not defined.")

        return EndpointBase.call(
            self,
            action="download",
            map_query_string={
                'job_id': job_id
            }
        )

    ## Helper function for fetching report upon completion.
    #  Starts worker for polling export queue.
    #
    #  @param str   job_id      Job identifier assigned for report export.
    #  @return object Document contents
    def fetch(self,
              job_id):
        """Helper function for fetching report upon completion.
        Starts worker for polling export queue.

            :param str  job_id:     Job identifier assigned for report export.
            :return:   Document contents
        """
        if not job_id or len(job_id) < 1:
            raise ValueError("Parameter 'job_id' is not defined.")

        return self._fetch(
            "export",
            "download",
            job_id
        )

    ## Helper function for parsing export status response to gather report url.
    #  @param @see TuneServiceResponse
    #  @return str Report Url
    @staticmethod
    def parse_response_report_url(response):
        """Helper function for parsing export status response to
        gather report url.

            :param object response: TuneServiceResponse
            :return (str): Report Url
            :throws: TuneSdkException
        """
        if not response:
            raise ValueError("Parameter 'response' is not defined.")
        if not response.data:
            raise ValueError("Parameter 'response.data' is not defined.")
        if "data" not in response.data:
            raise ValueError(
                "Parameter 'response.data['data'] is not defined."
            )
        if "url" not in response.data["data"]:
            raise ValueError(
                "Parameter 'response.data['data']['url'] is not defined."
            )

        url = response.data["data"]["url"]

        if sys.version_info >= (3, 0, 0):
            # for Python 3
            if isinstance(url, bytes):
                url = url.decode('ascii')  # or  s = str(s)[2:-1]
        else:
            if isinstance(url, unicode):
                url = str(url)

        return url
