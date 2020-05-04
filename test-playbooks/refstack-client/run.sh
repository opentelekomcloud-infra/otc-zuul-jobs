#!/usr/bin/bash -x

source .venv/bin/activate

TEST_LIST=""
if [ -f "tests" ]; then
    TEST_LIST="--test-list tests"
fi

# Currently there is bug in refstack-client, which fails in non-verbose mode
refstack-client test -c tempest.conf ${TEST_LIST} -p -v -- --concurrent 2
