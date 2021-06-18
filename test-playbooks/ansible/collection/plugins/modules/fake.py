#!/usr/bin/python
# GNU General Public License v3.0+ (see COPYING or https://www.gnu.org/licenses/gpl-3.0.txt)

DOCUMENTATION = '''
---
module: fake
short_description: Add/Modify/Delete Fake
version_added: "0.0.1"
author: "Fake Author (@fake-author)"
description:
  - Add/Modify/Delete Fake.
options:
  name:
    description: Specifies the fake name.
    required: true
    type: str
  foo:
    description: Specifies the foo value.
    type: str
    default: bar
  state:
    description: Specifies fake state
    type: str
    choices: [absent, present]
    default: present

requirements: ["openstacksdk", "otcextensions"]
'''

RETURN = '''
fake:
  description: fake.
  type: complex
  returned: On Success.
  contains:
    id:
      description: Specifies the instance ID.
      type: str
'''
EXAMPLES = '''
# Create Fake.
- namespace_name.collection_name.fake:
    name: test.domain.name
    foo: bar
  state: present

'''

import abc
from ansible.module_utils.basic import AnsibleModule


class FakeModule:

    argument_spec = dict(
        name=dict(required=True, type='str'),
        foo=dict(required=False, type='str', default='bar'),
        state=dict(default='present', choices=['absent', 'present']),
    )
    module_kwargs = dict(
        supports_check_mode=True
    )

    def __init__(self):
        self.ansible = AnsibleModule(
            self.argument_spec,
            self.module_kwargs)

    @abc.abstractmethod
    def run(self):
        pass

    def __call__(self):
        """Execute `run` function when calling the instance.
        """

        try:
            results = self.run()
            if results and isinstance(results, dict):
                self.ansible.exit_json(**results)

        except Exception as e:
            self.ansible.fail_json(msg=str(e))


def main():
    module = FakeModule()
    module()


if __name__ == '__main__':
    main()
