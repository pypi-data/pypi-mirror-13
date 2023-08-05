"""
TUNE Reporting API '/advertiser/stats/event/items/'
====================================================
"""
#!/usr/bin/env python
# -*- coding: utf-8 -*-
#
#  advertiser_report_log_event_items.py
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
    AdvertiserReportLogBase
)


#  /advertiser/stats/event/items
#  @example example_reports_event_items.py
class AdvertiserReportLogEventItems(AdvertiserReportLogBase):
    """Advertiser Stats logs pertaining to event items."""

    ## The constructor.
    #
    def __init__(self):
        """The constructor.
        """
        AdvertiserReportLogBase.__init__(
            self,
            "advertiser/stats/event/items",
            False,
            True
        )

        self.fields_recommended = [
            "id",
            "created",
            "site_id",
            "site.name",
            "campaign_id",
            "campaign.name",
            "site_event_id",
            "site_event.name",
            "site_event_item_id",
            "site_event_item.name",
            "quantity",
            "value_usd",
            "country_id",
            "country.name",
            "region_id",
            "region.name",
            "agency_id",
            "agency.name",
            "advertiser_sub_site_id",
            "advertiser_sub_site.name",
            "advertiser_sub_campaign_id",
            "advertiser_sub_campaign.name",
            "currency_code",
            "value"
        ]
