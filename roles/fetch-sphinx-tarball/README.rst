Collect output from a sphinx build as a tarball

By default, this copies the output from the sphinx build on the worker
to the log root of the executor as a tarball, and then extracts the
archive into the log root for viewing.

**Role Variables**

.. zuul:rolevar:: sphinx_build_dir
   :default: doc/build

   Directory relative to zuul_work_dir where build output should be
   found.

.. zuul:rolevar:: zuul_work_dir
   :default: {{ zuul.project.src_dir }}

   The location of the main working directory of the job.

.. zuul:rolevar:: sphinx_pdf_files
   :default: list

   A list of file names of PDF files to collect.
   By default, the list contains as entry only
   ``doc-{{ zuul.project.short_name }}.pdf``.

.. zuul:rolevar:: zuul_use_fetch_output
   :default: false

   Whether to synchronize files to the executor work dir, or to only
   copy them on the test instance.

   When set to ``False``, the default, the role synchronizes the
   tarball archives and extracted documentation files to the executor
   ``log_root``.

   When set to ``True``, the content is copied locally to
   ``{{  ansible_user_dir }}/zuul-output/logs/``.  The ``fetch-output`` role
   needs to be run to copy this output to the executor ``log_root``.
