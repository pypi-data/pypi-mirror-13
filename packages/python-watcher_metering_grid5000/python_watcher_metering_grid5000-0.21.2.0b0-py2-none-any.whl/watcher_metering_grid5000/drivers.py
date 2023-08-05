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


class Grid5kBoottime(BaseGrid5000MetricPuller):

    metric_name = "boottime"
    metric_type = "cumulative"
    metric_unit = "s"  # seconds

    @classmethod
    def get_default_interval(cls):
        return 60 * 60 * 24  # 1 day


# class Grid5kBreadSec(BaseGrid5000MetricPuller):

#     metric_name = "bread_sec"
#     metric_type = "gauge"
#     metric_unit = "1/sec"

#     @classmethod
#     def get_default_interval(cls):
#         return 60 * 60 * 24  # 1 day


# class Grid5kBwriteSec(BaseGrid5000MetricPuller):

#     metric_name = "bwrite_sec"
#     metric_type = "gauge"
#     metric_unit = "1/sec"

#     @classmethod
#     def get_default_interval(cls):
#         return 60 * 60 * 24  # 1 day


class Grid5kBytesIn(BaseGrid5000MetricPuller):

    metric_name = "bytes_in"
    metric_type = "gauge"
    metric_unit = "bytes/sec"

    @classmethod
    def get_default_interval(cls):
        return 60 * 60 * 24  # 1 day


class Grid5kBytesOut(BaseGrid5000MetricPuller):

    metric_name = "bytes_out"
    metric_type = "gauge"
    metric_unit = "bytes/sec"

    @classmethod
    def get_default_interval(cls):
        return 60 * 60 * 24  # 1 day


class Grid5kCpuAidle(BaseGrid5000MetricPuller):

    metric_name = "cpu_aidle"
    metric_type = "gauge"
    metric_unit = "%"

    @classmethod
    def get_default_interval(cls):
        return 60 * 60 * 24  # 1 day


# class Grid5kCpuArm(BaseGrid5000MetricPuller):

#     metric_name = "cpu_arm"
#     metric_type = "gauge"
#     metric_unit = "%"

#     @classmethod
#     def get_default_interval(cls):
#         return 60 * 60 * 24  # 1 day


# class Grid5kCpuAvm(BaseGrid5000MetricPuller):

#     metric_name = "cpu_avm"
#     metric_type = "gauge"
#     metric_unit = "%"

#     @classmethod
#     def get_default_interval(cls):
#         return 60 * 60 * 24  # 1 day


class Grid5kCpuIdle(BaseGrid5000MetricPuller):

    metric_name = "cpu_idle"
    metric_type = "gauge"
    metric_unit = "%"

    @classmethod
    def get_default_interval(cls):
        return 60 * 60 * 24  # 1 day


# class Grid5kCpuIntr(BaseGrid5000MetricPuller):

#     metric_name = "cpu_intr"
#     metric_type = "gauge"
#     metric_unit = "%"

#     @classmethod
#     def get_default_interval(cls):
#         return 60 * 60 * 24  # 1 day


class Grid5kCpuNice(BaseGrid5000MetricPuller):

    metric_name = "cpu_nice"
    metric_type = "gauge"
    metric_unit = "%"

    @classmethod
    def get_default_interval(cls):
        return 60 * 60 * 24  # 1 day


class Grid5kCpuNum(BaseGrid5000MetricPuller):

    metric_name = "cpu_num"
    metric_type = "gauge"
    metric_unit = "CPUs"

    @classmethod
    def get_default_interval(cls):
        return 60 * 60 * 24  # 1 day


# class Grid5kCpuRm(BaseGrid5000MetricPuller):

#     metric_name = "cpu_rm"
#     metric_type = "gauge"
#     metric_unit = "%"

#     @classmethod
#     def get_default_interval(cls):
#         return 60 * 60 * 24  # 1 day


class Grid5kCpuSpeed(BaseGrid5000MetricPuller):

    metric_name = "cpu_speed"
    metric_type = "gauge"
    metric_unit = "MHz"

    @classmethod
    def get_default_interval(cls):
        return 60 * 60 * 24  # 1 day


class Grid5kCpuSsys(BaseGrid5000MetricPuller):

    metric_name = "cpu_ssys"
    metric_type = "gauge"
    metric_unit = "%"

    @classmethod
    def get_default_interval(cls):
        return 60 * 60 * 24  # 1 day


class Grid5kCpuSystem(BaseGrid5000MetricPuller):

    metric_name = "cpu_system"
    metric_type = "gauge"
    metric_unit = "%"

    @classmethod
    def get_default_interval(cls):
        return 60 * 60 * 24  # 1 day


class Grid5kCpuUser(BaseGrid5000MetricPuller):

    metric_name = "cpu_user"
    metric_type = "gauge"
    metric_unit = "%"

    @classmethod
    def get_default_interval(cls):
        return 60 * 60 * 24  # 1 day


# class Grid5kCpuVm(BaseGrid5000MetricPuller):

#     metric_name = "cpu_vm"
#     metric_type = "gauge"
#     metric_unit = "%"

#     @classmethod
#     def get_default_interval(cls):
#         return 60 * 60 * 24  # 1 day


# class Grid5kCpuWait(BaseGrid5000MetricPuller):

#     metric_name = "cpu_wait"
#     metric_type = "gauge"
#     metric_unit = "%"

#     @classmethod
#     def get_default_interval(cls):
#         return 60 * 60 * 24  # 1 day


# class Grid5kCpuWio(BaseGrid5000MetricPuller):

#     metric_name = "cpu_wio"
#     metric_type = "gauge"
#     metric_unit = "%"

#     @classmethod
#     def get_default_interval(cls):
#         return 60 * 60 * 24  # 1 day


class Grid5kDiskFree(BaseGrid5000MetricPuller):

    metric_name = "disk_free"
    metric_type = "gauge"
    metric_unit = "GB"

    @classmethod
    def get_default_interval(cls):
        return 60 * 60 * 24  # 1 day


class Grid5kDiskTotal(BaseGrid5000MetricPuller):

    metric_name = "disk_total"
    metric_type = "gauge"
    metric_unit = "GB"

    @classmethod
    def get_default_interval(cls):
        return 60 * 60 * 24  # 1 day


class Grid5kLoadFifteen(BaseGrid5000MetricPuller):

    metric_name = "load_fifteen"
    metric_type = "gauge"
    metric_unit = " "

    @classmethod
    def get_default_interval(cls):
        return 60 * 60 * 24  # 1 day


class Grid5kLoadFive(BaseGrid5000MetricPuller):

    metric_name = "load_five"
    metric_type = "gauge"
    metric_unit = " "

    @classmethod
    def get_default_interval(cls):
        return 60 * 60 * 24  # 1 day


class Grid5kLoadOne(BaseGrid5000MetricPuller):

    metric_name = "load_one"
    metric_type = "gauge"
    metric_unit = " "

    @classmethod
    def get_default_interval(cls):
        return 60 * 60 * 24  # 1 day


class Grid5kLocation(BaseGrid5000MetricPuller):

    metric_name = "location"
    metric_type = "gauge"
    metric_unit = "(x,y,z)"

    @classmethod
    def get_default_interval(cls):
        return 60 * 60 * 24  # 1 day


# class Grid5kLreadSec(BaseGrid5000MetricPuller):

#     metric_name = "lread_sec"
#     metric_type = "gauge"
#     metric_unit = "1/sec"

#     @classmethod
#     def get_default_interval(cls):
#         return 60 * 60 * 24  # 1 day


# class Grid5kLwriteSec(BaseGrid5000MetricPuller):

#     metric_name = "lwrite_sec"
#     metric_type = "gauge"
#     metric_unit = "1/sec"

#     @classmethod
#     def get_default_interval(cls):
#         return 60 * 60 * 24  # 1 day


class Grid5kMachineType(BaseGrid5000MetricPuller):

    metric_name = "machine_type"
    metric_type = "gauge"
    metric_unit = ""

    @classmethod
    def get_default_interval(cls):
        return 60 * 60 * 24  # 1 day


class Grid5kMemBuffers(BaseGrid5000MetricPuller):

    metric_name = "mem_buffers"
    metric_type = "gauge"
    metric_unit = "KB"

    @classmethod
    def get_default_interval(cls):
        return 60 * 60 * 24  # 1 day


class Grid5kMemCached(BaseGrid5000MetricPuller):

    metric_name = "mem_cached"
    metric_type = "gauge"
    metric_unit = "KB"

    @classmethod
    def get_default_interval(cls):
        return 60 * 60 * 24  # 1 day


class Grid5kMemFree(BaseGrid5000MetricPuller):

    metric_name = "mem_free"
    metric_type = "gauge"
    metric_unit = "KB"

    @classmethod
    def get_default_interval(cls):
        return 60 * 60 * 24  # 1 day


class Grid5kMemShared(BaseGrid5000MetricPuller):

    metric_name = "mem_shared"
    metric_type = "gauge"
    metric_unit = "KB"

    @classmethod
    def get_default_interval(cls):
        return 60 * 60 * 24  # 1 day


class Grid5kMemSreclaimable(BaseGrid5000MetricPuller):

    metric_name = "mem_sreclaimable"
    metric_type = "gauge"
    metric_unit = "KB"

    @classmethod
    def get_default_interval(cls):
        return 60 * 60 * 24  # 1 day


class Grid5kMemTotal(BaseGrid5000MetricPuller):

    metric_name = "mem_total"
    metric_type = "gauge"
    metric_unit = "KB"

    @classmethod
    def get_default_interval(cls):
        return 60 * 60 * 24  # 1 day


class Grid5kMtu(BaseGrid5000MetricPuller):

    metric_name = "mtu"
    metric_type = "gauge"
    metric_unit = ""

    @classmethod
    def get_default_interval(cls):
        return 60 * 60 * 24  # 1 day


class Grid5kOsName(BaseGrid5000MetricPuller):

    metric_name = "os_name"
    metric_type = "gauge"
    metric_unit = ""

    @classmethod
    def get_default_interval(cls):
        return 60 * 60 * 24  # 1 day


class Grid5kOsRelease(BaseGrid5000MetricPuller):

    metric_name = "os_release"
    metric_type = "gauge"
    metric_unit = ""

    @classmethod
    def get_default_interval(cls):
        return 60 * 60 * 24  # 1 day


class Grid5kPartMaxUsed(BaseGrid5000MetricPuller):

    metric_name = "part_max_used"
    metric_type = "gauge"
    metric_unit = "%"

    @classmethod
    def get_default_interval(cls):
        return 60 * 60 * 24  # 1 day


# class Grid5kPhreadSec(BaseGrid5000MetricPuller):

#     metric_name = "phread_sec"
#     metric_type = "gauge"
#     metric_unit = "1/sec"

#     @classmethod
#     def get_default_interval(cls):
#         return 60 * 60 * 24  # 1 day


# class Grid5kPhwriteSec(BaseGrid5000MetricPuller):

#     metric_name = "phwrite_sec"
#     metric_type = "gauge"
#     metric_unit = "1/sec"

#     @classmethod
#     def get_default_interval(cls):
#         return 60 * 60 * 24  # 1 day


class Grid5kPktsIn(BaseGrid5000MetricPuller):

    metric_name = "pkts_in"
    metric_type = "gauge"
    metric_unit = "packets/sec"

    @classmethod
    def get_default_interval(cls):
        return 60 * 60 * 24  # 1 day


class Grid5kPktsOut(BaseGrid5000MetricPuller):

    metric_name = "pkts_out"
    metric_type = "gauge"
    metric_unit = "packets/sec"

    @classmethod
    def get_default_interval(cls):
        return 60 * 60 * 24  # 1 day


class Grid5kProcRun(BaseGrid5000MetricPuller):

    metric_name = "proc_run"
    metric_type = "gauge"
    metric_unit = " "  # Number of processes

    @classmethod
    def get_default_interval(cls):
        return 60 * 60 * 24  # 1 day


class Grid5kProcTotal(BaseGrid5000MetricPuller):

    metric_name = "proc_total"
    metric_type = "gauge"
    metric_unit = " "  # Number of processes

    @classmethod
    def get_default_interval(cls):
        return 60 * 60 * 24  # 1 day


# class Grid5kRcache(BaseGrid5000MetricPuller):

#     metric_name = "rcache"
#     metric_type = "gauge"
#     metric_unit = "%"

#     @classmethod
#     def get_default_interval(cls):
#         return 60 * 60 * 24  # 1 day


class Grid5kSwapFree(BaseGrid5000MetricPuller):

    metric_name = "swap_free"
    metric_type = "gauge"
    metric_unit = "KB"

    @classmethod
    def get_default_interval(cls):
        return 60 * 60 * 24  # 1 day


class Grid5kSwapTotal(BaseGrid5000MetricPuller):

    metric_name = "swap_total"
    metric_type = "gauge"
    metric_unit = "KB"

    @classmethod
    def get_default_interval(cls):
        return 60 * 60 * 24  # 1 day


class Grid5kSysClock(BaseGrid5000MetricPuller):

    metric_name = "sys_clock"
    metric_type = "gauge"
    metric_unit = "s"  # seconds

    @classmethod
    def get_default_interval(cls):
        return 60 * 60 * 24  # 1 day


# class Grid5kWcache(BaseGrid5000MetricPuller):

#     metric_name = "wcache"
#     metric_type = "gauge"
#     metric_unit = "%"

#     @classmethod
#     def get_default_interval(cls):
#         return 60 * 60 * 24  # 1 day


class Grid5kPdu(BaseGrid5000MetricPuller):

    metric_name = "pdu"
    metric_type = "gauge"
    metric_unit = "W"  # Watt

    @classmethod
    def get_default_interval(cls):
        return 60 * 60 * 24  # 1 day


class Grid5kPduShared(BaseGrid5000MetricPuller):

    metric_name = "pdu_shared"
    metric_type = "gauge"
    metric_unit = "W"  # Watt

    @classmethod
    def get_default_interval(cls):
        return 60 * 60 * 24  # 1 day


class Grid5kAmbientTemp(BaseGrid5000MetricPuller):

    metric_name = "ambient_temp"
    metric_type = "gauge"
    metric_unit = "degree celsius"

    @classmethod
    def get_default_interval(cls):
        return 60 * 60 * 24  # 1 day
