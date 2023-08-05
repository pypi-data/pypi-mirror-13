# -*- encoding: utf-8 -*-
# Copyright (c) 2015 b<>com
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#    http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or
# implied.
# See the License for the specific language governing permissions and
# limitations under the License.

from __future__ import unicode_literals

import datetime
import time

from freezegun import freeze_time
from mock import patch
from watcher_metering.agent.measurement import Measurement
from watcher_metering.agent.puller import MetricPuller
from watcher_metering_grid5000.tests._fixtures import FakePuller
from watcher_metering_grid5000.tests.base import BaseTestCase
from watcher_metering_grid5000.wrappers.grid5000 import Grid5000Wrapper


class TestGrid5000Base(BaseTestCase):

    @freeze_time("2015-08-04T15:15:45.703542+00:00")
    def test_format_measurements(self):
        data_puller = FakePuller(
            FakePuller.get_name(),
            FakePuller.get_default_probe_id(),
            FakePuller.get_default_interval(),
            username="fake_username",
            password="fake_password",
            sites=["rennes"],
        )
        site = "TEST"
        expected_measurement = Measurement(
            name="grid5000.fake_metric",
            unit="fake_unit",
            type_="gauge",
            value=0.0255,
            resource_id="testserver-01",
            host="testserver-01",
            # timestamp is truncated at the second by grid5000
            # The first value is the oldest one (one day ago)
            timestamp="2015-08-03T15:15:45+00:00",
            resource_metadata={
                "host": "testserver-01",
                "title": "grid5000_fake_metric",
                "site": "TEST"
            },
        )

        epoch_now = int(time.time())
        one_day = int(datetime.timedelta(days=1).total_seconds())
        from_ = epoch_now - one_day
        raw_measurements = {
            "testserver-01": {
                "hostname": "testserver-01.rennes.grid5000.fr",
                "metric_uid": "fake_metric",
                "links": [{
                    "href": "/3.0/sites/rennes/metrics/fake_metric"
                            "/timeseries/testserver-01",
                    "rel": "self",
                    "type": "application/vnd.fr.grid5000.api.Timeseries+json;"
                            "level=1"
                }, {
                    "href": "/3.0/sites/rennes/metrics/fake_metric",
                    "rel": "parent",
                    "type": "application/vnd.fr.grid5000.api.Metric+json;"
                            "level=1"
                }],
                "from": from_,
                "to": epoch_now,
                "resolution": 360,
                "values": [0.0255],
                "uid": "testserver-01",
                "type": "timeseries"
            },
        }

        formatted_measurement = data_puller.format_measurements(
            site, raw_measurements
        )
        self.assertEqual(1, len(formatted_measurement))
        self.assertEqual(
            expected_measurement.as_dict(),
            formatted_measurement[0].as_dict(),
        )

    @patch.object(MetricPuller, "send_measurements")
    @patch.object(Grid5000Wrapper, "fetch_server_measurements")
    @patch.object(Grid5000Wrapper, "get_metrics_metadata")
    def test_do_pull(self, m_get_metrics_metadata,
                     m_fetch_measurements, m_send_measurements):
        m_get_metrics_metadata.return_value = {
            "fake_metric": {
                "type": "metric",
                "available_on": ["fake_server.fake_site.grid5000.fr"],
                "uid": "fake_metric"
                }
        }

        m_fetch_measurements.return_value = {
            "resolution": 360,
            "from": 1438614945,
            "metric_uid": "fake_metric",
            "to": 1438701345,
            "uid": "fake_site",
            "values": [0.255]
        }

        expected_measurement = Measurement(
            name="grid5000.fake_metric",
            unit="fake_unit",
            type_="gauge",
            value=0.255,
            resource_id="fake_server",
            host="fake_server",
            # timestamp is truncated at the second by grid5000
            # The first value is the oldest one (one day ago)
            timestamp="2015-08-03T15:15:45+00:00",
            resource_metadata={
                "host": "fake_server",
                "title": "grid5000_fake_metric",
                "site": "fake_site"
            },
        )

        data_puller = FakePuller(
            FakePuller.get_name(),
            FakePuller.get_default_probe_id(),
            FakePuller.get_default_interval(),
            username="fake_username",
            password="fake_password",
            sites=["fake_site"],
        )

        # Action
        data_puller.do_pull()

        # Assertions
        self.assertEqual(1, m_send_measurements.call_count)
        sent_measurements = m_send_measurements.call_args[0][0]
        self.assertEqual(1, len(sent_measurements))
        self.assertEqual(
            expected_measurement.as_dict(),
            sent_measurements[0].as_dict(),
        )
