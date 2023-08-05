"""
TUNE Service Logs Reports Endpoint base
=============================================
"""
#!/usr/bin/env python
# -*- coding: utf-8 -*-
#
#  advertiser_report_log_base.py
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


from .advertiser_report_base import (
    AdvertiserReportBase
)
from tune_reporting.base.service import (
    TuneServiceClient
)
from tune_reporting.base.endpoints import (
    TUNE_FIELDS_DEFAULT
)


## Base class intended for gathering from Advertiser Stats logs.
##
class AdvertiserReportLogBase(AdvertiserReportBase):
    """
    Base class intended for gathering from Advertiser Stats logs.
    """

    ## The constructor.
    #
    #  @param str controller                    TUNE Reporting API endpoint
    #                                           name.
    #  @param bool   filter_debug_mode          Remove debug mode information
    #                                           from results.
    #  @param bool   filter_test_profile_id     Remove test profile information
    #                                           from results.
    def __init__(self,
                 controller,
                 filter_debug_mode,
                 filter_test_profile_id):
        """The constructor.

            :param str controller:          TUNE Reporting API endpoint name.
            :param bool filter_debug_mode:  Remove debug mode information
                                                    from results.
            :param bool filter_test_profile_id: Remove test profile information
                                                    from results.
        """
        # controller
        if not controller or len(controller) < 1:
            raise ValueError("Parameter 'controller' is not defined.")

        AdvertiserReportBase.__init__(
            self,
            controller,
            filter_debug_mode,
            filter_test_profile_id
        )

    ## Counts all existing records that match filter criteria
    #  and returns an array of found model data.
    #
    # @param dict map_params    Mapping of: <p><dl>
    # <dt>start_date</dt><dd>YYYY-MM-DD HH:MM:SS</dd>
    # <dt>end_date</dt><dd>YYYY-MM-DD HH:MM:SS</dd>
    # <dt>filter</dt><dd>Apply constraints based upon values associated with
    #                    this endpoint's fields.</dd>
    # <dt>response_timezone</dt><dd>Setting expected timezone for results,
    #                          default is set in account.</dd>
    # </dl><p>
    #
    #  @return object TuneServiceResponse
    #
    def count(self,
              map_params):
        """Counts all existing records that match filter criteria
        and returns an array of found model data.

            :param (dict) map_params\n
                start_date: YYYY-MM-DD HH:MM:SS\n\n
                end_date: YYYY-MM-DD HH:MM:SS\n\n
                filter: Apply constraints based upon values
                    associated with this endpoint's fields.\n\n
                response_timezone: Setting expected timezone for results,
                    default is set in account.\n\n

            :return: (TuneServiceResponse)
        """
        map_query_string = {};
        map_query_string = self._validate_datetime(map_params, "start_date", map_query_string)
        map_query_string = self._validate_datetime(map_params, "end_date", map_query_string)

        if "filter" in map_params and map_params["filter"] is not None:
            map_query_string = self._validate_filter(map_params, map_query_string)

        if "response_timezone" in map_params and map_params["response_timezone"] is not None:
            map_query_string["response_timezone"] = map_params["response_timezone"]

        return AdvertiserReportBase.call(
            self,
            "count",
            map_query_string
        )

    ## Finds all existing records that match filter criteria
    #  and returns an array of found model data.
    #
    # @param dict map_params    Mapping of: <p><dl>
    # <dt>start_date</dt><dd>YYYY-MM-DD HH:MM:SS</dd>
    # <dt>end_date</dt><dd>YYYY-MM-DD HH:MM:SS</dd>
    # <dt>fields</dt><dd>Present results using these endpoint's fields.</dd>
    # <dt>filter</dt><dd>Apply constraints based upon values associated with
    #                    this endpoint's fields.</dd>
    # <dt>limit</dt><dd>Limit number of results, default 10, 0 shows all.</dd>
    # <dt>page</dt><dd>Pagination, default 1.</dd>
    # <dt>sort</dt><dd>Sort results using this endpoint's fields.
    #                    Directions: DESC, ASC</dd>
    # <dt>response_timezone</dt><dd>Setting expected timezone for results,
    #                          default is set in account.</dd>
    # </dl><p>
    #
    #  @return object TuneServiceResponse
    #
    def find(self,
             map_params):
        """Finds all existing records that match filter criteria
        and returns an array of found model data.

            :param (dict) map_params:\n
                start_date: YYYY-MM-DD HH:MM:SS\n
                end_date: YYYY-MM-DD HH:MM:SS\n
                fields: Present results using these endpoint's fields.\n
                filter: Apply constraints based upon values
                    associated with this endpoint's fields.\n
                limit: Limit number of results, default 10, 0 shows all.\n
                page: Pagination, default 1.\n
                sort: Sort results using this endpoint's fields.
                    Directions: DESC, ASC.\n
                response_timezone: Setting expected timezone for results,
                    default is set in account.\n

            :return (object): (TuneServiceResponse)
        """
        if map_params is None or \
           not isinstance(map_params, dict):
            raise ValueError(
                "Parameter 'map_params' is not defined as dict."
            )

        map_query_string = {}
        map_query_string = self._validate_datetime(map_params, "start_date", map_query_string)
        map_query_string = self._validate_datetime(map_params, "end_date", map_query_string)

        if "filter" in map_params and map_params["filter"] is not None:
            map_query_string = self._validate_filter(map_params, map_query_string)

        if "fields" not in map_params or map_params["fields"] is None:
          map_params["fields"] = self.fields(TUNE_FIELDS_DEFAULT)
        if "fields" in map_params and map_params["fields"] is not None:
            map_query_string = self._validate_fields(map_params, map_query_string)

        if "limit" in map_params and map_params["limit"] is not None:
            map_query_string = self._validate_limit(map_params, map_query_string)
        if "page" in map_params and map_params["page"] is not None:
            map_query_string = self._validate_page(map_params, map_query_string)

        if "sort" in map_params and map_params["sort"] is not None:
            map_query_string = self._validate_sort(map_params, map_query_string)

        if "response_timezone" in map_params and map_params["response_timezone"] is not None:
            map_query_string["response_timezone"] = map_params["response_timezone"]

        return AdvertiserReportBase.call(
            self,
            "find",
            map_query_string
        )

    ## Places a job into a queue to generate a report that will contain
    #  records that match provided filter criteria, and it returns a job
    #  identifier to be provided to action /export/download.json to download
    #  completed report.
    #
    # @param dict map_params    Mapping of: <p><dl>
    # <dt>start_date</dt><dd>YYYY-MM-DD HH:MM:SS</dd>
    # <dt>end_date</dt><dd>YYYY-MM-DD HH:MM:SS</dd>
    # <dt>fields</dt><dd>Present results using these endpoint's fields.</dd>
    # <dt>filter</dt><dd>Apply constraints based upon values associated with
    #                    this endpoint's fields.</dd>
    # <dt>format</dt><dd>Export format choices: csv</dd>
    # <dt>response_timezone</dt><dd>Setting expected timezone for results,
    #                          default is set in account.</dd>
    # </dl><p>
    #
    #  @return object TuneServiceResponse
    #
    def export(self,
               map_params):
        """Places a job into a queue to generate a report that will contain
        records that match provided filter criteria, and it returns a job
        identifier to be provided to action /export/download.json to download
        completed report.

            :param (dict) map_params:\n
                start_date: YYYY-MM-DD HH:MM:SS\n
                end_date: YYYY-MM-DD HH:MM:SS\n
                fields: Present results using these endpoint's fields.\n
                filter: Apply constraints based upon values
                    associated with this endpoint's fields.\n
                format: Export format choices: csv.\n
                response_timezone: Setting expected timezone for results,
                    default is set in account.\n

            :return: (TuneServiceResponse)
        """
        if map_params is None or \
           not isinstance(map_params, dict):
            raise ValueError(
                "Parameter 'map_params' is not defined as dict."
            )

        map_query_string = {}
        map_query_string = self._validate_datetime(map_params, "start_date", map_query_string)
        map_query_string = self._validate_datetime(map_params, "end_date", map_query_string)

        if "fields" not in map_params or map_params["fields"] is None:
          map_params["fields"] = self.fields(TUNE_FIELDS_DEFAULT)
        if "fields" in map_params and map_params["fields"] is not None:
            map_query_string = self._validate_fields(map_params, map_query_string)

        if "filter" in map_params and map_params["filter"] is not None:
            map_query_string = self._validate_filter(map_params, map_query_string)

        if "format" in map_params and map_params["format"] is not None:
            map_query_string = self._validate_format(map_params, map_query_string)
        else:
            map_query_string["format"] = 'csv'

        if "response_timezone" in map_params and map_params["response_timezone"] is not None:
            map_query_string["response_timezone"] = map_params["response_timezone"]

        return AdvertiserReportBase.call(
            self,
            "find_export_queue",
            map_query_string
        )

    ## Query status of insight reports. Upon completion will
    #  return url to download requested report.
    #
    #  @param str job_id    Provided Job Identifier to reference requested
    #                                   report on export queue.
    #
    #  @return object TuneServiceResponse
    #
    def status(self,
               job_id):
        """Query status of insight reports. Upon completion will return url to
        download requested report.

            :param str job_id: Export queue identifier
            :return (object): (TuneServiceResponse)
        """

        # job_id
        if not job_id or len(job_id) < 1:
            raise ValueError("Parameter 'job_id' is not defined.")

        client = TuneServiceClient(
            controller="export",
            action="download",
            auth_key=self.auth_key,
            auth_type=self.auth_type,
            map_query_string={
                'job_id': job_id
            }
        )

        client.call()

        return client.response

    ## Helper function for fetching report upon completion.
    #
    #  @param str   job_id      Job identifier assigned for report export.
    #  @return object @see TuneServiceResponse
    def fetch(self,
              job_id):
        """Helper function for fetching report upon completion.

            :param str  job_id:     Job identifier assigned for report export.
            :return: (TuneServiceResponse)
        """
        # job_id
        if not job_id or len(job_id) < 1:
            raise ValueError("Parameter 'job_id' is not defined.")

        return self._fetch(
            "export",
            "download",
            job_id
        )
