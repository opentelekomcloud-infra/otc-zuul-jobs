# Make coding more python3-ish
from __future__ import (absolute_import, division, print_function)
__metaclass__ = type

import queue

import openstack

from ansible.module_utils.basic import AnsibleModule


def run_module():
    # define available arguments/parameters a user can pass to the module
    module_args = dict(
        cloud=dict(type='raw', required=True),
        filters=dict(type='dict', required=False)
    )

    module = AnsibleModule(
        argument_spec=module_args,
        supports_check_mode=True
    )

    conn = openstack.connect(module.params['cloud'])
    status_queue = queue.Queue()
    resources = []

    conn.project_cleanup(
        dry_run=module.check_mode,
        wait_timeout=120,
        status_queue=status_queue,
        filters=module.params['filters'])

    while not status_queue.empty():
        res = status_queue.get()
        resources.append(dict(
            type=type(res).__name__,
            name=res.name,
            id=res.id
        ))

    module.exit_json(
        changed=not module.check_mode,
        resources=resources)


def main():
    run_module()


if __name__ == '__main__':
    main()
