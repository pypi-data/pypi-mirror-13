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

from collections import OrderedDict
import textwrap

from mock import Mock
from mock import patch
from watcher_metering_vsphere.commands import export_drivers
from watcher_metering_vsphere.commands import gen_drivers
from watcher_metering_vsphere.tests.base import BaseTestCase
from watcher_metering_vsphere.wrappers.vsphere import VSphereWrapper


class TestVSphereCommands(BaseTestCase):

    @patch.object(gen_drivers, "export_py")
    @patch.object(VSphereWrapper, "get_counter_mapping")
    @patch.object(gen_drivers, "parse_args")
    def test_generate_drivers_py(self, m_parse_args, m_get_counter_mapping,
                                 m_export_py):
        m_args = Mock()
        m_parse_args.return_value = m_args

        m_args.required_drivers = "Fake required_drivers"
        m_args.host = "Fake host"
        m_args.username = "Fake username"
        m_args.password = "Fake password"
        m_args.filepath = "fake_filepath.py"

        # Mock the counter mapping
        m_get_counter_mapping.return_value = {
            "dummy.driver": {
                "group": "dummy",
                "name": "driver",
                "unit": "dummy_unit",
                "type": "dummy_type",
                "uid": "21345",
                "description": "does not matter",
            },
        }

        gen_drivers.main()

        expected_vm_content = textwrap.dedent("""\
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
        from watcher_metering_vsphere.base import BaseVSphereMetricPuller

        LOG = log.getLogger(__name__)


        class VSphereVmDummyDriver(BaseVSphereMetricPuller):
            \"\"\"does not matter\"\"\"
            metric_group = "vm"
            metric_name = "dummy.driver"
            metric_type = "dummy_type"
            metric_unit = "dummy_unit"
            pulling_interval = 10
        """)

        expected_host_content = textwrap.dedent("""\
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
        from watcher_metering_vsphere.base import BaseVSphereMetricPuller

        LOG = log.getLogger(__name__)


        class VSphereHostDummyDriver(BaseVSphereMetricPuller):
            \"\"\"does not matter\"\"\"
            metric_group = "host"
            metric_name = "dummy.driver"
            metric_type = "dummy_type"
            metric_unit = "dummy_unit"
            pulling_interval = 10
        """)

        self.assertEqual(2, m_export_py.call_count)
        m_export_py.assert_any_call(
            expected_vm_content,
            "vm_fake_filepath.py",
        )
        m_export_py.assert_any_call(
            expected_host_content,
            "host_fake_filepath.py",
        )

    @patch.object(export_drivers, "export_csv")
    @patch.object(VSphereWrapper, "get_counter_mapping")
    @patch.object(export_drivers, "parse_args")
    def test_export_drivers_csv(self, m_parse_args, m_get_counter_mapping,
                                m_export_csv):
        m_args = Mock()
        m_parse_args.return_value = m_args

        m_args.required_drivers = "Fake required_drivers"
        m_args.host = "Fake host"
        m_args.username = "Fake username"
        m_args.password = "Fake password"
        m_args.filepath = "fake_filepath.csv"

        # Mock the counter mapping
        m_get_counter_mapping.return_value = {
            "dummy.driver": {
                "group": "dummy",
                "name": "driver",
                "unit": "dummy_unit",
                "type": "dummy_type",
                "uid": "21345",
                "description": "does not matter",
            },
        }

        export_drivers.main()

        expected_vm_content = [{
            "metric_unit": "dummy_unit",
            "metric_type": "dummy_type",
            "wm_name": "vsphere_vm_dummy_driver",
            "metric_description": "does not matter",
            "metric_name": "dummy.driver"
        }]
        expected_vm_headers = OrderedDict(
            [("wm_name", "Metric name"),
             ("metric_name", "vSphere Metric name"),
             ("metric_unit", "Metric unit"),
             ("metric_type", "Metric type"),
             ("entity", "Entity"),
             ("metric_description", "Description")]
        )
        expected_host_content = [{
            "metric_unit": "dummy_unit",
            "metric_type": "dummy_type",
            "wm_name": "vsphere_host_dummy_driver",
            "metric_description": "does not matter",
            "metric_name": "dummy.driver"
        }]
        expected_host_headers = OrderedDict(
            [("wm_name", "Metric name"),
             ("metric_name", "vSphere Metric name"),
             ("metric_unit", "Metric unit"),
             ("metric_type", "Metric type"),
             ("entity", "Entity"),
             ("metric_description", "Description")]
        )

        # assertions
        self.assertEqual(2, m_export_csv.call_count)
        m_export_csv.assert_any_call(
            expected_vm_content,
            expected_vm_headers,
            "vm_fake_filepath.csv",
        )
        m_export_csv.assert_any_call(
            expected_host_content,
            expected_host_headers,
            "host_fake_filepath.csv",
        )
