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

from freezegun import freeze_time
from mock import Mock
from mock import patch
from watcher_metering.agent.measurement import Measurement
from watcher_metering.agent.puller import MetricPuller

from watcher_metering_vsphere.opts import DRIVERS
from watcher_metering_vsphere.tests.base import BaseTestCase
from watcher_metering_vsphere.wrappers.vsphere import VSphereWrapper


class TestVSphereVmDrivers(BaseTestCase):

    scenarios = [
        (
            "Test --> %s" % str(drivers_cls), {
                "metric_puller_cls": drivers_cls,
                "counter_full_name": drivers_cls.metric_name,
                "counter_group": drivers_cls.metric_name.split(".")[0],
                "counter_name": drivers_cls.metric_name.split(".")[1],
                "metric_group": drivers_cls.metric_group,
                "metric_name": drivers_cls.get_normalized_name(),
                "metric_unit": drivers_cls.metric_unit,
                "metric_type": drivers_cls.metric_type,
            }
        )
        for drivers_cls in DRIVERS
        if drivers_cls.metric_group == VSphereWrapper.VM_TYPE
    ]

    @patch("watcher_metering_vsphere.base.md5")
    @freeze_time("2015-08-04T15:15:45.703542+00:00")
    @patch.object(MetricPuller, "send_measurements")
    @patch.object(VSphereWrapper, "get_counter_mapping")
    @patch.object(VSphereWrapper, "get_all_instances")
    @patch("watcher_metering_vsphere.wrappers.vsphere.vim")
    @patch("watcher_metering_vsphere.wrappers.vsphere.connect")
    def test_vsphere_pull_vm(self, m_connect, m_vim,
                             m_get_all_instances,
                             m_get_counter_mapping,
                             m_send_measurements,
                             md5_mock):
        m_perf_manager = m_connect.SmartConnect().RetrieveContent().perfManager
        m_metric_id = Mock()
        m_metric_cls = m_vim.PerformanceManager.MetricId
        m_metric_cls.return_value = m_metric_id
        m_query_perf = m_perf_manager.QueryPerf
        dummy_timestamp = datetime.datetime.now()

        # Mock the counter mapping
        m_get_counter_mapping.return_value = {
            self.counter_full_name: {
                "group": self.counter_group,
                "name": self.counter_name,
                "unit": self.metric_unit,
                "type": self.metric_type,
                "uid": "does not matter",
            },
        }
        m_instance = Mock(
            name="instance_name",
            summary=Mock(vm=Mock(config=Mock(uuid="instance_uuid"))),
            runtime=Mock(
                host=Mock(
                    name="host_name",
                    hardware=Mock(systemInfo=Mock(uuid="host_uuid")),
                )
            )
        )
        m_instance.name = "instance_name"
        m_instance.runtime.host.name = "host_name"
        m_get_all_instances.return_value = [m_instance]

        m_query_perf.return_value = [
            Mock(  # Sample
                value=[
                    Mock(  # Serie
                        value=[12.34]  # Actual value
                    ),
                ],
                sampleInfo=[Mock(timestamp=dummy_timestamp)]
            ),
        ]

        hexdigest_mock = md5_mock.return_value.hexdigest
        hexdigest_mock.side_effect = ["host_uuid", "host_name",
                                      "instance_name", "instance_uuid",
                                      "host_uuid"]

        expected_measurement = Measurement(
            name="vsphere.%s.%s" % (self.metric_group, self.metric_name),
            unit=self.metric_unit,
            type_=self.metric_type,
            value=12.34,
            resource_id="instance_uuid",
            timestamp=dummy_timestamp.isoformat(),
            host="host_uuid",
            resource_metadata={
                "host": "host_uuid",
                "host_name": "host_name",
                "title": "vsphere_%s_%s" % (
                    self.metric_group, self.metric_name
                ),
                "resource_name": "instance_name",
            },
        )

        # Action
        data_puller = self.metric_puller_cls(
            self.metric_puller_cls.get_name(),
            self.metric_puller_cls.get_default_probe_id(),
            self.metric_puller_cls.get_default_interval(),
            datacenter="fake_vcenter_fqdn",
            username="fake_username",
            password="fake_password",
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


class TestVSphereHostDrivers(BaseTestCase):

    scenarios = [
        (
            "Test --> %s" % str(drivers_cls), {
                "metric_puller_cls": drivers_cls,
                "counter_full_name": drivers_cls.metric_name,
                "counter_group": drivers_cls.metric_name.split(".")[0],
                "counter_name": drivers_cls.metric_name.split(".")[1],
                "metric_group": drivers_cls.metric_group,
                "metric_name": drivers_cls.get_normalized_name(),
                "metric_unit": drivers_cls.metric_unit,
                "metric_type": drivers_cls.metric_type,
            }
        )
        for drivers_cls in DRIVERS
        if drivers_cls.metric_group == VSphereWrapper.HOST_TYPE
    ]

    @patch("watcher_metering_vsphere.base.md5")
    @freeze_time("2015-08-04T15:15:45.703542+00:00")
    @patch.object(MetricPuller, "send_measurements")
    @patch.object(VSphereWrapper, "get_counter_mapping")
    @patch.object(VSphereWrapper, "get_all_instances")
    @patch("watcher_metering_vsphere.wrappers.vsphere.vim")
    @patch("watcher_metering_vsphere.wrappers.vsphere.connect")
    def test_vsphere_pull_host(self, m_connect, m_vim,
                               m_get_all_instances,
                               m_get_counter_mapping,
                               m_send_measurements,
                               md5_mock):
        m_perf_manager = m_connect.SmartConnect().RetrieveContent().perfManager
        m_metric_id = Mock()
        m_metric_cls = m_vim.PerformanceManager.MetricId
        m_metric_cls.return_value = m_metric_id
        m_query_perf = m_perf_manager.QueryPerf
        dummy_timestamp = datetime.datetime.now()

        # Mock the counter mapping
        m_get_counter_mapping.return_value = {
            self.counter_full_name: {
                "group": self.counter_group,
                "name": self.counter_name,
                "unit": self.metric_unit,
                "type": self.metric_type,
                "uid": "does not matter",
            },
        }
        m_instance = Mock(
            name="host_name",
            hardware=Mock(systemInfo=Mock(uuid="host_uuid")),
        )
        m_instance.name = "host_name"

        m_get_all_instances.return_value = [m_instance]

        m_query_perf.return_value = [
            Mock(  # Sample
                value=[
                    Mock(  # Serie
                        value=[12.34]  # Actual value
                    ),
                ],
                sampleInfo=[Mock(timestamp=dummy_timestamp)]
            ),
        ]

        hexdigest_mock = md5_mock.return_value.hexdigest
        hexdigest_mock.side_effect = ["host_uuid", "host_name", "host_name",
                                      "host_uuid", "host_uuid"]

        expected_measurement = Measurement(
            name="vsphere.%s.%s" % (self.metric_group, self.metric_name),
            unit=self.metric_unit,
            type_=self.metric_type,
            value=12.34,
            resource_id="host_uuid",
            timestamp=dummy_timestamp.isoformat(),
            host="host_uuid",
            resource_metadata={
                "host": "host_uuid",
                "host_name": "host_name",
                "title": "vsphere_%s_%s" % (
                    self.metric_group, self.metric_name
                ),
                "resource_name": "host_name",
            },
        )

        # Action
        data_puller = self.metric_puller_cls(
            self.metric_puller_cls.get_name(),
            self.metric_puller_cls.get_default_probe_id(),
            self.metric_puller_cls.get_default_interval(),
            datacenter="fake_vcenter_fqdn",
            username="fake_username",
            password="fake_password",
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
