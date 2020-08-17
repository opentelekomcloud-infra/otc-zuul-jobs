Install Ansible

**Role Variables**

.. zuul:rolevar:: ensure_ansible_version
   :default: latest

   Version of Ansible to install, pip format.

.. zuul:rolevar:: ensure_ansible_state
   :default: present

   State of Ansible package, can be "present", "absent", "forcereinstall", "latest".

.. zuul:rolevar:: ensure_ansible_pip_extra_args
   :default: ''

   Extra arguments to pass to pip, like "--user" or "--update".

.. zuul:rolevar:: ensure_ansible_venv_path
   :default: ''

   Path to directory of Virtualenv

.. zuul:rolevar:: ensure_ansible_virtualenv_command
   :default: virtualenv

   The command or a pathname to the command to create the virtual environment with.

.. zuul:rolevar:: ensure_ansible_virtualenv_python
   :default: system default python

   The Python executable used for creating the virtual environment.

.. zuul:rolevar:: ensure_ansible_virtualenv_site_packages
   :default: false

   Whether the virtual environment will inherit packages from the global
   site-packages directory.
