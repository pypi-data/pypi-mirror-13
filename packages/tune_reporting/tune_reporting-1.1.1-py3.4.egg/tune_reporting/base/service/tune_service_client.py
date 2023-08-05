"""
TUNE Service Client
=============================================
"""
#!/usr/bin/env python
# -*- coding: utf-8 -*-
#
#  tune_service_client.py
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
    python_check_version
)
from tune_reporting.version import (
    __sdk_version__,
    __python_required_version__
)

python_check_version(__python_required_version__)

import json

from .tune_service_request import (TuneManagementRequest)
from .tune_service_response import (TuneServiceResponse)
from .constants import (
    __tune_management_api_endpoint__,
    __tune_management_api_version__
)
from tune_reporting.helpers import (
    TuneSdkException
)
from .tune_service_proxy import (
    TuneServiceProxy
)


#  TUNE MobileAppTracking TUNE Reporting API access class
#
#  @example example_client_account_users.py
#
class TuneServiceClient(object):
    """TUNE MobileAppTracking Servoce access class.
    """
    #
    #  @var object @see TuneManagementRequest
    #
    __request = None

    #
    #  @var object @see TuneServiceResponse
    #
    __response = None

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
                 map_query_string=None,
                 api_url_endpoint=__tune_management_api_endpoint__,
                 api_url_version=__tune_management_api_version__):
        """The constructor.

            :param str      controller:         TUNE Reporting API
                                                endpoint name.
            :param str      action:             TUNE Reporting API endpoint's
                                                action name.
            :param str      auth_key:           TUNE Reporting authentication
                                                key.
            :param str      auth_type:          TUNE Reporting authentication
                                                type.
            :param array    map_query_string:  Action's query string
                                                parameters.
            :param str      api_url_endpoint:   TUNE Reporting API
                                                endpoint path.
            :param str      api_url_version:    TUNE Reporting API version.
        """
        # controller
        if not controller or len(controller) < 1:
            raise ValueError("Parameter 'controller' is not defined.")
        # action
        if not action or len(action) < 1:
            raise ValueError("Parameter 'action' is not defined.")

        # set up the request
        self.__request = TuneManagementRequest(
            controller.strip(),
            action.strip(),
            auth_key,
            auth_type,
            map_query_string,
            api_url_endpoint,
            api_url_version
        )

    @staticmethod
    def version():
        """Get SDK version."""
        return __sdk_version__

    #  Sends a request and gets a response from the TUNE Management
    #  API Service.
    #
    def call(self):
        """Sends a request and gets a response from the TUNE Management
        API Service.
        """
        response_success = False

        if self.__request is None or \
           not isinstance(self.__request, TuneManagementRequest):
            raise TuneSdkException("TuneManagementRequest was not defined.")

        try:
            proxy = TuneServiceProxy(self.__request.url)
            if proxy.execute():
                json_string = proxy.response.read().decode('utf-8')
                # Convert from json to python data
                response_json = json.loads(json_string)
                response_http_code = proxy.response.getcode()
                response_headers = proxy.response.info()

                self.__response = TuneServiceResponse(
                    response_json,
                    response_http_code,
                    response_headers,
                    request_url=self.__request.url
                )

                if response_http_code == 200:
                    response_success = True

        except Exception as ex:
            raise TuneSdkException(
                "Failed to execute client request ({}): ({})".format(
                    str(self.__request),
                    str(ex)
                ),
                ex
            )

        return response_success

    @property
    def request(self):
        """Property get request object.
        """
        return self.__request

    @property
    def response(self):
        """Property get response object.
        """
        return self.__response
