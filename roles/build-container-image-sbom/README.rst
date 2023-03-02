Build container images SBOMs.

This role works in pair with `build-container-image1` role to generate sbom
reports for the built images.

**Role Variables**

.. zuul:rolevar:: zuul_work_dir
   :default: {{ zuul.project.src_dir }}

   The project directory.

.. zuul:rolevar:: build_container_image_sbom
   :default: true

   Flag to enable/disable SBOM processing

.. zuul:rolevar:: container_sbom_command
   :default: /usr/local/bin/syft

   Path to the executable used for generation of
   the SBOM file
