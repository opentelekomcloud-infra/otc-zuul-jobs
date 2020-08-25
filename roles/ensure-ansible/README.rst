Install Ansible

**Role Variables**

.. zuul:rolevar:: ensure_ansible_package_name
   :default: ansible-base

   Name of the pypi package with Ansible to install, (ansible or ansible-base).

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
   :default: '~/.local/venv'

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

** Output Variables**

.. zuul:rolevar:: ensure_ansible_ansible_executable

   Path to the installed `ansible` executable.

.. zuul:rolevar:: ensure_ansible_galaxy_executable

   Path to the installed `ansible-galaxy` executable.

.. zuul:rolevar:: ensure_ansible_root_dir

   Path to the root directory (virtual environment) where ansible is installed.
