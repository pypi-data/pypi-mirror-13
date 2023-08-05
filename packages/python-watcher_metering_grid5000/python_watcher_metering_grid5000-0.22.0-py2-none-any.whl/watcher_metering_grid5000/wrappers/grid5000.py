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

from collections import defaultdict
import datetime
import time

from oslo_log import log
import pytz
import requests

LOG = log.getLogger(__name__)


class Grid5000Wrapper(object):

    _epoch = datetime.datetime(1970, 1, 1, tzinfo=pytz.utc)

    def __init__(self, username, password):
        super(Grid5000Wrapper, self).__init__()
        self.username = username
        self.password = password

        self.site_stats = {}
        # Used to store the I/O stats of each site for the current run
        self._reset_stats()

    def reset_stats(self):
        self._reset_stats()

    def _reset_stats(self):
        self.site_stats = {
            "measurements": 0,
            "num_sites": 0,
            "sites": defaultdict(
                lambda: {"measurements": 0,
                         "num_servers": 0,
                         "series": defaultdict(
                             lambda: {"measurements": 0})}
            )
        }

    def log_stats(self):
        LOG.info("*****************")
        LOG.info("Total measurements: %d", self.site_stats["measurements"])
        for site_name, site_data in self.site_stats["sites"].items():
            LOG.info(" - [`%s`] --> %d measurements",
                     site_name, site_data["measurements"])

        LOG.info("--- Per-metric stats ---")
        metric_stats = {}
        for site_name, site_data in self.site_stats["sites"].items():
            for metric_name, metric_data in site_data["series"].items():
                # Add the entry if needed
                metric_stats.setdefault(metric_name, 0)
                metric_stats[metric_name] += metric_data["measurements"]

        for metric_name, measurements in metric_stats.items():
            LOG.info(" - [`%s`] --> %d measurements",
                     metric_name, measurements)

        LOG.debug(self.site_stats)
        LOG.info("*****************")

    def fetch_uri(self, uri):
        response = requests.get(
            uri,
            auth=(self.username, self.password),
            verify=False
        )
        try:
            return response.json()
        except Exception as exc:
            LOG.exception(exc)
            LOG.error("%s returned a none valid Json Object", uri)

    def get_metrics_metadata(self, site):
        uri = "https://api.grid5000.fr/3.0/sites/{site}/metrics".format(
            site=site
        )
        try:
            list_metrics = self.fetch_uri(uri)['items']
            LOG.info("[STATS] %d metrics on site %s " %
                     (len(list_metrics), site))
            return {
                meta["uid"]: meta for meta in list_metrics if "uid" in meta
            }
        except Exception as exc:
            LOG.exception(exc)
            LOG.warn("Could not fetch metric names!")

    def fetch_site_measurements(self, site, metric_metadata):
        server_values = {}
        for server in metric_metadata["available_on"]:
            try:
                metric_name = metric_metadata["uid"]
                server_name = server.rpartition(site)[0].rstrip(".")
                values = self.fetch_server_measurements(
                    metric_name, site, server_name
                )
            except Exception as exc:
                LOG.exception(exc)
                LOG.error(
                    "[fetch_site_measurements] Error: `%s`, `%s`",
                    metric_metadata['uid'],
                    server_name
                )
            num_values = len(values.get("values", []))
            self.site_stats["measurements"] += num_values
            self.site_stats["sites"][site]["num_servers"] += 1
            self.site_stats["sites"][site]["measurements"] += num_values
            self.site_stats["sites"][site][
                "series"
            ][metric_name]["measurements"] += num_values
            server_values[server_name] = values

        self.site_stats["num_sites"] += 1

        return server_values

    def fetch_server_measurements(self, metric, site, server):
        epoch_now = int(time.time())
        one_day = int(datetime.timedelta(days=1).total_seconds())
        from_ = epoch_now - one_day  # start 1 day ago
        server_uri = (
            "https://api.grid5000.fr/3.0/sites/{site}/metrics/{metric}"
            "/timeseries?from={from_}&to={to}&only={server}"
        ).format(
            site=site,
            metric=metric,
            from_=from_,
            to=epoch_now,
            server=server,
        )

        try:
            result = self.fetch_uri(server_uri)
            metric_values = result['items'][0]
        except requests.exceptions.RequestException as exc:
            LOG.error("Error while querying this url `%s`", server_uri)
            LOG.exception(exc)
            return {}
        except IndexError as exc:
            LOG.debug("Items list of %s is empty", server)
            return {}
        else:
            return metric_values
