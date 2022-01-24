Upload artifact archive to swift

**Role Variables**

.. zuul:rolevar:: swift_token

   Swift API token

.. zuul:rolevar:: artifact_src

   Path to the artifact to upload

.. zuul:rolevar:: upload_artifact_swift_object_store_endpoint

   Swift endpoint URL

.. zuul:rolevar:: upload_artifact_swift_container_name
   :default: zuul.project.short_name

   Container name

.. zuul:rolevar:: upload_artifact_swift_container_public
   :default: true

   Flag whether container should be publicly readable or not

.. zuul:rolevar:: upload_artifact_swift_container_read_acl

   Read ACL on the container to set. If not set
   upload_artifact_swift_container_public is being analyzed.

.. zuul:rolevar:: upload_artifact_swift_prefix

   Optional prefix for the container path
