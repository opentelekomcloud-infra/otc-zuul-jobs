Fetch bindep.txt if it does not exist.

This role fetches bindep.txt from otcdocstheme if the project doesn't have one already.

**Role Variables**

.. zuul:rolevar:: zuul_work_dir
   :default: {{ zuul.project.dir }}

   Working directory.
