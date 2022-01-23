Create HashiVault AppRole wrapped secret-id.

**Role Variables**

.. zuul:rolevar:: vault_role_name

   AppRole name to try to generate secret-id for.

.. zuul:rolevar:: zuul_vault_addr

   HashiVault URL.

.. zuul:rolevar:: vault_token

   Token with privileges to check presence of the application role and generate
   new secret-id.

.. zuul:rolevar:: vault_secret_dest

   Location on the host to write file with secret content to. The file is
   overwritten.
