"""
TUNE Service Request
=============================================
"""
#!/usr/bin/env python
# -*- coding: utf-8 -*-
#
#  tune_service_request.py
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

from tune_reporting.helpers import (
    TuneSdkException
)
from .query_string_builder import (
    QueryStringBuilder
)
from tune_reporting.version import (
    __sdk_name__,
    __sdk_version__
)

class TuneManagementRequest(object):
    """Base components for every TUNE Service Client request.
    """
    __controller = None
    __action = None
    __auth_key = None
    __auth_type = None
    __query_string_dict = None
    __api_url_endpoint = None
    __api_url_version = None

    #  Constructor
    #
    #  @param str      controller           TUNE Reporting API endpoint
    #                                       name.
    #  @param str      action               TUNE Reporting API endpoint's
    #                                       action name.
    #  @param str      auth_key             TUNE Reporting authentication key.
    #  @param str      auth_type            TUNE Reporting authentication type.
    #  @param null|array  map_query_string Action's query string parameters.
    #  @param null|string api_url_endpoint  TUNE Reporting API endpoint path.
    #  @param null|string api_url_version   TUNE Reporting API version.
    #
    def __init__(self,
                 controller,
                 action,
                 auth_key,
                 auth_type,
                 map_query_string,
                 api_url_endpoint,
                 api_url_version):
        """The constructor.

            :param str      controller:         TUNE Reporting API
                                                endpoint name.
            :param str      action:             TUNE Reporting API
                                                endpoint's action name.
            :param str      auth_key            TUNE Reporting authentication
                                                key.
            :param str      auth_type           TUNE Reporting authentication
                                                type.
            :param array    map_query_string:  Action's query string
                                                parameters
            :param str      api_url_endpoint:   TUNE Reporting API
                                                endpoint path
            :param str      api_url_version:    TUNE Reporting API version
        """
        # -----------------------------------------------------------------
        # validate_fields inputs
        # -----------------------------------------------------------------

        # controller
        if not controller or len(controller) < 1:
            raise ValueError("Parameter 'controller' is not defined.")
        # action
        if not action or len(action) < 1:
            raise ValueError("Parameter 'action' is not defined.")
        if not api_url_endpoint or len(api_url_endpoint) < 1:
            raise ValueError("Parameter 'api_url_endpoint' is not defined.")
        if not api_url_version or len(api_url_version) < 1:
            raise ValueError("Parameter 'api_url_version' is not defined.")

        self.__controller = controller
        self.__action = action
        self.__auth_key = auth_key
        self.__auth_type = auth_type
        self.__query_string_dict = map_query_string
        self.__api_url_endpoint = api_url_endpoint
        self.__api_url_version = api_url_version

    @property
    def controller(self):
        """TUNE Reporting API controller."""
        return self.__controller

    @property
    def action(self):
        """TUNE Reporting API action."""
        return self.__action

    @property
    def endpoint_base(self):
        """TUNE Reporting API endpoint_base URL"""
        return self.__api_url_endpoint

    @property
    def version(self):
        """TUNE Reporting API version"""
        return self.__api_url_version

    @property
    def auth_key(self):
        """TUNE Reporting authentication key."""
        return self.__auth_key

    @property
    def auth_type(self):
        """TUNE Reporting authentication type."""
        return self.__auth_type

    @property
    def map_query_string(self):
        """
        TUNE Reporting API query string dictionary used to build Query String.
        """
        return self.__query_string_dict

    @property
    def query_string(self):
        """TUNE Reporting API query string."""
        qsb = QueryStringBuilder()

        qsb.add("sdk", __sdk_name__)
        qsb.add("ver", __sdk_version__)

        if self.__auth_key and self.__auth_type:
            qsb.add(self.__auth_type, self.__auth_key)

        # Build query string with provided contents in dictionary
        if self.__query_string_dict is not None:
            for name, value in self.__query_string_dict.items():
                qsb.add(name, value)

        return str(qsb)

    @property
    def path(self):
        """TUNE Reporting API service path"""
        request_path = "{0}/{1}/{2}/{3}".format(
            self.__api_url_endpoint,
            self.__api_url_version,
            self.__controller,
            self.__action
        )

        return request_path

    @property
    def url(self):
        """TUNE Reporting API full service request."""
        request_url = "{0}?{1}".format(
            self.path,
            self.query_string
        )

        return request_url

    def __str__(self):
        """Pretty print.

            :rtype: str
        """
        pretty = "\napi_url_endpoint_base:\t " + str(self.__api_url_endpoint)
        pretty += "\napi_url_version:\t " + str(self.__api_url_version)
        pretty += "\ncontroller:\t " + str(self.__controller)
        pretty += "\naction:\t " + str(self.__action)
        pretty += "\nauth_type:\t " + str(self.__auth_type)
        pretty += "\nauth_key:\t " + str(self.__auth_key)
        pretty += "\nurl:\t " + str(self.url)
        return pretty
