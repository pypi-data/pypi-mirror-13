"""
TUNE Service Exception
======================
"""
#!/usr/bin/env python
# -*- coding: utf-8 -*-
#
#  exceptions.py
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


class TuneSdkException(Exception):
    """Exception raised for errors when using TUNE SDK
    """

    #
    # Failure response type
    #
    __errors = None

    ## Constructor
    #
    def __init__(self, message=None, errors=None):
        """TUNE SDK exception constructor

            :param str          message:    Message describing error.
            :param Exception    exc:        Caught exception.
        """
        if message is None:
            message = "TUNE SDK error"

        # Call the endpoint_base class constructor with the parameters it needs
        Exception.__init__(self, message)

        # Now for your custom code...
        self.__errors = errors

    @property
    def errors(self):
        """Get property of error object."""
        return self.__errors


class TuneServiceException(Exception):
    """Exception raised when error is returned from TUNE Management Service
    """

    #
    # Failure response type
    #
    __errors = None

    ## Constructor
    #
    def __init__(self, message=None, errors=None):
        """TUNE Reporting API Service exception constructor

            :param str message: Message describing error.
            :param Exception exc: Caught exception.
        """
        if message is None:
            message = "TUNE Service error"

        # Call the endpoint_base class constructor with the parameters it needs
        Exception.__init__(self, message)

        # Now for your custom code...
        self.__errors = errors
