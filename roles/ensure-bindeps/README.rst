Fetch bindep.txt if it does not exist.

This role fetches bindep.txt from otcdocstheme if the project doesn't have one already.

**Role Variables**

.. zuul:rolevar:: zuul_work_dir
   :default: {{ zuul.project.dir }}

   Working directory.

.. zuul:rolevar:: bindep_download_url
   :default: https://raw.githubusercontent.com/opentelekomcloud/otcdocstheme/main/bindep.txt

   Download URL for the bindep.txt file
