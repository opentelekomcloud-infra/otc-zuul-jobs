Install binary tool from GitHub

**Role Variables**

.. zuul:rolevar:: ensure_base_install_dir
   :default: /usr/local/bin

   Directory to install binary in.

.. zuul:rolevar:: ensure_base_version
   :default: latest

   Version of tool

.. zuul:rolevar:: ensure_base_os
   :default: {{ ansible_system | lower }}

.. zuul:rolevar:: ensure_base_arch
   :default: amd64 / 386
