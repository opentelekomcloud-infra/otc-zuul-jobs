Publish Ansible collection to Ansible Galaxy server

**Role Variables**

.. zuul:rolevar:: ansible_collection_publish_galaxy_collection_path
   :default: zuul.branch

   Directory contains collection tarballs to publish.

.. zuul:rolevar:: ansible_collection_publish_galaxy_executable
   :default: ansible-galaxy

   Path to ansible-galaxy executable.

.. zuul:rolevar:: ansible_collection_publish_collection_tarball
   :default: ansible-galaxy

   Path to single collection tarball to publish.

.. zuul:rolevar:: ansible_collection_publish_galaxy_info

   Complex argument which contains the information about the Ansible
   Galaxy server as well as the authentication information needed. It
   is expected that this argument comes from a `Secret`.

  .. zuul:rolevar:: url
     :default: https://galaxy.ansible.com

     The API server destination.

  .. zuul:rolevar:: token

     Identify with github token rather than username and password.
