Build Ansible collection with ansible-galaxy

**Role Variables**

.. zuul:rolevar:: ansible_collection_build_collection_dir
   :default: zuul.project.src_dir

   Path to directory containing collection.

.. zuul:rolevar:: ansible_collection_build_galaxy_executable
   :default: ansible-galaxy

   Path to ansible-galaxy executable.

.. zuul:rolevar:: ansible_collection_build_galaxy_output_path
   :default: {{ ansible_user_dir }}/build_artifacts

    Path to directory where to save built artifact.

.. zuul:rolevar:: ansible_collection_build_collection_verify
   :default: true

    Whether to verify collection for publishing.

.. zuul:rolevar:: ansible_collection_build_generate_version
   :default: true

    Generate version of galaxy.yml in case of galaxy.yml.in presents.

.. zuul:rolevar:: ansible_collection_build_save_artifact
   :default: true

    Whether to save collection tarball as an artifact for child jobs.

.. zuul:rolevar:: ansible_collection_build_pip_dependencies
   :default: true

    Python modules to install for this role

.. zuul:rolevar:: ansible_collection_build_pip_virtualenv
   :default: true

    Path to virtualenv where to install required modules if it exists

.. zuul:rolevar:: ansible_collection_build_pip_extra_args
   :default: true

    Extra args to pip when install required modules

