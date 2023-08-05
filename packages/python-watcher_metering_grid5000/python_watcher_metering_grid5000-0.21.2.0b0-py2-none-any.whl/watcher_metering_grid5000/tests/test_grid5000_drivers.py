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

from mock import patch
from watcher_metering.agent.measurement import Measurement
from watcher_metering.agent.puller import MetricPuller
from watcher_metering_grid5000.opts import GRID5000_DRIVERS
from watcher_metering_grid5000.tests.base import BaseTestCase
from watcher_metering_grid5000.wrappers.grid5000 import Grid5000Wrapper


class TestGrid5000Drivers(BaseTestCase):

    scenarios = [
        (
            "SCENARIO_NAME", {
                "metric_puller_cls": drivers_cls,
                "metric_name": drivers_cls.metric_name,
                "metric_unit": drivers_cls.metric_unit,
                "metric_type": drivers_cls.metric_type,
            }
        )
        for drivers_cls in GRID5000_DRIVERS
    ]

    @patch.object(MetricPuller, "send_measurements")
    @patch("watcher_metering_grid5000.base.Grid5000Wrapper.reset_stats")
    @patch.object(Grid5000Wrapper, "fetch_server_measurements")
    @patch.object(Grid5000Wrapper, "get_metrics_metadata")
    def test_grid5k_pull(self, m_get_metrics_metadata, m_fetch_measurements,
                         m_reset_stats, m_send_measurements):
        m_get_metrics_metadata.return_value = {
            self.metric_name: {
                "type": "metric",
                "available_on": ["fake_server.fake_site.grid5000.fr"],
                "uid": self.metric_name
                }
        }

        m_fetch_measurements.return_value = {
            "resolution": 360,
            "from": 1438614945,
            "metric_uid": self.metric_name,
            "to": 1438701345,
            "uid": "fake_site",
            "values": [0.255]
        }

        expected_measurement = Measurement(
            name="grid5000.%s" % self.metric_name,
            unit=self.metric_unit,
            type_=self.metric_type,
            value=0.255,
            resource_id="fake_server",
            host="fake_server",
            # timestamp is truncated at the second by grid5000
            # The first value is the oldest one (one day ago)
            timestamp="2015-08-03T15:15:45+00:00",
            resource_metadata={
                "host": "fake_server",
                "title": "grid5000_%s" % self.metric_name,
                "site": "fake_site"
            },
        )

        data_puller = self.metric_puller_cls(
            self.metric_puller_cls.get_name(),
            self.metric_puller_cls.get_default_probe_id(),
            self.metric_puller_cls.get_default_interval(),
            username="fake_username",
            password="fake_password",
            sites=["fake_site"],
        )
        data_puller.do_pull()

        # Assertions
        self.assertEqual(1, m_send_measurements.call_count)
        sent_measurements = m_send_measurements.call_args[0][0]
        self.assertEqual(1, len(sent_measurements))
        self.assertEqual(
            expected_measurement.as_dict(),
            sent_measurements[0].as_dict(),
        )

        self.assertEqual(1, data_puller.wrapper.site_stats["num_sites"])
        self.assertEqual(1, data_puller.wrapper.site_stats["measurements"])
        self.assertEqual(
            1,
            data_puller.wrapper.site_stats[
                "sites"
            ]["fake_site"]["measurements"]
        )
        self.assertEqual(
            1,
            data_puller.wrapper.site_stats[
                "sites"
            ]["fake_site"]["series"][self.metric_name]["measurements"]
        )

        self.assertEqual(1, m_reset_stats.call_count)
