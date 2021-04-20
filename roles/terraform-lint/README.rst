Run terraform fmt with check flag and terraform validate. Assumes the appropriate version of terraform has been installed.

**Role Variables**

.. zuul:rolevar:: terraform_executable
   :default: {{ ansible_user_dir }}/.local/bin/terraform

   Path to terraform executable to use.

.. zuul:rolevar:: zuul_work_dir
   :default: {{ zuul.project.src_dir }}

   Directory to run terraform in.
