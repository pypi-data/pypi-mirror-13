#!/usr/bin/env python
# -*- coding: utf-8 -*-
#
#  example_advertiser_report_actuals.py
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
#  The Actuals report gives you quick insight into the performance of your apps
#  and advertising partners (publishers). Use this report for reconciliation,
#  testing, debugging, and ensuring that all measurement and attribution continues
#  to operate smoothly. MAT generates this report by aggregating all the logs of
#  each request (MAT updates the report every 5 minutes).
#
#  API call(s) stats/
#

import datetime
import os.path
import sys
import traceback

try:
    from tune_reporting import (
        AdvertiserReportActuals,
        ReportReaderCSV,
        SdkConfig,
        TuneSdkException,
        TUNE_FIELDS_RECOMMENDED,
        TUNE_FIELDS_DEFAULT
        )
except ImportError as exc:
    sys.stderr.write("Error: failed to import module ({})".format(exc))
    raise


class ExampleAdvertiserReportActuals(object):
    """Example using TUNE Advertiser Report Actuals."""

    def __init__(self):
        pass

    #
    # Example of running successful requests to TUNE Advertiser Report Actuals.
    #
    def run(self,
            auth_key,
            auth_type):

        # Setup TUNE Reporting SDK configuration.
        dirname = os.path.split(__file__)[0]
        dirname = os.path.dirname(dirname)
        filepath = os.path.join(dirname, "config", SdkConfig.SDK_CONFIG_FILENAME)

        abspath = os.path.abspath(filepath)

        sdk_config = SdkConfig(filepath=abspath)
        if auth_type and auth_key:
            sdk_config.auth_key = auth_key
            sdk_config.auth_type = auth_type

        print("")
        print("\033[34m" + "================================================" + "\033[0m")
        print("\033[34m" + " TUNE Advertiser Report Actuals                 " + "\033[0m")
        print("\033[34m" + "================================================" + "\033[0m")

        try:
            week_ago = datetime.date.fromordinal(datetime.date.today().toordinal() - 8)
            yesterday = datetime.date.fromordinal(datetime.date.today().toordinal() - 1)
            start_date = "{} 00:00:00".format(week_ago)
            end_date = "{} 23:59:59".format(yesterday)

            advertiser_report = AdvertiserReportActuals()

            print("")
            print("===========================================================")
            print(" Default Fields of Advertiser Report Actuals               ")
            print("===========================================================")

            response = advertiser_report.fields(TUNE_FIELDS_DEFAULT)
            for field in response:
                print(str(field))

            print("")
            print("===========================================================")
            print(" Recommended Fields of Advertiser Report Actuals           ")
            print("===========================================================")

            response = advertiser_report.fields(TUNE_FIELDS_RECOMMENDED)
            for field in response:
                print(str(field))

            print("")
            print("===========================================================")
            print(" Count Advertiser Report Actuals.                          ")
            print("===========================================================")

            map_params = {
                "start_date": start_date,
                "end_date": end_date,
                "filter": "(publisher_id > 0)",
                "group": "site_id,publisher_id",
                "response_timezone": "America/Los_Angeles"
            }

            response = advertiser_report.count(
                map_params
            )

            if response.http_code != 200 or response.errors:
                raise Exception("Failed: {}: {}".format(response.http_code, str(response)))

            print(" TuneServiceResponse:")
            print(str(response))

            print(" JSON:")
            print(response.json)

            print(" Count:")
            print(str(response.data))

            print("")
            print("===========================================================")
            print(" Find Advertiser Report Actuals with Default fields.       ")
            print("===========================================================")

            map_params = {
                "start_date": start_date,
                "end_date": end_date,
                "fields": None,
                "filter": "(publisher_id > 0)",
                "group": "site_id,publisher_id",
                "limit": 5,
                "page": None,
                "sort": {"paid_installs": "DESC"},
                "timestamp": "datehour",
                "response_timezone": "America/Los_Angeles"
            }

            response = advertiser_report.find(
                map_params
            )

            if response.http_code != 200 or response.errors:
                raise Exception("Failed: {}: {}".format(response.http_code, str(response)))

            print(" TuneServiceResponse:")
            print(str(response))

            print(" JSON:")
            print(response.json)

            print("")
            print("===========================================================")
            print(" Find Advertiser Report Actuals with Recommended fields.   ")
            print("===========================================================")

            map_params = {
                "start_date": start_date,
                "end_date": end_date,
                "fields": advertiser_report.fields(TUNE_FIELDS_RECOMMENDED),
                "filter": "(publisher_id > 0)",
                "group": "site_id,publisher_id",
                "limit": 5,
                "page": None,
                "sort": {"paid_installs": "DESC"},
                "timestamp": "datehour",
                "response_timezone": "America/Los_Angeles"
            }

            response = advertiser_report.find(
                map_params
            )

            if response.http_code != 200 or response.errors:
                raise Exception("Failed: {}: {}".format(response.http_code, str(response)))

            print(" TuneServiceResponse:")
            print(str(response))

            print(" JSON:")
            print(response.json)

            print("")
            print("===========================================================")
            print(" Export Advertiser Report Actuals CSV                      ")
            print("===========================================================")

            map_params = {
                "start_date": start_date,
                "end_date": end_date,
                "fields": advertiser_report.fields(TUNE_FIELDS_RECOMMENDED),
                "filter": "(publisher_id > 0)",
                "group": "site_id,publisher_id",
                "format": "csv",
                "timestamp": "datehour",
                "response_timezone": "America/Los_Angeles"
            }

            response = advertiser_report.export(
                map_params
            )

            if response.http_code != 200 or response.errors:
                raise Exception("Failed: {}: {}".format(response.http_code, str(response)))

            print(" TuneServiceResponse:")
            print(str(response))

            print(" JSON:")
            print(str(response.json))

            job_id = AdvertiserReportActuals.parse_response_report_job_id(response)

            print(" CSV Job ID: {}".format(job_id))

            print("")
            print("===========================================================")
            print(" Status Advertiser Report Actuals CSV                    ")
            print("===========================================================")

            status_response = advertiser_report.status(
                job_id
            )

            print(" TuneServiceResponse:")
            print(str(status_response))

            print(" JSON:")
            print(str(status_response.json))

            print("")
            print("===========================================================")
            print(" Fetching Advertiser Report Actuals CSV                    ")
            print("===========================================================")

            fetch_response = advertiser_report.fetch(
                job_id
            )

            csv_report_url = AdvertiserReportActuals.parse_response_report_url(fetch_response)

            print(" CVS Report URL: {}".format(csv_report_url))

            print("")
            print("===========================================================")
            print(" Read Advertiser Report Actuals CSV                        ")
            print("===========================================================")

            csv_report_reader = ReportReaderCSV(csv_report_url)
            csv_report_reader.read()
            csv_report_reader.pretty_print(limit=5)

        except TuneSdkException as exc:
            print("TuneSdkException ({})".format(exc))
            print(self.provide_traceback())
            raise
        except Exception:
            exc_type, exc_value, exc_traceback = sys.exc_info()
            print("*** print_tb:")
            traceback.print_tb(exc_traceback, limit=1, file=sys.stdout)
            print("*** print_exception:")
            traceback.print_exception(exc_type, exc_value, exc_traceback,
                                      limit=2, file=sys.stdout)
            print("*** print_exc:")
            traceback.print_exc()
            raise

        print("")
        print("\033[32m" + "======================================" + "\033[0m")
        print("\033[32m" + " End Example                          " + "\033[0m")
        print("\033[32m" + "======================================" + "\033[0m")

    @staticmethod
    def provide_traceback():
        "Provide traceback of provided exception."
        exception_list = traceback.format_stack()
        exception_list = exception_list[:-2]
        exception_list.extend(traceback.format_tb(sys.exc_info()[2]))
        exception_list.extend(traceback.format_exception_only(sys.exc_info()[0], sys.exc_info()[1]))

        exception_str = "Traceback (most recent call last):\n"
        exception_str += "".join(exception_list)
        # Removing the last \n
        exception_str = exception_str[:-1]

        return exception_str

if __name__ == '__main__':
    try:
        if len(sys.argv) < 2:
            raise ValueError("{} [auth_key].".format(sys.argv[0]))
        auth_key = sys.argv[1]
        example = ExampleAdvertiserReportActuals()
        example.run(auth_key)
    except Exception as exc:
        print("Exception: {0}".format(exc))
        raise
