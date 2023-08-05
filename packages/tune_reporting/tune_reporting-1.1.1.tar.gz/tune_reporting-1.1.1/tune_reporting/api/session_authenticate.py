"""session_authenticate.py
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

## TUNE Reporting API endpoint '/session/authenticate'
#
class SessionAuthenticate(EndpointBase):
    """TUNE Reporting API endpoint '/session/authenticate/'."""

    ## The constructor.
    #
    def __init__(self):
        """The constructor.
        """

        EndpointBase.__init__(
            self,
            controller="session/authenticate",
            use_config=False
        )

    ## Generate session token is returned to provide access to service.
    #
    #  @param string api_keys  Generate 'session token' for this api_keys.
    #  @return object @see TuneServiceResponse
    def api_key(self,
                api_keys):
        """
        Generate session token is returned to provide access to service.

            :param api_keys (string):   Generate 'session token'
                                        for this api_keys.
            :return: TuneServiceResponse
        """
        if not api_keys or len(api_keys) < 1:
            raise ValueError("Parameter 'api_keys' is not defined.")

        return EndpointBase.call(
            self,
            action="api_key",
            map_query_string={
                'api_keys': api_keys
            }
        )
