# Copyright 2020 Open Telekom Cloud
#
#  Licensed under the Apache License, Version 2.0 (the "License"); you may
#  not use this file except in compliance with the License. You may obtain
#  a copy of the License at
#
#       http://www.apache.org/licenses/LICENSE-2.0
#
#  Unless required by applicable law or agreed to in writing, software
#  distributed under the License is distributed on an "AS IS" BASIS, WITHOUT
#  WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied. See the
#  License for the specific language governing permissions and limitations
#  under the License.
#

import os
import json
import re
import sys
import unittest

import subunit
import testtools


class TempestSubunitTestResult(testtools.TestResult):

    def __init__(self, *args, **kwargs):
        super(TempestSubunitTestResult, self).__init__()
        self.results = []

    @staticmethod
    def get_test_uuid(test):
        attrs = None
        try:
            attrs = test.split('[')[1].split(']')[0].split(',')
        except IndexError:
            pass
        if not attrs:
            return
        for attr in attrs:
            if attr.startswith('id-'):
                return '-'.join(attr.split('-')[1:])

    def addSuccess(self, testcase):
        super(TempestSubunitTestResult, self).addSuccess(testcase)
        test_result = {
            'name': str(re.sub(r'\[.*\]', '', testcase.id())),
            'status': 'success'}
        uuid = self.get_test_uuid(str(testcase.id()))
        if uuid:
            test_result['uuid'] = uuid
        self.results.append(test_result)

    def addError(self, test, err=None, details=None):
        super(TempestSubunitTestResult, self).addError(test)
        test_result = {
            'name': str(re.sub(r'\[.*\]', '', test.id())),
            'result': self._err_details_to_string(test, err, details),
            'status': 'error'
        }
        uuid = self.get_test_uuid(str(test.id()))
        if uuid:
            test_result['uuid'] = uuid
        self.results.append(test_result)

    def addFailure(self, test, err=None, details=None):
        super(TempestSubunitTestResult, self).addFailure(test, err, details)
        test_result = {
            'name': str(re.sub(r'\[.*\]', '', test.id())),
            'result': self._err_details_to_string(test, err, details),
            'status': 'failure'
        }
        uuid = self.get_test_uuid(str(test.id()))
        if uuid:
            test_result['uuid'] = uuid
        self.results.append(test_result)

    def addSkip(self, test, reason=None, details=None):
        super(TempestSubunitTestResult, self).addSkip(test, reason, details)
        test_result = {
            'name': str(re.sub(r'\[.*\]', '', test.id())),
            'result': reason,
            'status': 'skip'
        }
        uuid = self.get_test_uuid(str(test.id()))
        if uuid:
            test_result['uuid'] = uuid
        self.results.append(test_result)

    def get_results(self):
        return self.results


class SubunitProcessor:
    def __init__(self, in_stream,
                 result_class=TempestSubunitTestResult):
        self.in_stream = in_stream
        self.result_class = result_class

    def process_stream(self):
        with open(self.in_stream, 'r') as fin:
            test = subunit.ProtocolTestCase(fin)
            runner = unittest.TextTestRunner(stream=open(os.devnull, 'w'),
                                             resultclass=self.result_class)

            # Run (replay) the test from subunit stream.
            test_result = runner.run(test)
            return test_result.get_results()


class App:

    def __init__(self):
        self.tempest_dir = sys.argv[1]
        self.test_list = sys.argv[2]
        self.output_file = sys.argv[3]
        self.required_tests = {}

    def _get_required_tests(self, tests_file='.test_list'):
        lst = open(tests_file).read()
        p = re.compile(r'(.*)\[id-(.*)\]')
        for test in re.findall(r'.*\[.*\]', lst):
            grp = p.match(test)
            if grp:
                self.required_tests[grp.group(2)] = dict(
                    name=grp.group(1),
                    status='not_executed'
                )

    def _get_next_stream_subunit_output_file(self, tempest_dir):
        if os.path.exists(os.path.join(tempest_dir, '.stestr.conf')):
            sub_dir = '.stestr'
        else:
            sub_dir = '.testrepository'
        try:
            subunit_file = str(
                int(open(os.path.join(tempest_dir, sub_dir,
                                      'next-stream'), 'r').read().rstrip()
                    ) - 1)

        except (IOError, OSError):
            subunit_file = "0"

        return os.path.join(tempest_dir, sub_dir, subunit_file)

    def process(self):
        self._get_required_tests(self.test_list)
        processor = SubunitProcessor(
            self._get_next_stream_subunit_output_file(self.tempest_dir))
        for test in processor.process_stream():
            uuid = test.get('uuid')
            if uuid in self.required_tests:
                self.required_tests[uuid].update(test)

        with open(self.output_file, 'w') as f:
            json.dump(self.required_tests, f)


if __name__ == '__main__':
    app = App()
    app.process()
