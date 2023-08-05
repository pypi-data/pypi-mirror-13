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
from watcher_metering_vsphere.tests._fixtures import FakePuller
from watcher_metering_vsphere.tests.base import BaseTestCase


class TestVSphereWrapper(BaseTestCase):

    @freeze_time("2015-08-04T15:15:45.703542+00:00")
    @patch("watcher_metering_vsphere.wrappers.vsphere.vim")
    @patch("watcher_metering_vsphere.wrappers.vsphere.connect")
    def test_pull_metrics(self, m_connect, m_vim):
        m_perf_manager = m_connect.SmartConnect().RetrieveContent().perfManager
        m_metric_id = Mock()
        m_metric_cls = m_vim.PerformanceManager.MetricId
        m_metric_cls.return_value = m_metric_id
        m_query_spec = m_vim.PerformanceManager.QuerySpec
        m_query_perf = m_perf_manager.QueryPerf
        dummy_timestamp = datetime.datetime.now()

        # Mock the counter mapping
        m_perf_manager.perfCounter = [
            Mock(
                rollupType="none",
                groupInfo=Mock(key="fake"),
                nameInfo=Mock(key="metric"),
                unitInfo=Mock(label="%"),
                key=1,  # metric_uid
                statsType="absolute",  # --> makes it a cumulative
            ),
        ]
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

        expected_metric = dict(
            metric_name="fake.metric",
            unit="%",
            timestamp=dummy_timestamp.isoformat(),
            type="cumulative",
            value=12.34,
            instance_id="instance_uuid",
            instance_name="instance_name",
            host_id="host_uuid",
            host_name="host_name",
        )

        data_puller = FakePuller(
            FakePuller.get_name(),
            FakePuller.get_default_probe_id(),
            FakePuller.get_default_interval(),
            datacenter="fake_vcenter_fqdn",
            username="fake_username",
            password="fake_password",
        )

        pulled_metrics = data_puller.wrapper.pull_metrics(
            metric_name="fake.metric",
            metric_group="vm",
            instance=m_instance,
        )

        m_query_spec.assert_called_once_with(
            maxSample=1,
            intervalId=20,
            entity=m_instance,
            metricId=[m_metric_id],
            startTime=None,
            endTime=None,
        )
        self.assertEqual(m_query_perf.call_count, 1)
        self.assertEqual(len(pulled_metrics), 1)
        self.assertEqual(
            expected_metric,
            pulled_metrics[0],
        )

    @freeze_time("2015-08-04T15:15:45.703542+00:00")
    @patch("watcher_metering_vsphere.wrappers.vsphere.vim")
    @patch("watcher_metering_vsphere.wrappers.vsphere.connect")
    def test_vsphere_get_all_vm_instances(self, m_connect, m_vim):
        m_service_instance = m_connect.SmartConnect()
        m_content = m_service_instance.RetrieveContent()
        m_perf_manager = m_content.perfManager
        m_metric_id = Mock()
        m_metric_cls = m_vim.PerformanceManager.MetricId
        m_metric_cls.return_value = m_metric_id

        # Mock the counter mapping
        m_perf_manager.perfCounter = [
            Mock(
                rollupType="none",
                groupInfo=Mock(key="fake"),
                nameInfo=Mock(key="metric"),
                unitInfo=Mock(label="%"),
                key=1,  # metric_uid
                statsType="absolute",  # --> makes it a cumulative
            ),
        ]

        m_instance1 = Mock(
            name="instance1_name",
            summary=Mock(vm=Mock(config=Mock(uuid="instance1_uuid"))),
            runtime=Mock(
                host=Mock(
                    name="host_name",
                    hardware=Mock(systemInfo=Mock(uuid="host_uuid")),
                )
            )
        )
        m_instance1.name = "instance1_name"
        m_instance1.runtime.host.name = "host_name"

        m_instance2 = Mock(
            name="instance2_name",
            summary=Mock(vm=Mock(config=Mock(uuid="instance2_uuid"))),
            runtime=Mock(
                host=Mock(
                    name="host_name",
                    hardware=Mock(systemInfo=Mock(uuid="host_uuid")),
                )
            )
        )
        m_instance2.name = "instance2_name"
        m_instance2.runtime.host.name = "host_name"

        m_dc = Mock(
            vmFolder=Mock(childEntity=[m_instance1, m_instance2])
        )
        m_content.rootFolder = Mock(childEntity=[m_dc])

        data_puller = FakePuller(
            FakePuller.get_name(),
            FakePuller.get_default_probe_id(),
            FakePuller.get_default_interval(),
            datacenter="fake_vcenter_fqdn",
            username="fake_username",
            password="fake_password",
        )

        # Action
        instances_gen = data_puller.wrapper.get_all_instances(
            data_puller.wrapper.VM_TYPE
        )
        instances = [inst for inst in instances_gen]

        self.assertEqual(
            [m_instance1, m_instance2],
            instances
        )

    @freeze_time("2015-08-04T15:15:45.703542+00:00")
    @patch("watcher_metering_vsphere.wrappers.vsphere.vim")
    @patch("watcher_metering_vsphere.wrappers.vsphere.connect")
    def test_vsphere_get_all_host_instances(self, m_connect, m_vim):
        m_service_instance = m_connect.SmartConnect()
        m_content = m_service_instance.RetrieveContent()
        m_perf_manager = m_content.perfManager
        m_metric_id = Mock()
        m_metric_cls = m_vim.PerformanceManager.MetricId
        m_metric_cls.return_value = m_metric_id

        # Mock the counter mapping
        m_perf_manager.perfCounter = [
            Mock(
                rollupType="none",
                groupInfo=Mock(key="fake"),
                nameInfo=Mock(key="metric"),
                unitInfo=Mock(label="%"),
                key=1,  # metric_uid
                statsType="absolute",  # --> makes it a cumulative
            ),
        ]

        m_instance1 = Mock(
            name="host_name",
            hardware=Mock(systemInfo=Mock(uuid="host_uuid")),
        )
        m_instance1.name = "instance1_name"
        m_instance1.runtime.host.name = "host_name"

        m_instance2 = Mock(
            name="host_name",
            hardware=Mock(systemInfo=Mock(uuid="host_uuid")),
        )
        m_instance2.name = "instance2_name"
        m_instance2.runtime.host.name = "host_name"

        m_dc = Mock(
            hostFolder=Mock(
                childEntity=[
                    Mock(host=[m_instance1]),
                    Mock(host=[m_instance2]),
                ],
            )
        )
        m_content.rootFolder = Mock(childEntity=[m_dc])

        data_puller = FakePuller(
            FakePuller.get_name(),
            FakePuller.get_default_probe_id(),
            FakePuller.get_default_interval(),
            datacenter="fake_vcenter_fqdn",
            username="fake_username",
            password="fake_password",
        )

        # Action
        instances_gen = data_puller.wrapper.get_all_instances(
            data_puller.wrapper.HOST_TYPE
        )
        instances = [inst for inst in instances_gen]

        self.assertEqual(
            [m_instance1, m_instance2],
            instances
        )
