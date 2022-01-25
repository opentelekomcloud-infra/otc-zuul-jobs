# Licensed under the Apache License, Version 2.0 (the "License"); you may
# not use this file except in compliance with the License. You may obtain
# a copy of the License at
#
# http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS, WITHOUT
# WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied. See the
# License for the specific language governing permissions and limitations
# under the License.

# Make coding more python3-ish
from __future__ import (absolute_import, division, print_function)
__metaclass__ = type


"""
Utility to upload files to swift
"""

import logging
import traceback

import openstack
import requests
import requests.exceptions
import requestsexceptions
import keystoneauth1.exceptions

from ansible.module_utils.basic import AnsibleModule


def get_cloud(cloud):
    if isinstance(cloud, dict):
        config = openstack.config.loader.OpenStackConfig().get_one(**cloud)
        return openstack.connection.Connection(config=config)
    else:
        return openstack.connect(cloud=cloud)


def main():
    module = AnsibleModule(
        argument_spec=dict(
            cloud=dict(required=True, type='raw'),
            container=dict(required=True, type='str'),
            prefix=dict(type='str', default=''),
            src=dict(required=True, type='str'),
            public=dict(type='bool', default=True),
            read_acl=dict(type='str')
        )
    )

    p = module.params
    cloud = get_cloud(p.get('cloud'))
    failures = []
    try:
        container = cloud.get_container(p['container'])
        if not container:
            cloud.create_container(name=p['container'])
        read_acl = ''
        if not p['read_acl']:
            read_acl = '.r:*,.rlistings' if p['public'] else ''
        else:
            read_acl = p['read_acl']
        cloud.update_container(
            p['container'], {'x-container-read': read_acl})

        with open(p['src'], 'rb') as f:
            headers = {
                "X-Detect-Content-Type": "true",
                "Content-Type": "application/gzip",
                "Accept": "application/json"
            }

            response = cloud.object_store.put(
                "{}/{}?extract-archive=tar.gz".format(
                    p['container'],
                    p['prefix'],
                ),
                headers=headers,
                data=f
            )
            errors = response.json().get('Errors')
            for error in errors:
                failures.append({
                    "file": error[0],
                    "error": error[1]})

    except (keystoneauth1.exceptions.http.HttpError,
            requests.exceptions.RequestException):
        s = "Error uploading to %s.%s" % (cloud.name, cloud.config.region_name)
        logging.exception(s)
        s += "\n" + traceback.format_exc()
        module.fail_json(
            changed=False,
            msg=s,
            cloud=cloud.name,
            region_name=cloud.config.region_name)
    module.exit_json(
        changed=True,
        upload_failures=failures,
    )


if __name__ == '__main__':
    # Avoid unactionable warnings
    requestsexceptions.squelch_warnings(
        requestsexceptions.InsecureRequestWarning)

    main()
