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
import os

from oslo_log import log
from watcher_metering_vsphere.tests._fixtures import FakePuller

LOG = log.getLogger(__name__)


header = """# -*- encoding: utf-8 -*-
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
"""

template = """
{metric_cls_signature}
    {metric_description}
    metric_group = "{metric_group}"
    metric_name = "{metric_name}"
    metric_type = "{metric_type}"
    metric_unit = "{metric_unit}"
    pulling_interval = 10
"""


def parse_args(default_filepath=""):
    parser = argparse.ArgumentParser(
        description='Generates a class implemetation for each desired driver'
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
        'filepath', default=default_filepath,
        help='filepath of the output'
    )

    args = parser.parse_args()
    return args


def format_docstring(docstring):
    quoted_doc = "\"\"\"{0}\"\"\"".format(docstring)
    max_line_length = 79 - 4  # -4 for indentation

    if len(quoted_doc) <= max_line_length:
        return quoted_doc  # short enough so we return it as is

    word_split_doc = quoted_doc.split(" ")

    start_line_idx = 0
    lines = []

    for idx, _ in enumerate(word_split_doc):
        tmp_line = " ".join(word_split_doc[start_line_idx:idx + 1])

        if idx == len(word_split_doc) - 1:  # last word
            if len(tmp_line) < max_line_length:
                # last word fits in the last line
                line = " ".join(word_split_doc[start_line_idx:idx + 1])
                lines.append(line)
            else:
                # last word does not fit in the last line
                line = " ".join(word_split_doc[start_line_idx:idx])
                lines.append(line)
                lines.append(word_split_doc[-1])
            break
        elif len(tmp_line) < max_line_length:
            continue
        line = " ".join(word_split_doc[start_line_idx:idx])
        start_line_idx = idx

        lines.append(line)

    if len(lines):
        last_line = lines.pop()
        last_line = last_line[:len(last_line) - 3]  # remove the end quotes
        lines.append(last_line)
        lines.append("\"\"\"")  # End of docstring on a new line

    return "\n    ".join([l for l in lines if l])


def format_cls_signature(cls_name):
    if len(cls_name) < 48:
        # The class signature fits in 1 line
        return "class {metric_cls_name}(BaseVSphereMetricPuller):".format(
            metric_cls_name=cls_name
        )

    return (
        "class {metric_cls_name}(\n"
        "{padding}BaseVSphereMetricPuller):"
    ).format(
        metric_cls_name=cls_name,
        padding=" " * 4 * 2,
    )

# def get_drivers_list(filepath):
#     with open(filepath) as drivers_file:
#         required_drivers = json.load(drivers_file)
#     return required_drivers


def export_py(data, filepath):
    print("Exporting to %s ..." % filepath)
    with open(filepath, "wb") as gen_file:
        gen_file.write(data.encode("utf-8"))


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


def generate_drivers_implementation(prefix, drivers, args):
    mapping = get_data_puller(args).wrapper.get_counter_mapping()
    output = ""
    for vsphere_metric_name in drivers:
        metric_metadata = mapping[vsphere_metric_name]
        group_and_sample = vsphere_metric_name.split(".")
        cls_name = "".join(
            ["VSphere", prefix.capitalize()] +
            [part[0].upper() + part[1:]
             for part in group_and_sample if part]
        )

        description = format_docstring(metric_metadata["description"])

        cls_signature = format_cls_signature(cls_name)
        output += "\n"
        output += template.format(
            metric_cls_signature=cls_signature,
            metric_name=vsphere_metric_name,
            metric_group=prefix,
            metric_type=metric_metadata["type"],
            metric_unit=metric_metadata["unit"],
            metric_description=description,
        )
    return output


def format_filepath(prefix, filepath):
    split_filepath = list(os.path.split(filepath))
    parts = split_filepath[:-1] + ["_".join([prefix] + [split_filepath[-1]])]
    formatted_filepath = os.path.join(*parts)
    return formatted_filepath


def main():
    default_filepath = os.path.join(os.getcwd(), "generated_drivers.py")
    args = parse_args(default_filepath)
    mapping = get_data_puller(args).wrapper.get_counter_mapping()

    prefixes = ["vm", "host"]
    for prefix in prefixes:
        output = "{0}".format(header)

        # required_drivers = get_drivers_list(args.required_drivers)
        required_drivers = sorted(mapping.keys())  # all of them

        output += generate_drivers_implementation(
            prefix, required_drivers, args
        )

        output_filepath = format_filepath(prefix, args.filepath)
        export_py(output, output_filepath)

    print("Done.")

if __name__ == '__main__':
    main()
