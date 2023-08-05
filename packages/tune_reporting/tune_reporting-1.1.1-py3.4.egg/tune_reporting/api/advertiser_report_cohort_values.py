"""
TUNE Reporting API '/advertiser/stats/ltv/'
====================================================
"""
#!/usr/bin/env python
# -*- coding: utf-8 -*-
#
#  advertiser_report_cohort_values.py
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
#  @version   $Date: 2015-12-11 20:56:46 $
#  @link      https://developers.mobileapptracking.com @endlink
#

from tune_reporting.base import (
    AdvertiserReportCohortBase
)
from tune_reporting.base.endpoints import (
    TUNE_FIELDS_DEFAULT
)
from tune_reporting.base.endpoints.advertiser_report_base import (
    AdvertiserReportBase
)
from tune_reporting.helpers import (
    TuneSdkException
)


#  /advertiser/stats/ltv
#  @example example_reports_cohort.py
class AdvertiserReportCohortValues(AdvertiserReportCohortBase):
    """TUNE Reporting API controller 'advertiser/stats/ltv'"""

    ## The constructor.
    #
    def __init__(self):
        """The constructor.
        """
        AdvertiserReportCohortBase.__init__(
            self,
            "advertiser/stats/ltv",
            False,
            True
        )

        self.fields_recommended = [
            "site_id",
            "site.name",
            "publisher_id",
            "publisher.name",
            "rpi",
            "epi"
        ]

    ## Counts all existing records that match filter criteria
    #  and returns an array of found model data.
    #
    # @param dict map_params    Mapping of: <p><dl>
    # <dt>start_date</dt><dd>YYYY-MM-DD HH:MM:SS</dd>
    # <dt>end_date</dt><dd>YYYY-MM-DD HH:MM:SS</dd>
    # <dt>cohort_type</dt><dd>Cohort types: click, install</dd>
    # <dt>cohort_interval</dt><dd>Cohort intervals: year_day, year_week, year_month, year</dd>
    # <dt>group</dt><dd>Group results using this endpoint's fields.</dd>
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

            :param (dict) map_params:\n
                start_date: YYYY-MM-DD HH:MM:SS\n
                end_date: YYYY-MM-DD HH:MM:SS\n
                cohort_type: Cohort types: click, install.\n
                cohort_interval: Cohort intervals:
                    year_day, year_week, year_month, year.\n
                group: Group results using this endpoint's fields.\n
                filter: Apply constraints based upon values
                    associated with this endpoint's fields.\n
                response_timezone: Setting expected timezone for results,
                    default is set in account.\n

            :return: TuneServiceResponse
        """
        map_query_string = {}
        map_query_string = self._validate_datetime(map_params, "start_date", map_query_string)
        map_query_string = self._validate_datetime(map_params, "end_date", map_query_string)

        map_query_string = self._validate_cohort_type(map_params, map_query_string)
        map_query_string = self._validate_cohort_interval(map_params, map_query_string)

        map_query_string = self._validate_group(map_params, map_query_string)

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
    # <dt>cohort_type</dt><dd>Cohort types: click, install</dd>
    # <dt>cohort_interval</dt><dd>Cohort intervals: year_day, year_week, year_month, year</dd>
    # <dt>aggregation_type</dt><dd>Aggregation types: cumulative, incremental</dd>
    # <dt>fields</dt><dd>Present results using these endpoint's fields.</dd>
    # <dt>group</dt><dd>Group results using this endpoint's fields.</dd>
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
                cohort_type: Cohort types: click, install.\n
                cohort_interval: Cohort intervals:
                    year_day, year_week, year_month, year.\n
                aggregation_type: Aggregation types:
                    year_day, year_week, year_month, year.\n
                fields: Present results using these endpoint's fields.\n
                group: Group results using this endpoint's fields.\n
                filter: Apply constraints based upon values
                    associated withthis endpoint's fields.\n
                limit: Limit number of results, default 10, 0 shows all.\n
                page: Pagination, default 1.\n
                sort: Sort results using this endpoint's fields.
                    Directions: DESC, ASC.\n
                response_timezone: Setting expected timezone for results,
                    default is set in account.\n

            :return: (TuneServiceResponse)
        """
        map_query_string = {}
        map_query_string = self._validate_datetime(map_params, "start_date", map_query_string)
        map_query_string = self._validate_datetime(map_params, "end_date", map_query_string)

        map_query_string = self._validate_cohort_type(map_params, map_query_string)
        map_query_string = self._validate_cohort_interval(map_params, map_query_string)
        map_query_string = self._validate_aggregation_type(map_params, map_query_string)

        map_query_string = self._validate_group(map_params, map_query_string)

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

        return self.call(
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
    # <dt>cohort_type</dt><dd>Cohort types: click, install</dd>
    # <dt>cohort_interval</dt><dd>Cohort intervals: year_day, year_week, year_month, year</dd>
    # <dt>aggregation_type</dt><dd>Aggregation types: cumulative, incremental</dd>
    # <dt>fields</dt><dd>Present results using these endpoint's fields.</dd>
    # <dt>group</dt><dd>Group results using this endpoint's fields.</dd>
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
    def export(self,
               map_params):
        """Places a job into a queue to generate a report that will contain
        records that match provided filter criteria, and it returns a job
        identifier to be provided to action /export/download.json to download
        completed report.

            :param (dict) map_params:\n
                start_date: YYYY-MM-DD HH:MM:SS\n
                end_date: YYYY-MM-DD HH:MM:SS\n
                cohort_type: Cohort types: click, install.\n
                cohort_interval: Cohort intervals:
                    year_day, year_week, year_month, year.\n
                aggregation_type: Aggregation types:
                    year_day, year_week, year_month, year.\n
                fields: Present results using these endpoint's fields.\n
                group: Group results using this endpoint's fields.\n
                filter: Apply constraints based upon values
                    associated with this endpoint's fields.\n
                response_timezone: Setting expected timezone for results,
                    default is set in account.\n

            :return: (TuneServiceResponse)
        """
        map_query_string = {}
        map_query_string = self._validate_datetime(map_params, "start_date", map_query_string)
        map_query_string = self._validate_datetime(map_params, "end_date", map_query_string)

        map_query_string = self._validate_cohort_type(map_params, map_query_string)
        map_query_string = self._validate_cohort_interval(map_params, map_query_string)
        map_query_string = self._validate_aggregation_type(map_params, map_query_string)

        map_query_string = self._validate_group(map_params, map_query_string)

        if "fields" not in map_params or map_params["fields"] is None:
          map_params["fields"] = self.fields(TUNE_FIELDS_DEFAULT)
        if "fields" in map_params and map_params["fields"] is not None:
            map_query_string = self._validate_fields(map_params, map_query_string)

        if "filter" in map_params and map_params["filter"] is not None:
            map_query_string = self._validate_filter(map_params, map_query_string)

        if "response_timezone" in map_params and map_params["response_timezone"] is not None:
            map_query_string["response_timezone"] = map_params["response_timezone"]

        return self.call(
            "export",
            map_query_string
        )

    ## Helper function for fetching report document given provided
    #   job identifier.
    #
    #  @param str   job_id      Job Identifier of report on queue.
    #
    #  @return object
    def fetch(self,
              job_id):
        """Helper function for fetching report upon completion.
        Starts worker for polling export queue.

            :param str    job_id:   Provided Job Identifier to reference
                                    requested report on export queue.
            :return: (TuneServiceResponse)
        """
        return super(AdvertiserReportCohortValues, self)._fetch(
            self.controller,
            "status",
            job_id
        )

    ## Validate query string parameter 'cohort_type'.
    #  @param dict map_params
    #  @param dict map_query_string
    #  @return dict map_query_string
    #  @throws ValueError
    @staticmethod
    def _validate_cohort_type(map_params, map_query_string):
        """Validate 'cohort_type' parameter.

            :param (dict) map_params
            :param (dict) map_query_string

            :return (dict): map_query_string
            :throws: ValueError
        """

        if 'cohort_type' not in map_params:
            raise ValueError("Parameter 'cohort_type' is not defined.")

        cohort_type = map_params['cohort_type']

        cohort_types = [
            "click",
            "install"
        ]
        if cohort_type is None or not cohort_type:
            raise ValueError("Parameter 'cohort_type' is not defined.")
        if (not isinstance(cohort_type, str) or
                (cohort_type not in cohort_types)):
            raise TuneSdkException(
                "Parameter 'cohort_type' is invalid: '{}'.".format(
                    cohort_type
                )
            )

        map_query_string['cohort_type'] = cohort_type
        return map_query_string
