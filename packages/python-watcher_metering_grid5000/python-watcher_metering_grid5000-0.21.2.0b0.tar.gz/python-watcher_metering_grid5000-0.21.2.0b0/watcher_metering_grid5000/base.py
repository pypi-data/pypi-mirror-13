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

from oslo_config import cfg
from oslo_log import log
import pytz
import requests
from watcher_metering.agent.measurement import Measurement
from watcher_metering.agent.puller import MetricPuller
from watcher_metering_grid5000.wrappers.grid5000 import Grid5000Wrapper

LOG = log.getLogger(__name__)


class BaseGrid5000MetricPuller(MetricPuller):

    metric_name = NotImplemented  # Should be contained in the above list
    metric_type = NotImplemented
    metric_unit = NotImplemented

    def __init__(self, title, probe_id, interval,
                 username, password, sites):
        super(BaseGrid5000MetricPuller, self).__init__(
            title=title,
            probe_id=probe_id,
            interval=interval,
        )
        self.wrapper = Grid5000Wrapper(
            username=username,
            password=password,
        )
        self.sites = sites
        requests.packages.urllib3.disable_warnings()

    @classmethod
    def get_name(cls):
        return "grid5000_{0}".format(cls.metric_name)

    @classmethod
    def get_default_probe_id(cls):
        return "grid5000.{0}".format(cls.metric_name)

    def get_metric_type(self):
        # either 'gauge' or 'cumulative'
        return self.metric_type

    @property
    def unit(self):
        return self.metric_unit

    @classmethod
    def get_config_opts(cls):
        return cls.get_base_opts() + [
            cfg.StrOpt(
                'username',
                help='Grid5000 username'),
            cfg.StrOpt(
                'password',
                secret=True,
                help='Grid5000 password'),
            cfg.ListOpt(
                'sites',
                default=[],
                help='List of Grid5000 datacenters/sites against which '
                     'the measurements shall be retrieved'),
        ]

    @classmethod
    def validate(cls, measurement):
        """Should make some assertions to make sure the value is correct
        :raises: AssertionError
        """
        assert measurement

    def do_pull(self):
        """Retrives the number of CPUs on the host"""
        LOG.info("[%s] Pulling measurements...", self.key)

        for site in self.sites:
            LOG.info("[%s] Running metric collection on the site %s ",
                     self.key, site)
            try:
                site_metrics_metadata = self.wrapper.get_metrics_metadata(site)
                metric_metadata = site_metrics_metadata[self.metric_name]
                LOG.info("[%s][%s] Fetching measurements...", self.key, site)
                grid5000_measurements = self.wrapper.fetch_site_measurements(
                    site, metric_metadata
                )

                LOG.info("[%s][%s] Formatting measurements...", self.key, site)
                site_measurements = self.format_measurements(
                    site, grid5000_measurements
                )

                # Sends the measurements explicitly now
                self.send_measurements(site_measurements)
            except KeyError as exc:
                LOG.debug("[%s] Metric not available", self.metric_name)
            except Exception as exc:
                LOG.exception(exc)
            else:
                LOG.info("[%s][STATS] Scanned %d sites from %d in total",
                         self.key, self.wrapper.site_stats.get("num_sites", 0),
                         len(self.sites))
            finally:
                # Stats are reset after each pulling
                self.wrapper.log_stats()
                # Stats are reset after each pulling
                self.wrapper.reset_stats()

        return []

    def format_measurements(self, site, raw_measurements):
        # gauge and cumulative attribution is not working 100%
        measurements = []
        for server_name, metric in raw_measurements.items():
            if all([val is None for val in metric['values']]):
                LOG.debug(
                    "[%s] No `%s` values to add for server `%s`",
                    site, metric['metric_uid'], server_name
                )
                continue

            timestamp = float(metric['from'])
            for value in metric['values']:
                if value is not None:
                    try:
                        value = float(value)
                        iso_datetime = datetime.datetime.fromtimestamp(
                            timestamp, tz=pytz.utc,
                        )
                        resource_metadata = {
                            "host": server_name,
                            "title": self.title,
                            "site": site
                        }
                        measurement = Measurement(
                            name=self.probe_id,
                            unit=self.unit,
                            type_=self.get_metric_type(),
                            value=value,
                            resource_id=server_name,
                            timestamp=iso_datetime.isoformat(),
                            host=server_name,
                            resource_metadata=resource_metadata,
                        )
                        self.validate(measurement)
                        # Adds the measurements if it has been validated
                        measurements.append(measurement)
                    except Exception as exc:
                        LOG.exception(exc)
                timestamp = timestamp + metric['resolution']

        return measurements
