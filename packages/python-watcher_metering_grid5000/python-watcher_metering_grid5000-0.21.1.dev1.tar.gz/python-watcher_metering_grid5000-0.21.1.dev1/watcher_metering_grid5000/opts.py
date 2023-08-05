# -*- encoding: utf-8 -*-
# Copyright 2014
# The Cloudscaling Group, Inc.
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
# http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or
# implied.
# See the License for the specific language governing permissions and
# limitations under the License.

from watcher_metering_grid5000 import drivers as grid5000

GRID5000_DRIVERS = [
    grid5000.Grid5kBoottime,
    # grid5000.Grid5kBreadSec,
    # grid5000.Grid5kBwriteSec,
    grid5000.Grid5kBytesIn,
    grid5000.Grid5kBytesOut,
    grid5000.Grid5kCpuAidle,
    # grid5000.Grid5kCpuArm,
    # grid5000.Grid5kCpuAvm,
    grid5000.Grid5kCpuIdle,
    # grid5000.Grid5kCpuIntr,
    grid5000.Grid5kCpuNice,
    grid5000.Grid5kCpuNum,
    # grid5000.Grid5kCpuRm,
    grid5000.Grid5kCpuSpeed,
    # grid5000.Grid5kCpuSsys,
    grid5000.Grid5kCpuSystem,
    grid5000.Grid5kCpuUser,
    # grid5000.Grid5kCpuVm,
    # grid5000.Grid5kCpuWait,
    # grid5000.Grid5kCpuWio,
    grid5000.Grid5kDiskFree,
    grid5000.Grid5kDiskTotal,
    grid5000.Grid5kLoadFifteen,
    grid5000.Grid5kLoadFive,
    grid5000.Grid5kLoadOne,
    grid5000.Grid5kLocation,
    # grid5000.Grid5kLreadSec,
    # grid5000.Grid5kLwriteSec,
    grid5000.Grid5kMachineType,
    grid5000.Grid5kMemBuffers,
    grid5000.Grid5kMemCached,
    grid5000.Grid5kMemFree,
    grid5000.Grid5kMemShared,
    grid5000.Grid5kMemSreclaimable,
    grid5000.Grid5kMemTotal,
    grid5000.Grid5kMtu,
    grid5000.Grid5kOsName,
    grid5000.Grid5kOsRelease,
    grid5000.Grid5kPartMaxUsed,
    # grid5000.Grid5kPhreadSec,
    # grid5000.Grid5kPhwriteSec,
    grid5000.Grid5kPktsIn,
    grid5000.Grid5kPktsOut,
    grid5000.Grid5kProcRun,
    grid5000.Grid5kProcTotal,
    # grid5000.Grid5kRcache,
    grid5000.Grid5kSwapFree,
    grid5000.Grid5kSwapTotal,
    grid5000.Grid5kSysClock,
    # grid5000.Grid5kWcache,
    grid5000.Grid5kPdu,
    grid5000.Grid5kPduShared,
    grid5000.Grid5kAmbientTemp,
]


DRIVERS = GRID5000_DRIVERS


def list_opts():
    drivers_opts = [
        (driver.get_entry_name(), driver.get_config_opts())
        for driver in DRIVERS
        ]
    return drivers_opts
