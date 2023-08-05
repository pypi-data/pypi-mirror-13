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

from hashlib import md5
import re

from oslo_config import cfg
from oslo_log import log
from watcher_metering.agent.measurement import Measurement
from watcher_metering.agent.puller import MetricPuller
from watcher_metering_vsphere.wrappers.vsphere import VSphereWrapper

LOG = log.getLogger(__name__)


class BaseVSphereMetricPuller(MetricPuller):

    metric_group = NotImplemented  # either 'vm' or 'host'
    metric_name = NotImplemented  # Should be contained in the above list
    metric_type = NotImplemented
    metric_unit = NotImplemented
    pulling_interval = NotImplemented

    def __init__(self, title, probe_id, interval,
                 datacenter, username, password):
        super(BaseVSphereMetricPuller, self).__init__(
            title=title,
            probe_id=probe_id,
            interval=interval,
        )
        self._datacenter = datacenter
        self.wrapper = VSphereWrapper(
            host=self._datacenter,
            username=username,
            password=password,
        )

    @classmethod
    def convert(cls, name):
        s1 = re.sub('(.)([A-Z][a-z]+)', r'\1_\2', name)
        return re.sub('([a-z0-9])([A-Z])', r'\1_\2', s1).lower()

    @classmethod
    def get_normalized_name(cls):
        return cls.convert(cls.metric_name.replace(".", "_"))

    @classmethod
    def get_name(cls):
        return "vsphere_{group}_{name}".format(
            group=cls.metric_group,
            name=cls.get_normalized_name(),
        )

    @classmethod
    def get_default_probe_id(cls):
        return "vsphere.{group}.{name}".format(
            group=cls.metric_group,
            name=cls.get_normalized_name(),
        )

    @classmethod
    def get_metric_type(cls):
        # either 'gauge', 'cumulative' or 'delta'
        return cls.metric_type

    @classmethod
    def get_default_interval(cls):
        return cls.pulling_interval  # In seconds

    @property
    def unit(self):
        return self.metric_unit

    @classmethod
    def get_config_opts(cls):
        return cls.get_base_opts() + [
            cfg.StrOpt(
                'datacenter',
                help='vSphere datacenter FQDN or IP address'),
            cfg.StrOpt(
                'username',
                help='vSphere username (make sure the account '
                     'has the proper permissions)'),
            cfg.StrOpt(
                'password',
                secret=True,
                help='vSphere password'),
        ]

    @classmethod
    def validate(cls, measurement):
        """Should make some assertions to make sure the value is correct
        :raises: AssertionError
        """
        assert measurement
        assert measurement.unit == cls.metric_unit
        assert measurement.type == cls.metric_type

    def do_pull(self):
        LOG.info("[%s] Pulling measurements...", self.key)
        for instance in self.wrapper.get_all_instances(self.metric_group):
            LOG.info(
                "[%s] Running metric collection on instance %s ",
                self.key, instance
            )
            try:
                raw_measurements = self.wrapper.pull_metrics(
                    metric_name=self.metric_name,
                    metric_group=self.metric_group,
                    instance=instance,
                )
                LOG.debug("[%s] Formatting measurement...", self.key)
                for raw_measurement in raw_measurements:
                    measurement = self.format_measurement(raw_measurement)
                    # Sends the measurements explicitly now
                    self.send_measurements([measurement])
            except KeyError as exc:
                LOG.debug("[%s] Metric not available", self.metric_name)
            except Exception as exc:
                LOG.exception(exc)
            else:
                LOG.info(
                    "[%s] Probed all VMs from `%s`", self.key, self._datacenter
                )

        # We return an empty list because we want to send the data as we go
        # to avoid having to send a too large set at the end (avoid a spike).
        return []

    def format_measurement(self, raw_measurement):
        try:
            resource_metadata = {
                "host": raw_measurement["host_id"],
                "host_name": raw_measurement["host_name"],
                "title": self.title,
                "resource_name": raw_measurement["instance_name"],
            }

            measurement = self.anonymize_measurement(
                name=self.probe_id,
                unit=self.unit,
                type_=raw_measurement["type"],
                value=raw_measurement["value"],
                resource_id=raw_measurement["instance_id"],
                timestamp=raw_measurement["timestamp"],
                host=raw_measurement["host_id"],
                resource_metadata=resource_metadata,
            )
            self.validate(measurement)
            # Adds the measurements if it has been validated
            return measurement
        except Exception as exc:
            LOG.exception(exc)

    def anonymize_measurement(self, name, unit, type_, value,
                              resource_id, host=None, timestamp=None,
                              resource_metadata=None):
        anonymized_metadata = dict()
        if resource_metadata:
            keys_to_anonymize = ["host", "host_name", "resource_name"]
            anonymized_metadata = resource_metadata.copy()

            for key in keys_to_anonymize:
                if key in resource_metadata.keys():
                    anonymized_metadata.pop(key)
                    anonymized_metadata[key] = \
                        self._hash_value(resource_metadata[key])

        anonymized_measurement = Measurement(
            name=name,
            unit=unit,
            type_=type_,
            value=value,
            resource_id=self._hash_value(resource_id),
            timestamp=timestamp,
            host=self._hash_value(host),
            resource_metadata=anonymized_metadata,
        )
        return anonymized_measurement

    def _hash_value(self, value):
        hashed_value = value
        if value is not None:
            hash_function = md5()
            hash_function.update(value)
            hashed_value = hash_function.hexdigest()
        return hashed_value
