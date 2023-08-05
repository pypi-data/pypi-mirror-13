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

import os

import httpretty
from watcher_metering_grid5000.tests.base import BaseTestCase
from watcher_metering_grid5000.wrappers.grid5000 import Grid5000Wrapper


class TestGrid5000Wrapper(BaseTestCase):

    @httpretty.activate
    def test_grid5k_fetch_uri(self):
        httpretty.register_uri(httpretty.GET, "https://fake.uri.com",
                               body='[{"title": "Test OK"}]')

        wrapper = Grid5000Wrapper(
            username="fake_username",
            password="fake_password",
        )
        json_data = wrapper.fetch_uri("https://fake.uri.com")
        self.assertEqual(json_data, [{"title": "Test OK"}])

    @httpretty.activate
    def test_get_metrics_metadata(self):
        site = "rennes"
        with open(
            os.path.join(
                os.path.dirname(__file__),
                "test_data", "metadata.json")
            ) as data_file:
            raw_data = data_file.read()
            httpretty.register_uri(
                httpretty.GET,
                "https://api.grid5000.fr/3.0/sites/rennes/metrics",
                body=raw_data,
            )

        wrapper = Grid5000Wrapper(
            username="fake_username",
            password="fake_password",
        )

        expected_site_metric_metadata = {
            "cpu_nice": {
                "type": "metric",
                "available_on": ["fake_server.fake_site.grid5000.fr"],
                "uid": "cpu_nice",
                "links": [{
                    "href": "/3.0/sites/rennes/metrics/cpu_nice",
                    "rel": "self",
                    "type": "application/vnd.fr.grid5000.api.Metric+json;"
                            "level=1"
                }, {
                    "href": "/3.0/sites/rennes/metrics/cpu_nice/timeseries",
                    "title": "timeseries",
                    "rel": "collection",
                    "type": "application/vnd.fr.grid5000.api.Collection+json;"
                            "level=1"
                }, {
                    "href": "/3.0/sites/rennes",
                    "rel": "parent",
                    "type": "application/vnd.fr.grid5000.api.Site+json;level=1"
                }],
                "step": 15,
                "timeseries": [{
                    "xff": 0.5,
                    "cf": "AVERAGE",
                    "rows": 244,
                    "pdp_per_row": 1
                }, {
                    "xff": 0.5,
                    "cf": "AVERAGE",
                    "rows": 244,
                    "pdp_per_row": 24
                }, {
                    "xff": 0.5,
                    "cf": "AVERAGE",
                    "rows": 244,
                    "pdp_per_row": 168
                }, {
                    "xff": 0.5,
                    "cf": "AVERAGE",
                    "rows": 244,
                    "pdp_per_row": 672
                }, {
                    "xff": 0.5,
                    "cf": "AVERAGE",
                    "rows": 374,
                    "pdp_per_row": 5760
                }]
            }
        }

        json_data = wrapper.get_metrics_metadata(site)

        self.assertEqual(expected_site_metric_metadata, json_data)

    @httpretty.activate
    def test_fetch_site_measurements(self):
        site = "rennes"
        mocked_uri = (
            'https://api.grid5000.fr/3.0/sites/rennes/metrics/cpu_nice/'
            'timeseries?from=1445934571&to=1446020971&only=fake_server'
        )
        with open(
            os.path.join(os.path.dirname(__file__),
                         "test_data", "cpu_nice.json")
            ) as data_file:
            raw_data = data_file.read()
            httpretty.register_uri(
                httpretty.GET,
                mocked_uri,
                verify=False,
                body=raw_data,
            )

        metric_metadata = {
            "type": "metric",
            "available_on": ["fake_server.rennes.grid5000.fr"],
            "uid": "cpu_nice",
            "links": [{
                "href": "/3.0/sites/rennes/metrics/cpu_nice",
                "rel": "self",
                "type": "application/vnd.fr.grid5000.api.Metric+json;"
                        "level=1"
            }, {
                "href": "/3.0/sites/rennes/metrics/cpu_nice/timeseries",
                "title": "timeseries",
                "rel": "collection",
                "type": "application/vnd.fr.grid5000.api.Collection+json;"
                        "level=1"
            }, {
                "href": "/3.0/sites/rennes",
                "rel": "parent",
                "type": "application/vnd.fr.grid5000.api.Site+json;level=1"
            }],
            "step": 15,
            "timeseries": [{
                "xff": 0.5,
                "cf": "AVERAGE",
                "rows": 244,
                "pdp_per_row": 1
            }, {
                "xff": 0.5,
                "cf": "AVERAGE",
                "rows": 244,
                "pdp_per_row": 24
            }, {
                "xff": 0.5,
                "cf": "AVERAGE",
                "rows": 244,
                "pdp_per_row": 168
            }, {
                "xff": 0.5,
                "cf": "AVERAGE",
                "rows": 244,
                "pdp_per_row": 672
            }, {
                "xff": 0.5,
                "cf": "AVERAGE",
                "rows": 374,
                "pdp_per_row": 5760
            }]
        }

        expected_measurements = {
            "fake_server": {
                "resolution": 360,
                "from": 1445890320,
                "metric_uid": "cpu_nice",
                "to": 1445967360,
                "uid": "fake_server",
                "type": "timeseries",
                "values": [0.0, 1.07, 1.83305555555556, None, 0.0, 0.0],
                "links": [{
                    "href": "/3.0/sites/rennes/metrics/cpu_nice/timeseries/"
                            "fake_server",
                    "rel": "self",
                    "type": "application/vnd.fr.grid5000.api.Timeseries+json;"
                            "level=1"
                }, {
                    "href": "/3.0/sites/rennes/metrics/cpu_nice",
                    "rel": "parent",
                    "type": "application/vnd.fr.grid5000.api.Metric+json;"
                            "level=1"
                }],
                "hostname": "fake_server.rennes.grid5000.fr"
            }
        }

        wrapper = Grid5000Wrapper(
            username="fake_username",
            password="fake_password",
        )

        site_measurements = wrapper.fetch_site_measurements(
            site, metric_metadata
        )
        self.assertEqual(expected_measurements, site_measurements)
