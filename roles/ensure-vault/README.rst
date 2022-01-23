Install HashiCorp Vault

**Role Variables**

.. zuul:rolevar:: vault_install_dir
   :default: /usr/local/bin

   Directory to install vault in.

.. zuul:rolevar:: vault_version
   :default: 1.9.2

   Version of vault

.. zuul:rolevar:: vault_checksum
   :default: sha256:1e3eb5c225ff1825a59616ebbd4ac300e9d6eaefcae26253e49209350c0a5e71

   Checksum to verivy vault download

.. zuul:rolevar:: vault_os
   :default: {{ ansible_system | lower }}

.. zuul:rolevar:: vault_arch
   :default: amd64 / 386
