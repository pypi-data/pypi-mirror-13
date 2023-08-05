"""
TUNE Service Response
=============================================
"""
#!/usr/bin/env python
# -*- coding: utf-8 -*-
#
#  tune_service_response.py
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


class TuneServiceResponse(object):
    """Response container of TUNE Service Client.
    """

    __response_json = None
    __response_http_code = None
    __response_headers = None
    __request_url = None

    def __init__(self,
                 response_json=None,
                 response_http_code=None,
                 response_headers=None,
                 request_url=None):
        """The constructor.

            :param str   response_json:         TUNE Reporting API Service
                                                full response.
            :param str   response_http_code:    TUNE Reporting API Service
                                                response HTTP code.
            :param array response_headers:      TUNE Reporting API Service
                                                response HTTP headers.
            :param str   request_url:           TUNE Reporting API request
                                                URL.
        """
        self.__response_json = response_json
        self.__response_http_code = response_http_code
        self.__response_headers = response_headers
        self.__request_url = request_url

    @property
    def request_url(self):
        """
        Initial TuneManagementRequest URL to TUNE Reporting API Service.
        """
        return self.__request_url

    @property
    def json(self):
        """
        Get property for Full JSON response returned
        from TUNE Reporting API Service."""
        return dict([(str(k), v) for k, v in self.__response_json.items()])

    @property
    def http_code(self):
        """Get property for HTTP Code of response."""
        return self.__response_http_code

    @property
    def headers(self):
        """Get property for HTTP Headers of response."""
        return self.__response_headers

    @property
    def data(self):
        """
        Get property to get 'data' portion of JSON response returned
        from TUNE Reporting API Service.
        """
        if 'data' in self.__response_json:
            return self.__response_json['data']
        return None

    @property
    def size(self):
        """
        Get property to get 'response_size' portion of JSON
        response returned from TUNE Reporting API Service.
        """
        if 'response_size' in self.__response_json:
            return self.__response_json['response_size']
        return None

    @property
    def status_code(self):
        """
        Get property to get 'status_code' portion of JSON
        response returned from TUNE Reporting API Service.
        """
        if 'status_code' in self.__response_json:
            return self.__response_json['status_code']
        return None

    @property
    def errors(self):
        """
        Get property to get 'errors' portion of JSON response
        returned from TUNE Reporting API Service.
        """
        if 'errors' in self.__response_json:
            return self.__response_json['errors']
        return None

    def __str__(self):
        """
        Pretty print response including HTTP connection
        results and TUNE Management Service JSON components.

            Returns:
                string
        """
        pretty = "\nrequest_url:\t " + str(self.request_url)
        pretty += "\nstatus_code:\t " + str(self.status_code)
        pretty += "\nresponse_size:\t " + str(self.size)
        pretty += "\ndata:\t\t" + json.dumps(
            self.data,
            sort_keys=True,
            indent=4,
            separators=(',', ': ')
        )
        pretty += "\nerrors:\t\t" + json.dumps(
            self.errors,
            sort_keys=True,
            indent=4,
            separators=(',', ': ')
        )
        pretty += "\nhttp_code:\t\t" + str(self.http_code)
        pretty += "\nheaders:\n" + str(self.headers)
        return pretty
