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

import argparse
from collections import OrderedDict
import csv
import os
import re

from oslo_log import log
from watcher_metering_vsphere.tests._fixtures import FakePuller

LOG = log.getLogger(__name__)


def parse_args(default_filepath=""):
    parser = argparse.ArgumentParser(
        description='Generates CSV table containing information '
                    'about each desired/implemented driver'
    )
    # parser.add_argument(
    #     '--drivers',
    #     dest='required_drivers',
    #     required=True,
    #     help='JSON file containing the list of drivers to generate'
    # )
    parser.add_argument(
        '--vsphere',
        dest='host',
        default="10.10.255.115",
        help='vSphere FQDN or IP address'
    )
    parser.add_argument(
        '--username',
        dest='username',
        default="Administrator@vsphere.local",
        help='vSphere username'
    )
    parser.add_argument(
        '--password',
        dest='password',
        default="R00troot!",
        help='vSphere password'
    )
    parser.add_argument(
        '--format', default="csv",  # or rst
        help='filepath of the output'
    )
    parser.add_argument(
        'filepath', default=default_filepath,
        help='filepath of the output'
    )

    args = parser.parse_args()
    return args


def export_csv(data, headers, filepath):
    print("Exporting to %s ..." % filepath)
    csv_data = [{headers[k]: v for k, v in row.items()} for row in data]
    keys = headers.values()
    with open(filepath, 'w') as output_file:
        dict_writer = csv.DictWriter(output_file, keys)
        dict_writer.writeheader()
        dict_writer.writerows(csv_data)


def get_data_puller(args):
    data_puller = FakePuller(
        FakePuller.get_name(),
        FakePuller.get_default_probe_id(),
        FakePuller.get_default_interval(),
        datacenter=args.host,
        username=args.username,
        password=args.password,
    )
    return data_puller

# def get_drivers_list(filepath):
#     with open(filepath) as drivers_file:
#         required_drivers = json.load(drivers_file)
#     return required_drivers


def convert(name):
    s1 = re.sub('(.)([A-Z][a-z]+)', r'\1_\2', name)
    return re.sub('([a-z0-9])([A-Z])', r'\1_\2', s1).lower()


def generate_csv_export_data(prefix, drivers, args):
    mapping = get_data_puller(args).wrapper.get_counter_mapping()
    data = []
    for vsphere_metric_name in drivers:
        metric_metadata = mapping[vsphere_metric_name]
        watcher_metering_name = "vsphere_{prefix}_{metric_name}".format(
            prefix=prefix,
            metric_name=convert(vsphere_metric_name.replace(".", "_")),
        )
        row = dict(
            wm_name=watcher_metering_name,
            metric_type=metric_metadata["type"],
            metric_name=vsphere_metric_name,
            metric_unit=metric_metadata["unit"],
            metric_description=metric_metadata["description"],
        )
        data.append(row)

    return data


def main():
    default_filepath = os.path.join(os.getcwd(), "drivers.csv")
    args = parse_args(default_filepath)

    data_puller = get_data_puller(args)

    mapping = data_puller.wrapper.get_counter_mapping()

    # required_drivers = get_drivers_list(args.required_drivers)
    required_drivers = sorted(mapping.keys())  # all of them

    # old column name --> new vSphere name
    headers_mapping = OrderedDict([
        ("wm_name", "Metric name"),
        ("metric_name", "vSphere Metric name"),
        ("metric_unit", "Metric unit"),
        ("metric_type", "Metric type"),
        ("entity", "Entity"),
        ("metric_description", "Description"),
    ])
    prefixes = ["vm", "host"]
    for prefix in prefixes:
        data = generate_csv_export_data(prefix, required_drivers, args)
        export_csv(data, headers_mapping, "_".join([prefix, args.filepath]))

    print("Done.")

if __name__ == '__main__':
    main()
