from datetime import datetime
import requests
import base64
import json
from cryptography.hazmat.primitives import serialization as crypto_serialization
from cryptography.hazmat.primitives import hashes
from cryptography.hazmat.primitives.asymmetric import padding

from ansible.module_utils.basic import AnsibleModule
from ansible.module_utils._text import to_native


class InstallationTokenModule():
    argument_spec = dict(
        appid=dict(type='int', required=True),
        private_key=dict(type='str', required=True, no_log=True),
        expiration=dict(type='int', default=600),
        organization=dict(type='str', required=True),
        api_url=dict(type='str', default='https://api.github.com'),
        permissions=dict(type='dict'),
    )
    module_kwargs = {
        'supports_check_mode': True
    }

    def __init__(self):

        self.ansible = AnsibleModule(
            self.argument_spec,
            **self.module_kwargs)
        self.params = self.ansible.params
        self.module_name = self.ansible._name

    def base64url_encode(self, input: bytes):
        return base64.urlsafe_b64encode(input).decode('utf-8').replace('=', '')

    def get_token(self, appid, expiry, private_key):

        segments = []

        header = {"typ": "JWT", "alg": "RS256"}
        payload = {
            "iat": int(datetime.now().timestamp() - 10),
            "iss": appid,
            "exp": int(datetime.now().timestamp() + expiry)
        }

        json_header = json.dumps(header, separators=(",", ":")).encode()
        json_payload = json.dumps(payload, separators=(",", ":")).encode()

        segments.append(self.base64url_encode(json_header))
        segments.append(self.base64url_encode(json_payload))

        signing_input = ".".join(segments).encode()
        with open(private_key, "rb") as key_file:
            sign_key = crypto_serialization.load_pem_private_key(key_file.read(), password=None)

        signature = sign_key.sign(
            signing_input,
            padding.PKCS1v15(),
            hashes.SHA256()
        )

        segments.append(self.base64url_encode(signature))
        encoded_string = ".".join(segments)
        return encoded_string

    def __call__(self):
        appid = self.params['appid']
        private_key = self.params['private_key']
        expiration = self.params['expiration']
        organization = self.params['organization']
        api_url = self.params['api_url']

        token = self.get_token(appid, expiration, private_key)

        response = requests.get(
            f"{api_url}/app/installations",
            headers={
                'Authorization': f"Bearer {token}",
                'Accept': 'application/vnd.github.v3+json'
            }
        )
        if response.status_code >= 400:
            self.ansible.fail_json(
                msg="Error fetching installations",
                error=to_native(response.text),
            )
        data = response.json()
        installation = None
        for inst in data:
            if inst['account']['login'] == organization:
                installation = inst
                break
        if installation:
            data = dict()
            if self.params['permissions'] is not None:
                data = {'permissions': self.params['permissions']}
            response = requests.post(
                installation['access_tokens_url'],
                headers={
                    'Authorization': f"Bearer {token}",
                    'Accept': 'application/vnd.github.v3+json'
                },
                json=data
            )
            if response.status_code != 201:
                self.ansible.fail_json(
                    msg='Failed to fetch installation token',
                    error=to_native(response.text)
                )
            token_data = response.json()
            self.ansible.exit_json(
                organization=organization,
                id=installation['id'],
                token=token_data['token'],
                expires_at=token_data['expires_at']
            )
        self.ansible.fail_json(
            msg='Cannot find organization installation'
        )


def main():
    module = InstallationTokenModule()
    module()


if __name__ == '__main__':
    main()
