.. zuul:jobvar:: container_registry_credentials
   :type: dict

   This is expected to be a Zuul Secret with these keys:

   .. zuul:jobvar:: username

      The Dockerer registry username.

   .. zuul:jobvar:: password

      The Docker registry password.

   .. zuul:jobvar:: repository

      Optional; if supplied this is a regular expression which
      restricts to what repositories the image may be uploaded.  The
      following example allows projects to upload images to
      repositories within an organization based on their own names::

        repository: "^myorgname/{{ zuul.project.short_name }}.*"

