#!/usr/bin/env python3

from argparse import ArgumentParser
from dataclasses import dataclass

import requests
from openstack.config import OpenStackConfig


@dataclass
class Credential:
    """Container for credential"""
    access: str
    secret: str
    security_token: str


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


def _get_session_token(auth_url, os_token) -> Credential:
    v30_url = auth_url.replace('/v3', '/v3.0')
    token_url = f'{v30_url}/OS-CREDENTIAL/securitytokens'

    auth_headers = {'X-Auth-Token': os_token}

    response = requests.post(token_url, headers=auth_headers, json=_session_token_request())
    if response.status_code != 201:
        raise RuntimeError('Failed to get temporary AK/SK:', response.text)
    data = response.json()['credential']
    return Credential(data['access'], data['secret'], data['securitytoken'])


def acquire_temporary_ak_sk(cloud_name) -> Credential:
    """Get temporary AK/SK using password auth"""
    os_config = OpenStackConfig()
    cloud = os_config.get_one(cloud=cloud_name)

    iam_session = cloud.get_session()
    auth_url = iam_session.get_endpoint(service_type='identity')
    os_token = iam_session.get_token()
    return _get_session_token(auth_url, os_token)


def parse_params():
    parser = ArgumentParser(description='Create Temporary AK/SK')
    parser.add_argument('--cloud', '-c', required=True)
    args = parser.parse_args()
    return args


def main():
    args = parse_params()
    credential = acquire_temporary_ak_sk(args.cloud)
    print(credential.access, credential.secret)


if __name__ == '__main__':
    main()
