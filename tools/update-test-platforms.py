#!/usr/bin/env python
#
# Copyright 2019 Red Hat, Inc.
#
# Licensed under the Apache License, Version 2.0 (the "License"); you may
# not use this file except in compliance with the License. You may obtain
# a copy of the License at
#
#      http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS, WITHOUT
# WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied. See the
# License for the specific language governing permissions and limitations
# under the License.

# Update job definitions for multi-platform jobs, and make sure every
# in-repo test job appears in a project definition.  This script
# re-writes the files in zuul-tests.d.  It should be run from the root
# of the repo.

import os

from ruamel.yaml.comments import CommentedMap

import ruamellib

# There are fedora- and debian-latest nodesets, but they can't be used
# in the multinode jobs, so just use the real labels everywhere.

PLATFORMS = [
    'centos-7',
    'centos-8',
    'debian-stretch',
    'fedora-29',
    'gentoo-17-0-systemd',
    'opensuse-15',
    'opensuse-tumbleweed',
    'ubuntu-bionic',
    'ubuntu-xenial',
]

# insert a platform from above to make it non-voting
NON_VOTING = [
    'opensuse-tumbleweed',
]


def get_nodeset(platform, multinode):
    d = CommentedMap()
    if not multinode:
        d['nodes'] = [
            CommentedMap([('name', platform), ('label', platform)]),
        ]
    else:
        d['nodes'] = [
            CommentedMap([('name', 'primary'), ('label', platform)]),
            CommentedMap([('name', 'secondary'), ('label', platform)]),
        ]
        d['groups'] = [
            CommentedMap([('name', 'switch'), ('nodes', ['primary'])]),
            CommentedMap([('name', 'peers'), ('nodes', ['secondary'])]),
        ]
    return d


def handle_file(fn):
    yaml = ruamellib.YAML()
    data = yaml.load(open(fn))
    outdata = []
    outprojects = []
    joblist_check = []
    joblist_gate = []
    has_non_voting = False
    for obj in data:
        if 'job' in obj:
            job = obj['job']
            if 'auto-generated' in job.get('tags', []):
                continue
            outdata.append(obj)
            tags = job.get('tags', [])
            all_platforms = False
            if 'all-platforms-multinode' in tags:
                multinode = True
                all_platforms = True
            elif 'all-platforms' in tags:
                all_platforms = True
                multinode = False
            if all_platforms:
                for platform in PLATFORMS:
                    voting = False if platform in NON_VOTING else True
                    ojob = CommentedMap()
                    ojob['name'] = job['name'] + '-' + platform
                    if not voting:
                        ojob['name'] += '-nv'
                        ojob['voting'] = False
                        has_non_voting = True
                    desc = job['description'].split('\n')[0]
                    ojob['description'] = desc + ' on ' \
                        + platform
                    ojob['parent'] = job['name']
                    ojob['tags'] = 'auto-generated'
                    ojob['nodeset'] = get_nodeset(platform, multinode)
                    outdata.append({'job': ojob})
                    joblist_check.append(ojob['name'])
                    if voting:
                        joblist_gate.append(ojob['name'])
            else:
                joblist_check.append(job['name'])
                # don't append non-voting jobs to gate
                if job.get('voting', True):
                    joblist_gate.append(job['name'])
                else:
                    has_non_voting = True
        elif 'project' in obj:
            outprojects.append(obj)
        else:
            outdata.append(obj)
    # We control the last project stanza
    outdata.extend(outprojects)
    project = outprojects[-1]['project']
    project['check']['jobs'] = joblist_check
    # Use the same dictionary if there are no non-voting jobs
    # (i.e. check is the same as gate); this gives nicer YAML output
    # using dictionary anchors
    project['gate']['jobs'] = joblist_gate if has_non_voting else joblist_check
    with open(fn, 'w') as f:
        yaml.dump(outdata, stream=f)


def main():
    for f in os.listdir('zuul-tests.d'):
        if not f.endswith('.yaml'):
            continue
        if f == 'project.yaml':
            continue
        handle_file(os.path.join('zuul-tests.d', f))


if __name__ == "__main__":
    main()
