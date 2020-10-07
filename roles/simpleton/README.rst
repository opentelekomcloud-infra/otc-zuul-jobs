Generic script runner, making zuul as simple as any popular CI solutions

**Role Variables**

.. zuul:rolevar:: simple_source_image
    :type: string
    :default: bash:latest

    This is base image to be used for your container.

.. zuul:rolevar:: simple_env
    :type: dict

    This is key:value dictionary of environment variables defined as `ENV` Dockerfile directive

.. zuul:rolevar:: simple_prerun
    :type: list

    This is list of commans to be executed during preparation phase (`RUN` Dockerfile directives).

.. zuul:rolevar:: simple_run
    :type: list

    This is list of commands to be executed (`CMD` Dockerfile directive).
