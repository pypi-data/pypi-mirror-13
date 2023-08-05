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


from mock import MagicMock
from mock import patch
from watcher_metering.agent.measurement import Measurement
from watcher_metering.agent.puller import MetricPuller

from watcher_metering_vsphere.tests._fixtures import FakePuller
from watcher_metering_vsphere.tests.base import BaseTestCase
from watcher_metering_vsphere.wrappers.vsphere import VSphereWrapper


class TestVSphereBase(BaseTestCase):

    @patch("watcher_metering_vsphere.base.md5")
    def test_format_vsphere_measurement(self, md5_mock):

        hexdigest_mock = md5_mock.return_value.hexdigest
        hexdigest_mock.side_effect = ["fake_host_uuid", "fake_host_name",
                                      "fake_host_name", "fake_instance_uuid",
                                      "fake_host_name"]

        data_puller = FakePuller(
            FakePuller.get_name(),
            FakePuller.get_default_probe_id(),
            FakePuller.get_default_interval(),
            datacenter="fake_vcenter_fqdn",
            username="fake_username",
            password="fake_password",
        )

        expected_measurement = Measurement(
            name="vsphere.vm.fake_metric",
            unit="fake_unit",
            type_="gauge",
            value=12.34,
            resource_id="fake_instance_uuid",
            host="fake_host_name",
            timestamp="2015-08-03T15:15:45+00:00",
            resource_metadata={
                "host": "fake_host_uuid",
                "title": "vsphere_vm_fake_metric",
                "resource_name": "fake_host_name",
                "host_name": "fake_host_name",
                },
        )

        raw_measurement = dict(
            metric_name="fake_metric",
            unit="fake_unit",
            timestamp="2015-08-03T15:15:45+00:00",
            type="gauge",
            value=12.34,
            instance_id="fake_instance_uuid",
            instance_name="fake_instance_name",
            host_id="fake_host_uuid",
            host_name="fake_host_name",
        )

        formatted_measurement = data_puller.format_measurement(raw_measurement)
        self.assertEqual(
            expected_measurement.as_dict(),
            formatted_measurement.as_dict(),
        )

    @patch("watcher_metering_vsphere.base.md5")
    @patch.object(MetricPuller, "send_measurements")
    @patch.object(VSphereWrapper, "get_all_instances")
    @patch.object(VSphereWrapper, "pull_metrics")
    def test_vsphere_do_pull(self, m_pull_metrics, m_get_all_instances,
                             m_send_measurements, md5_mock):
        m_get_all_instances.return_value = [MagicMock()]
        m_pull_metrics.return_value = [dict(
            metric_name="fake_metric",
            unit="fake_unit",
            timestamp="2015-08-03T15:15:45+00:00",
            type="gauge",
            value=12.34,
            instance_id="fake_instance_uuid",
            instance_name="fake_instance_name",
            host_id="fake_instance_uuid",
            host_name="fake_host_name",
        )]

        hexdigest_mock = md5_mock.return_value.hexdigest
        hexdigest_mock.side_effect = ["fake_host_uuid", "fake_host_name",
                                      "fake_instance_name",
                                      "fake_instance_uuid",
                                      "fake_host_uuid"]

        expected_measurement = Measurement(
            name="vsphere.vm.fake_metric",
            unit="fake_unit",
            type_="gauge",
            value=12.34,
            resource_id="fake_instance_uuid",
            host="fake_host_uuid",
            timestamp="2015-08-03T15:15:45+00:00",
            resource_metadata={
                "host": "fake_host_uuid",
                "title": "vsphere_vm_fake_metric",
                "resource_name": "fake_instance_name",
                "host_name": "fake_host_name",
                },
        )

        data_puller = FakePuller(
            FakePuller.get_name(),
            FakePuller.get_default_probe_id(),
            FakePuller.get_default_interval(),
            datacenter="fake_vcenter_fqdn",
            username="fake_username",
            password="fake_password",
        )

        # Action under test
        data_puller.do_pull()

        # Assertions
        self.assertEqual(1, m_send_measurements.call_count)
        sent_measurements = m_send_measurements.call_args[0][0]
        self.assertEqual(1, len(sent_measurements))
        self.assertEqual(
            expected_measurement.as_dict(),
            sent_measurements[0].as_dict(),
        )
