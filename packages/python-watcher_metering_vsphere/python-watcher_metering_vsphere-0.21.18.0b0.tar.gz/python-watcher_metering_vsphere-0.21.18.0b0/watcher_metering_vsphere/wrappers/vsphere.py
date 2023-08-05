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
import itertools

from oslo_log import log
from pyVim import connect
from pyVmomi import vim
import requests
import ssl

LOG = log.getLogger(__name__)


class VSphereWrapper(object):

    VM_TYPE = "vm"
    HOST_TYPE = "host"

    def __init__(self, host, username, password, port=443):
        self.host = host
        self.username = username
        self.password = password
        self.port = port
        self.service_instance = None  # initialized with connect()
        self._counter_mapping = {}  # initialized with get_counter_mapping()
        requests.packages.urllib3.disable_warnings()

    def connect(self):

        context = ssl._create_unverified_context()
        context.verify_mode = ssl.CERT_NONE

        self.service_instance = connect.SmartConnect(
            host=self.host,
            user=self.username,
            pwd=self.password,
            port=int(self.port),
            sslContext=context
        )
        if not self.service_instance:
            raise IOError(
                "Could not connect to the specified host using specified "
                "username and password"
            )

    def get_content(self):
        if not self.service_instance:
            self.connect()
        content = self.service_instance.RetrieveContent()

        return content

    def get_datacenters(self):
        children = self.get_content().rootFolder.childEntity
        return (dc for dc in children if hasattr(dc, 'vmFolder'))

    def _get_all_vms(self):
        return (
            vm for vm in
            itertools.chain.from_iterable(
                dc.vmFolder.childEntity for dc in self.get_datacenters()
            )
        )

    def _get_all_hosts(self):
        compute_resources = itertools.chain.from_iterable(
            dc.hostFolder.childEntity for dc in self.get_datacenters()
        )
        hosts = itertools.chain.from_iterable(
            resource.host for resource in compute_resources
        )
        return hosts

    def get_all_instances(self, group):
        try:
            if group == self.VM_TYPE:
                # VMs
                return self._get_all_vms()
            else:
                # Hosts
                return self._get_all_hosts()
        except Exception as exc:
            LOG.exception(exc)
        return []

    def get_perf_manager(self):
        return self.get_content().perfManager

    def get_event_manager(self):
        return self.get_content().eventManager

    def get_counter_mapping(self):
        mapping = self._counter_mapping

        if mapping:
            return mapping

        perf_manager = self.get_perf_manager()
        metrics = perf_manager.perfCounter
        for metric in metrics:
            _rollup_type = str(metric.rollupType)
            rollup_type = _rollup_type if _rollup_type != 'none' else None
            parts = [metric.groupInfo.key, metric.nameInfo.key, rollup_type]
            metric_name = ".".join([part for part in parts if part])

            # `absolute` == cumulative but `delta` and `rate` are gauge
            # See https://pubs.vmware.com/vsphere-60/index.jsp#
            #   com.vmware.wssdk.apiref.doc/
            #   vim.PerformanceManager.CounterInfo.StatsType.html
            raw_type = metric.statsType

            infered_type = ""
            if raw_type == "rate":
                infered_type = "gauge"
            elif raw_type == "absolute":
                infered_type = "cumulative"
            elif raw_type == "delta":
                infered_type = "delta"

            mapping[metric_name] = {
                "group": metric.groupInfo.key,
                "name": metric.nameInfo.key,
                "description": metric.nameInfo.summary,
                "unit": metric.unitInfo.label,
                "uid": metric.key,
                "type": infered_type,
            }

        return mapping

    def get_metric_metadata(self, metric_name):
        counter_mapping = self.get_counter_mapping()
        if metric_name not in counter_mapping:
            raise KeyError("The metric does not exist or is not available!")
        metric_metadata = counter_mapping[metric_name]

        return metric_metadata

    def _prepare_query(self, metric_name, instance, interval,
                       start_time, end_time):
        metric_metadata = self.get_metric_metadata(metric_name)
        metric_id = vim.PerformanceManager.MetricId(
            counterId=metric_metadata["uid"],
            instance="*"
        )
        return vim.PerformanceManager.QuerySpec(
            maxSample=1,  # Only returns the latest value
            intervalId=interval,  # In seconds
            entity=instance,
            metricId=[metric_id],  # Takes a list of MetricId objects
            startTime=start_time,
            endTime=end_time,
        )

    def pull_events(self):
        end_time = datetime.datetime.now()
        start_time = end_time - datetime.timedelta(days=1)

        event_manager = self.get_event_manager()

        time_filter = vim.event.EventFilterSpec.ByTime(
            beginTime=start_time,
            endTime=datetime.datetime.now()
        )
        query_filter = vim.event.EventFilterSpec(time=time_filter)

        result = event_manager.QueryEvents(query_filter)

        # events = []
        # for raw_event in result:
        #     event_timestamp = raw_event.createdTime.isoformat()
        #     chainId
        #     changeTag
        #     computeResource
        #     datacenter = raw_event.datacenter
        #     ds
        #     dvs
        #     fullFormattedMessage
        #     host
        #     key
        #     net
        #     userName
        #     vm

        return result

    def _format_host_measurement(self, metric_name, instance, metric_value,
                                 metric_timestamp):
        metric_metadata = self.get_metric_metadata(metric_name)
        raw_measurement = dict(
            metric_name=metric_name,
            unit=metric_metadata["unit"],
            timestamp=metric_timestamp,
            type=metric_metadata["type"],
            value=metric_value,
            instance_id=instance.hardware.systemInfo.uuid,
            instance_name=instance.name,
            host_id=instance.hardware.systemInfo.uuid,
            host_name=instance.name,
        )
        return raw_measurement

    def _format_vm_measurement(self, metric_name, instance, metric_value,
                               metric_timestamp):
        metric_metadata = self.get_metric_metadata(metric_name)
        raw_measurement = dict(
            metric_name=metric_name,
            unit=metric_metadata["unit"],
            timestamp=metric_timestamp,
            type=metric_metadata["type"],
            value=metric_value,
            instance_id=instance.summary.vm.config.uuid,
            instance_name=instance.name,
            host_id=instance.runtime.host.hardware.systemInfo.uuid,
            host_name=instance.runtime.host.name,
        )
        return raw_measurement

    def extract_raw_measurements(self, metric_name, metric_group,
                                 instance, result):
        raw_measurements = []
        for sample in result:
            timestamp = sample.sampleInfo[0].timestamp.isoformat()
            for metric_serie in sample.value:
                for metric_value in metric_serie.value:
                    if metric_group == self.VM_TYPE:
                        raw_measurement = self._format_vm_measurement(
                            metric_name, instance, metric_value, timestamp,
                        )
                    else:
                        raw_measurement = self._format_host_measurement(
                            metric_name, instance, metric_value, timestamp,
                        )
                    if raw_measurement:
                        raw_measurements.append(raw_measurement)
        return raw_measurements

    def pull_metrics(self, metric_name, metric_group, instance, interval=20,
                     start_time=None, end_time=None):
        raw_measurements = []
        try:
            query = self._prepare_query(
                metric_name=metric_name,
                instance=instance,
                interval=interval,
                start_time=start_time,
                end_time=end_time,
            )
            # Returns a list of samples
            result = self.get_perf_manager().QueryPerf(querySpec=[query])
            if len(result):
                raw_measurements.extend(self.extract_raw_measurements(
                    metric_name, metric_group, instance, result,
                ))
            else:
                raise ValueError("Should have retrieved some data here...")
        except ValueError as exc:
            LOG.exception(exc)
            LOG.error("No metric retrieved! --> Expected at least 1 value.")
        except Exception as exc:
            LOG.exception(exc)
        return raw_measurements
