# Copyright (C) 2018 Red Hat, Inc.
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
try:
    from unittest import mock
except ImportError:
    import mock

import requests
from .zuul_swift_upload import Uploader
from ..module_utils.zuul_jobs.upload_utils import FileDetail

FIXTURE_DIR = os.path.join(os.path.dirname(__file__),
                           'test-fixtures')


class MockUploader(Uploader):
    """An uploader that uses a mocked cloud object"""
    def __init__(self, container):
        self.container = container
        self.cloud = mock.Mock()
        self.dry_run = False
        self.public = True
        self.delete_after = None
        self.prefix = ""
        self.url = 'http://dry-run-url.com/a/path/'


class TestUpload(testtools.TestCase):

    def test_upload_result(self):
        uploader = MockUploader(container="container")

        # Let the upload method fail for the job-output.json, but not for the
        # inventory.yaml file
        def side_effect(container, name, **ignored):
            if name == "job-output.json":
                raise requests.exceptions.RequestException(
                    "Failed for a reason"
                )
        uploader.cloud.create_object = mock.Mock(
            side_effect=side_effect
        )

        # Get some test files to upload
        files = [
            FileDetail(
                os.path.join(FIXTURE_DIR, "logs/job-output.json"),
                "job-output.json",
            ),
            FileDetail(
                os.path.join(FIXTURE_DIR, "logs/zuul-info/inventory.yaml"),
                "inventory.yaml",
            ),
        ]

        expected_failures = [
            {
                "file": "job-output.json",
                "error": (
                    "Error posting file after multiple attempts: "
                    "Failed for a reason"
                ),
            },
        ]

        failures = uploader.upload(files)
        self.assertEqual(expected_failures, failures)
