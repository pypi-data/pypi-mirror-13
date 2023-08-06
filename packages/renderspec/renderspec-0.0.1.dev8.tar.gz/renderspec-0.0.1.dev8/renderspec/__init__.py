#!/usr/bin/python
# Copyright (c) 2015 SUSE Linux GmbH
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

from __future__ import print_function

import argparse
import os
import platform
import sys

from jinja2 import Environment
from jinja2 import FileSystemLoader
import pymod2pkg


###############
# jinja2 filter
###############
def _filter_noop(value):
    """do nothing filter"""
    return value


def _filter_license_spdx2fedora(value):
    """convert a given known spdx license to another one"""
    # more values can be taken from from https://github.com/hughsie/\
    #    appstream-glib/blob/master/libappstream-builder/asb-package-rpm.c#L76
    mapping = {
        "Apache-1.1": "ASL 1.1",
        "Apache-2.0": "ASL 2.0",
        "BSD-3-Clause": "BSD",
        "GPL-1.0+": "GPL+",
        "GPL-2.0": "GPLv2",
        "GPL-2.0+": "GPLv2+",
        "GPL-3.0": "GPLv3",
        "GPL-3.0+": "GPLv3+",
        "LGPL-2.1": "LGPLv2.1",
        "LGPL-2.1+": "LGPLv2+",
        "LGPL-2.0": "LGPLv2 with exceptions",
        "LGPL-2.0+": "LGPLv2+ with exceptions",
        "LGPL-3.0": "LGPLv3",
        "LGPL-3.0+": "LGPLv3+",
        "MIT": "MIT with advertising",
        "MPL-1.0": "MPLv1.0",
        "MPL-1.1": "MPLv1.1",
        "MPL-2.0": "MPLv2.0",
        "Python-2.0": "Python",
    }
    return mapping[value]


def generate_spec(spec_style, input_template_path):
    """generate a spec file with the given style and the given template"""
    env = Environment(loader=FileSystemLoader(
        os.path.dirname(input_template_path)))

    # register dist specific filters
    if spec_style == 'suse':
        env.filters['license'] = _filter_noop
    elif spec_style == 'fedora':
        env.filters['license'] = _filter_license_spdx2fedora
    else:
        raise Exception("Unknown spec style '%s' given" % (spec_style))

    # use pymod2pkg to translate python module names to package names
    def _filter_python_module2package(value):
        return pymod2pkg.module2package(value, spec_style)

    env.filters['py2pkg'] = _filter_python_module2package

    template = env.get_template(os.path.basename(input_template_path))
    return template.render()


def _get_default_distro():
    distname, version, id_ = platform.linux_distribution()
    if "suse" in distname.lower():
        return "suse"
    elif "fedora" in distname.lower():
        return "fedora"
    else:
        return "unknown"


def _get_default_template():
    fns = [f for f in os.listdir('.')
           if os.path.isfile(f) and f.endswith('.spec.j2')]
    if not fns:
        return None, ("No *.spec.j2 templates found. "
                      "See `renderspec -h` for usage.")
    elif len(fns) > 1:
        return None, ("Multiple *.spec.j2 templates found, "
                      "please specify one.\n"
                      "See `renderspec -h` for usage.")
    else:
        return fns[0], None


def process_args():
    distro = _get_default_distro()
    parser = argparse.ArgumentParser(
        description="Convert a .spec.j2 template into a .spec")
    parser.add_argument("-o", "--output",
                        help="output filename or '-' for stdout. "
                        "default: autodetect")
    parser.add_argument("--spec-style", help="distro style you want to use. "
                        "default: %s" % (distro), default=distro,
                        choices=['suse', 'fedora'])
    parser.add_argument("input-template", nargs='?',
                        help="specfile jinja2 template to render. "
                        "default: *.spec.j2")
    return vars(parser.parse_args())


def main():
    args = process_args()

    # autodetect input/output fns if possible
    input_template = args['input-template']
    if not input_template:
        input_template, errmsg = _get_default_template()
        if not input_template:
            print(errmsg)
            return 1
    output_fn = args['output']
    if not output_fn:
        if not input_template.endswith('.spec.j2'):
            print("Failed to autodetect output file name. "
                  "Please specify using `-o/--output`.")
            return 2
        output_fn, _, _ = input_template.rpartition('.')

    spec = generate_spec(args['spec_style'], input_template)
    if output_fn and output_fn != '-':
        print("Rendering: %s -> %s" % (input_template, output_fn))
        with open(output_fn, "w") as o:
            o.write(spec)
    else:
        print(spec)
    return 0


if __name__ == '__main__':
    sys.exit(main())
