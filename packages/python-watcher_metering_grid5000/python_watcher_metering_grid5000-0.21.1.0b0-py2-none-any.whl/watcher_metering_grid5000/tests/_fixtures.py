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

from oslo_log import log
from watcher_metering_grid5000.base import BaseGrid5000MetricPuller

LOG = log.getLogger(__name__)


class FakePuller(BaseGrid5000MetricPuller):

    metric_type = "gauge"
    metric_name = "fake_metric"
    metric_unit = "fake_unit"

    @classmethod
    def get_default_interval(cls):
        return 1  # 1 second
