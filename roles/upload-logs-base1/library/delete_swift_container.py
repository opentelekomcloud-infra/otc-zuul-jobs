# Copyright 2019 Red Hat, Inc
#
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

import argparse
import openstack
import requests
import logging
import os

logging.basicConfig(level=logging.INFO)
# logging.getLogger("requests").setLevel(logging.DEBUG)
# logging.getLogger("keystoneauth").setLevel(logging.INFO)
# logging.getLogger("stevedore").setLevel(logging.INFO)
logging.captureWarnings(True)


def main():
    parser = argparse.ArgumentParser(
        description="Delete a swift container"
    )
    parser.add_argument('cloud',
                        help='Name of the cloud to use when uploading')
    parser.add_argument('container',
                        help='Name of the container to use when uploading')

    args = parser.parse_args()

    cloud = openstack.connect(cloud=args.cloud)

    sess = cloud.config.get_session()
    adapter = requests.adapters.HTTPAdapter(pool_maxsize=100)
    sess.mount('https://', adapter)

    container = cloud.get_container(args.container)
    print('Found container', container)
    print()
    for x in cloud.object_store.objects(args.container):
        print('Delete object', x.name)
        if x.name == '/':
            endpoint = cloud.object_store.get_endpoint()
            container = os.path.join(endpoint, args.container)
            cloud.session.delete(container + '//')
        else:
            cloud.object_store.delete_object(x)

    print()
    print('Delete container', container)
    cloud.object_store.delete_container(args.container)


if __name__ == "__main__":
    main()
