"""
TUNE Shared Helper Functions
=============================================
"""
#!/usr/bin/env python
# -*- coding: utf-8 -*-
#
#  utils.py
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
#  @version   $Date: 2015-07-30 12:49:27 $
#  @link      https://developers.mobileapptracking.com @endlink
#

import sys


#  Check Python Version
#
def python_check_version(required_version):
    """Check Python Version
    :param: required_version
    """
    current_version = sys.version_info
    if current_version[0] == required_version[0] and \
       current_version[1] >= required_version[1]:
        pass
    elif current_version[0] > required_version[0]:
        pass
    else:
        sys.stderr.write(
            "[%s] - Error: Python interpreter must be %d.%d or greater"
            " to use this library, current version is %d.%d.\n"
            % (
                sys.argv[0],
                required_version[0],
                required_version[1],
                current_version[0],
                current_version[1]
            )
        )
        sys.exit(-1)
    return 0


#  Check if string has balance parentheses.
#
def is_parentheses_balanced(string, i=0, cnt=0):
    """Check if string has balance parentheses.

        :param str string: Expression with parentheses.
        :return: True if balanced.
        :rtype: bool
    """
    if i == len(string):
        return cnt == 0
    if cnt < 0:
        return False
    if string[i] == "(":
        return is_parentheses_balanced(string, i + 1, cnt + 1)
    if string[i] == ")":
        return is_parentheses_balanced(string, i + 1, cnt - 1)
    return is_parentheses_balanced(string, i + 1, cnt)


#  Convert unicode contents of JSON file to utf-8
#
def json_convert(json_str):
    """Convert unicode contents of JSON file to utf-8

        :param str json_str: JSON string
    """
    if isinstance(json_str, dict):
        return {
            json_convert(key):
                json_convert(value) for key, value in json_str.iteritems()
        }
    elif isinstance(json_str, list):
        return [json_convert(element) for element in json_str]

    if sys.version_info >= (3, 0, 0):
        # for Python 3
        if isinstance(json_str, bytes):
            json_str = json_str.encode('utf-8')  # or  s = str(s)[2:-1]
    else:
        if isinstance(json_str, unicode):
            json_str = json_str.encode('utf-8')

    return json_str
