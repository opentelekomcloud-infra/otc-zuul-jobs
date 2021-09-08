# Copyright (C) 2018-2019 Red Hat, Inc.
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

# Make coding more python3-ish
from __future__ import (absolute_import, division, print_function)
__metaclass__ = type

import os
import testtools

from .zuul_google_storage_upload import Credentials


FIXTURE_DIR = os.path.join(os.path.dirname(__file__),
                           'test-fixtures')


class TestCredential(testtools.TestCase):

    def test_credential(self):
        path = os.path.join(FIXTURE_DIR, 'gcs', 'auth.json')
        headers = {}
        c = Credentials(path)
        c.before_request(None, None, None, headers)
        self.assertEqual("Bearer something", headers['authorization'])
