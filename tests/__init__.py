# Copyright (C) 2020 VEXXHOST, Inc.
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#    http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or
# implied.
#
# See the License for the specific language governing permissions and
# limitations under the License.

import os
import re
import yaml


def generate_dynamic_comments_tests(cls, test_path, func):
    def _create_test_using_file(name):
        def test(self):
            path = "%s/%s" % (test_path, name)
            with open(path) as fd:
                # Don't filter unicode chars as we need to parse \x1B
                yaml.reader.Reader.NON_PRINTABLE = re.compile('.^')
                data = yaml.load(fd, Loader=yaml.FullLoader)
            extra_args = {
                arg: data[arg] for arg in data
                if arg not in ('output', 'comments')
            }

            # Replace workdir in output by current work dir
            data['output'] = data['output'].format(workdir=os.getcwd())

            comments = func(data['output'], **extra_args)
            self.assertEqual(data['comments'], comments)
        return test

    for t in os.listdir(test_path):
        test = _create_test_using_file(t)
        test.__name__ = "test_%s" % t.split('.')[0]
        setattr(cls, test.__name__, test)
