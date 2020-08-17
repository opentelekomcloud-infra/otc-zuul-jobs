# This is a fake zuul_return to make ansible-lint happy
from ansible.module_utils.basic import AnsibleModule


def main():
    return AnsibleModule()
