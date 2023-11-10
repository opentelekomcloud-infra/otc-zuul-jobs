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

from __future__ import (absolute_import, division, print_function)

__metaclass__ = type

"""
Utility to create temporary ak/sk
"""

import requests
import requests.exceptions
from openstack.config import OpenStackConfig
from ansible.module_utils.basic import AnsibleModule


def _session_token_request():
    return {
        'auth': {
            'identity': {
                'methods': [
                    'token'
                ],
                'token': {
                    'duration-seconds': '900',
                }
            }
        }
    }


def main():
    module = AnsibleModule(
        argument_spec=dict(
            cloud=dict(required=True, type='raw', no_log=True),
        )
    )

    p = module.params
    os_config = OpenStackConfig()
    resp = [os_config.cloud_config['clouds']['functest_cloud']['auth'].keys()]
    module.exit_json(msg=f"{os_config.config_filename}\n"
                         f"{[i for i in resp]}\n")

    cloud = os_config.get_one(cloud=p.get('cloud'))
    iam_session = cloud.get_session()
    auth_url = iam_session.get_endpoint(service_type='identity')
    os_token = iam_session.get_token()
    v30_url = auth_url.replace('/v3', '/v3.0')
    token_url = f'{v30_url}/OS-CREDENTIAL/securitytokens'

    auth_headers = {'X-Auth-Token': os_token}

    response = requests.post(token_url, headers=auth_headers, json=_session_token_request())
    if response.status_code != 201:
        module.fail(
            changed=False,
            msg=f"Failed to get temporary AK/SK: {response.text}"
        )
    data = response.json()['credential']

    module.exit_json(
        changed=True,
        credential=data
    )


if __name__ == '__main__':
    main()
