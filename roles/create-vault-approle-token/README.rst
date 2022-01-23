Create File with vault approle login token

**Role Variables**

.. zuul:rolevar:: vault_addr

   Vault URL.

.. zuul:rolevar:: vault_client_token

   Client token to use for unwrapping secret_id,

.. zuul:rolevar:: vault_wrapping_token_id

   Wrapped secret-id.

.. zuul:rolevar:: vault_role_id

   Role-Id of the AppRole.

.. zuul:rolevar:: vault_secret_id

   Optional secret_id. Either it or wrapped secret_id must be passed.

.. zuul:rolevar:: vault_token_dest

   Destination where to write client token to.
