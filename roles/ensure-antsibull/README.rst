Install Anstsibull

**Role Variables**

.. zuul:rolevar:: zuul_work_dir
   :default: zuul.project.dir

   Working directory.

.. zuul:rolevar:: zuul_work_virtualenv
   :default: ansible_user_dir/.venv

   VirtualEnv into which antsibull is installed.

.. zuul:rolevar:: antsibull_packages
   :default: [antsibull]

   List of packages to install.

.. zuul:rolevar:: doc_building_extra_packages
   :default: []

   Additional packages to install.

