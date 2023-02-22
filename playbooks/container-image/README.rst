This is one of a collection of jobs which are designed to work
together to build, upload, and promote docker images in a gating
context:

  * :zuul:job:`otc-build-container-image`: Build the images.
  * :zuul:job:`otc-upload-container-image`: Build and stage the images on dockerhub.

The :zuul:job:`otc-build-container-image` job is designed to be used in
a `check` pipeline and simply builds the images to verify that
the build functions.

The :zuul:job:`otc-upload-container-image` job builds and uploads the images
to Docker Hub, but only with a single tag corresponding to the
change ID.  This job is designed in a `gate` pipeline so that the
build produced by the gate is staged and can later be promoted to
production if the change is successful.

They all accept the same input data, principally a list of
dictionaries representing the images to build.  YAML anchors_ can be
used to supply the same data to all three jobs.

**Job Variables**

.. zuul:jobvar:: zuul_work_dir
   :default: {{ zuul.project.src_dir }}

   The project directory.  Serves as the base for
   :zuul:jobvar:`otc-build-container-image.container_images.context`.

.. zuul:jobvar:: container_images
   :type: list

   A list of images to build.  Each item in the list should have:

   .. zuul:jobvar:: context

      The docker build context; this should be a directory underneath
      :zuul:jobvar:`otc-build-container-image.zuul_work_dir`.

   .. zuul:jobvar:: repository

      The name of the target repository in dockerhub for the
      image.  Supply this even if the image is not going to be
      uploaded (it will be tagged with this in the local
      registry).

   .. zuul:jobvar:: path

      Optional: the directory that should be passed to docker build.
      Useful for building images with a Dockerfile in the context
      directory but a source repository elsewhere.

   .. zuul:jobvar:: build_args
      :type: list

      Optional: a list of values to pass to the docker ``--build-arg``
      parameter.

   .. zuul:jobvar:: target

      Optional: the target for a multi-stage build.

   .. zuul:jobvar:: tags
      :type: list
      :default: ['latest']

      A list of tags to be added to the image when promoted.

.. _anchors: https://yaml.org/spec/1.2/spec.html#&%20anchor//
