Generate SBOM with Syft
=======================

**Role Variables**

.. zuul:rolevar:: generate_syft_report_artifact_path

   Path or name of the artifact to generate syft report

.. zuul:rolevar:: generate_syft_report_format
   :default: cyclonedx-xml

   Format of the SBOM report

.. zuul:rolevar:: generate_syft_report_path

   Path where to save the report
