Collect subunit outputs

**Role Variables**

.. zuul:rolevar:: zuul_work_dir
   :default: {{ ansible_user_dir }}/{{ zuul.project.src_dir }}

   Directory to work in. It has to be a fully qualified path.

.. zuul:rolevar:: fetch_subunit_output_additional_dirs
   :default: []

   List of additional directories which contains subunit files
   to collect. The content of zuul_work_dir is always checked,
   so it should not be added here.

.. zuul:rolevar:: tox_envlist

   tox environment that was used to run the tests originally.
