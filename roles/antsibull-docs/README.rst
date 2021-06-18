Execute antsibull-docs.

This role executes antsibull-docs to generate RST files for the ansible collection. Files are merged with the content in `antsibull_docs_dir` to allow overriding.

**Role Variables**

.. zuul:rolevar:: zuul_work_dir
   :default: {{ zuul.project.dir }}

   Working directory.

.. zuul:rolevar:: zuul_work_virtualenv
   :default: {{ ansible_user_dir }}/.venv

   VirtualEnv into which antsibull is installed.

.. zuul:rolevar:: antsibull_docs_executable
   :default: {{ zuul_work_virtualenv }}/bin/antsibull-docs

   Path to antsibull-docs executable.

.. zuul:rolevar:: antsibull_docs_squash
   :default: true

   Whether to enable `--squash` argument.

.. zuul:rolevar:: antsibull_docs_dir
   :default: {{ zuul_work_dir }}/doc/source

   Location to place generated files..
