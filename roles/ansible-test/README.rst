Execute ansible-test for testing ansible collections.

A project willing to test ansible collection must set variables `ansible_test_collection_namespace` and `ansible_test_collection_name`, since the ansible-test is working best from the installed collection location. Thus it is also expected, that the collection is built and installed before executing this role.

**Role Variables**

.. zuul:rolevar:: ansible_test_collections
   :default: true

   Whether collection testing is expected.

.. zuul:rolevar:: ansible_test_collection_name
   :default: ''

   Test collection name.

.. zuul:rolevar:: ansible_test_collection_namespace
   :default: ''

   Test collection namespace.

.. zuul:rolevar:: ansible_test_integration_targets
   :default: ''

   List of integration target to limit.

.. zuul:rolevar:: ansible_test_command
   :default: integration

   ansible-test command (sanity, unit, integration).

.. zuul:rolevar:: ansible_test_continue_on_error
   :default: true

   Whether to continue testing on errors (not applicable for all testing commands).

.. zuul:rolevar:: ansible_test_retry_on_error
   :default: false

   Whether to retry test on error (not applicable for all test commands).

.. zuul:rolevar:: ansible_test_skip_tags
   :default: ''

   List of tags to skip (not applicable to all test commands).

.. zuul:rolevar:: ansible_test_no_temp_unicode
   :default: false

   Whether to use --no-temp-unicode argument for ansible-test command.

.. zuul:rolevar:: ansible_test_location
   :default: ~/ansible-test

   Path to ansible-test command.

.. zuul:rolevar:: ansible_test_python
   :default: ''

   Whether to add --python XX argument to the ansible-test invocaction.

.. zuul:rolevar:: ansible_test_skip_tests
   :default: ''

   List of sanity tests to skip.

