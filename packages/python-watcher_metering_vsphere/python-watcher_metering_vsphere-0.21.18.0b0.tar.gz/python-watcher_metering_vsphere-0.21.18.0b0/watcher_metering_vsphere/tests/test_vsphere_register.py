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

import types

from mock import MagicMock
from mock import patch
from oslo_config import cfg
from oslo_config.fixture import Config as OsloConfigFixture
from watcher_metering.agent.agent import Agent
from watcher_metering.agent.loader import DriverLoader
from watcher_metering_vsphere.opts import DRIVERS
from watcher_metering_vsphere.tests.base import BaseTestCase


class TestDriverRegistration(BaseTestCase):

    # patches to be applied for each test in this test suite
    patches = []

    TESTED_DRIVERS = DRIVERS[-10:] + DRIVERS[:10]

    def setUp(self):
        super(TestDriverRegistration, self).setUp()
        self.conf = cfg.ConfigOpts()
        self.cfg_fixture = OsloConfigFixture(self.conf)
        self._load_config_data()
        self.useFixture(self.cfg_fixture)

        def _fake_parse(self, args=[]):
            return cfg.ConfigOpts._parse_cli_opts(self, [])

        _fake_parse_method = types.MethodType(_fake_parse, self.conf)
        self.conf._parse_cli_opts = _fake_parse_method

        # Patches the agent socket
        self.m_agent_socket = MagicMock(autospec=True)

        self.patches.extend([
            # Deactivates the nanomsg socket
            patch(
                "watcher_metering.agent.agent.nanomsg.Socket",
                new=self.m_agent_socket,
            ),
            patch.object(DriverLoader, "_reload_config", MagicMock()),
        ])

        # Applies all of our patches before each test
        for _patch in self.patches:
            _patch.start()

    def tearDown(self):
        super(TestDriverRegistration, self).tearDown()
        # The drivers are stored at the class level so we need to clear
        # it after each test
        for _patch in self.patches:
            _patch.stop()

    scenarios = [
        # This is enough for most drivers but
        # we still needs to pre-configure the extra params by hand
        (driver_cls.get_name(), {"driver_cls": driver_cls})
        for driver_cls in TESTED_DRIVERS
    ]

    def _load_config_data(self):
        for vsphere_driver in self.TESTED_DRIVERS:
            # pdu_servers=PDU_1:127.0.0.1,PDU_2:192.168.1.1
            self.cfg_fixture.load_raw_values(
                group=vsphere_driver.get_entry_name(),
                datacenter="fake_dc",
                username="dummy_username",
                password="dummy_password",
            )

    def test_register_metering_drivers(self):
        # Try to register/load each one of the driver using the Agent
        agent = Agent(
            conf=self.conf,
            driver_names=[self.driver_cls.get_name()],
            use_nanoconfig_service=False,
            publisher_endpoint="fake",
            nanoconfig_service_endpoint="",
            nanoconfig_update_endpoint="",
            nanoconfig_profile="nanoconfig://test_profile"
        )
        # Because it seems it does not clear from previous scenarios
        agent.drivers.clear()
        agent.register_drivers()

        self.assertEqual(
            sorted(agent.drivers.keys()),
            ["%s_%s" % (self.driver_cls.get_entry_name(),
                        self.driver_cls.get_default_probe_id())]
        )
