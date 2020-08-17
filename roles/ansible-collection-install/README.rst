Install Ansible collection.

**Role Variables**

.. zuul:rolevar:: ansible_collection_install_galaxy_collections_dir_path
   :default: ''

   Path to directory where to install collection to.
   If it's empty or not set, by default it's ~/.ansible/collections/ansible_collections

.. zuul:rolevar:: ansible_collection_install_galaxy_executable
   :default: ansible-galaxy

   Path to ansible-galaxy executable.

.. zuul:rolevar:: ansible_collection_install_galaxy_server
   :default: https://galaxy.ansible.com/

   URL of Ansible Galaxy server to install collection from.

.. zuul:rolevar:: ansible_collection_install_galaxy_force_deps
   :default: false

   Path to ansible-galaxy executable.

.. zuul:rolevar:: ansible_collection_install_galaxy_force_install
   :default: false

   Force overwriting an existing role or collection.

.. zuul:rolevar:: ansible_collection_install_galaxy_ignore_errors
   :default: false

   Ignore errors during installation and continue with the next specified collection.
   This will not ignore dependency conflict errors.

.. zuul:rolevar:: ansible_collection_install_galaxy_no_deps
   :default: false

   Don't download collections listed as dependencies.

.. zuul:rolevar:: ansible_collection_install_galaxy_requirements
   :default: ''

   A file containing a list of collections to be installed.

.. zuul:rolevar:: ansible_collection_install_galaxy_collections_set
   :default: []

   List of names of collections to install.

.. zuul:rolevar:: ansible_collection_install_galaxy_collection_name
   :default: ''

   Name of single collection to install.

.. zuul:rolevar:: ansible_collection_install_galaxy_ignore_certs
   :default: false

   Ignore SSL certificate validation errors.
