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
import six
import testtools
import time
import stat
import fixtures
try:
    from unittest import mock
except ImportError:
    import mock

import requests
from bs4 import BeautifulSoup
from .zuul_swift_upload import Uploader
from ..module_utils.zuul_jobs.upload_utils import FileList, Indexer, FileDetail
from .filefixture import FileFixture

FIXTURE_DIR = os.path.join(os.path.dirname(__file__),
                           'test-fixtures')


class SymlinkFixture(fixtures.Fixture):
    links = [
        ('bad_symlink', '/etc'),
        ('bad_symlink_file', '/etc/issue'),
        ('good_symlink', 'controller'),
        ('recursive_symlink', '.'),
        ('symlink_file', 'job-output.json'),
        ('symlink_loop_a', 'symlink_loop'),
        ('symlink_loop/symlink_loop_b', '..'),
    ]

    def _setUp(self):
        self.file_fixture = FileFixture()
        self.file_fixture.setUp()
        self.addCleanup(self.file_fixture.cleanUp)
        for (src, target) in self.links:
            path = os.path.join(self.file_fixture.root, 'links', src)
            os.symlink(target, path)
            self.addCleanup(os.unlink, path)


class TestFileList(testtools.TestCase):

    def assert_files(self, result, files):
        self.assertEqual(len(result), len(files))
        for expected, received in zip(files, result):
            e = expected[0]
            if six.PY2:
                e = e.encode('utf-8')
            self.assertEqual(e, received.relative_path)
            if e and e[0][-1] == '/':
                efilename = os.path.split(
                    os.path.dirname(e))[1] + '/'
            else:
                efilename = os.path.split(e)[1]
            self.assertEqual(efilename, received.filename)
            if received.folder:
                if received.full_path is not None and expected[0] != '':
                    self.assertTrue(os.path.isdir(received.full_path))
            else:
                self.assertTrue(os.path.isfile(received.full_path))
            self.assertEqual(expected[1], received.mimetype)
            self.assertEqual(expected[2], received.encoding)

    def find_file(self, file_list, path):
        for f in file_list:
            if f.relative_path == path:
                return f

    def test_single_dir_trailing_slash(self):
        '''Test a single directory with a trailing slash'''

        with FileList() as fl:
            with FileFixture() as file_fixture:
                fl.add(os.path.join(file_fixture.root, 'logs/'))
                self.assert_files(fl, [
                    ('', 'application/directory', None),
                    ('controller', 'application/directory', None),
                    ('zuul-info', 'application/directory', None),
                    ('job-output.json', 'application/json', None),
                    (u'\u13c3\u0e9a\u0e9a\u03be-unicode.txt',
                     'text/plain', None),
                    ('controller/subdir', 'application/directory', None),
                    ('controller/compressed.gz', 'text/plain', 'gzip'),
                    ('controller/cpu-load.svg', 'image/svg+xml', None),
                    ('controller/journal.xz', 'text/plain', 'xz'),
                    ('controller/service_log.txt', 'text/plain', None),
                    ('controller/syslog', 'text/plain', None),
                    ('controller/subdir/foo::3.txt', 'text/plain', None),
                    ('controller/subdir/subdir.txt', 'text/plain', None),
                    ('zuul-info/inventory.yaml', 'text/plain', None),
                    ('zuul-info/zuul-info.controller.txt', 'text/plain', None),
                ])

    def test_single_dir(self):
        '''Test a single directory without a trailing slash'''
        with FileList() as fl:
            with FileFixture() as file_fixture:
                fl.add(os.path.join(file_fixture.root, 'logs'))
                self.assert_files(fl, [
                    ('', 'application/directory', None),
                    ('logs', 'application/directory', None),
                    ('logs/controller', 'application/directory', None),
                    ('logs/zuul-info', 'application/directory', None),
                    ('logs/job-output.json', 'application/json', None),
                    (u'logs/\u13c3\u0e9a\u0e9a\u03be-unicode.txt',
                     'text/plain', None),
                    ('logs/controller/subdir', 'application/directory', None),
                    ('logs/controller/compressed.gz', 'text/plain', 'gzip'),
                    ('logs/controller/cpu-load.svg', 'image/svg+xml', None),
                    ('logs/controller/journal.xz', 'text/plain', 'xz'),
                    ('logs/controller/service_log.txt', 'text/plain', None),
                    ('logs/controller/syslog', 'text/plain', None),
                    ('logs/controller/subdir/foo::3.txt', 'text/plain', None),
                    ('logs/controller/subdir/subdir.txt', 'text/plain', None),
                    ('logs/zuul-info/inventory.yaml', 'text/plain', None),
                    ('logs/zuul-info/zuul-info.controller.txt',
                     'text/plain', None),
                ])

    def test_single_file(self):
        '''Test a single file'''
        with FileList() as fl:
            with FileFixture() as file_fixture:
                fl.add(os.path.join(file_fixture.root,
                                    'logs/zuul-info/inventory.yaml'))
                self.assert_files(fl, [
                    ('', 'application/directory', None),
                    ('inventory.yaml', 'text/plain', None),
                ])

    def test_symlinks(self):
        '''Test symlinks'''
        with FileList() as fl:
            symlink_fixture = self.useFixture(SymlinkFixture())
            fl.add(os.path.join(symlink_fixture.file_fixture.root, 'links/'))
            self.assert_files(fl, [
                ('', 'application/directory', None),
                ('controller', 'application/directory', None),
                ('good_symlink', 'application/directory', None),
                ('recursive_symlink', 'application/directory', None),
                ('symlink_loop', 'application/directory', None),
                ('symlink_loop_a', 'application/directory', None),
                ('job-output.json', 'application/json', None),
                ('symlink_file', 'text/plain', None),
                ('controller/service_log.txt', 'text/plain', None),
                ('symlink_loop/symlink_loop_b', 'application/directory', None),
                ('symlink_loop/placeholder', 'text/plain', None),
            ])

    def test_index_files(self):
        '''Test index generation'''
        with FileList() as fl:
            symlink_fixture = self.useFixture(SymlinkFixture())
            fl.add(os.path.join(symlink_fixture.file_fixture.root, 'logs'))
            ix = Indexer(fl)
            ix.make_indexes()

            self.assert_files(fl, [
                ('', 'application/directory', None),
                ('index.html', 'text/html', None),
                ('logs', 'application/directory', None),
                ('logs/controller', 'application/directory', None),
                ('logs/zuul-info', 'application/directory', None),
                ('logs/job-output.json', 'application/json', None),
                (u'logs/\u13c3\u0e9a\u0e9a\u03be-unicode.txt',
                 'text/plain', None),
                ('logs/index.html', 'text/html', None),
                ('logs/controller/subdir', 'application/directory', None),
                ('logs/controller/compressed.gz', 'text/plain', 'gzip'),
                ('logs/controller/cpu-load.svg', 'image/svg+xml', None),
                ('logs/controller/journal.xz', 'text/plain', 'xz'),
                ('logs/controller/service_log.txt', 'text/plain', None),
                ('logs/controller/syslog', 'text/plain', None),
                ('logs/controller/index.html', 'text/html', None),
                ('logs/controller/subdir/foo::3.txt', 'text/plain', None),
                ('logs/controller/subdir/subdir.txt', 'text/plain', None),
                ('logs/controller/subdir/index.html', 'text/html', None),
                ('logs/zuul-info/inventory.yaml', 'text/plain', None),
                ('logs/zuul-info/zuul-info.controller.txt',
                 'text/plain', None),
                ('logs/zuul-info/index.html', 'text/html', None),
            ])

            top_index = self.find_file(fl, 'index.html')
            page = open(top_index.full_path).read()
            page = BeautifulSoup(page, 'html.parser')
            rows = page.find_all('tr')[1:]

            self.assertEqual(len(rows), 1)

            self.assertEqual(rows[0].find('a').get('href'), 'logs/index.html')
            self.assertEqual(rows[0].find('a').text, 'logs/')

            subdir_index = self.find_file(
                fl, 'logs/controller/subdir/index.html')
            page = open(subdir_index.full_path).read()
            page = BeautifulSoup(page, 'html.parser')
            rows = page.find_all('tr')[1:]
            self.assertEqual(rows[0].find('a').get('href'), '../index.html')
            self.assertEqual(rows[0].find('a').text, '../')

            # Test proper escaping of files with funny names
            self.assertEqual(rows[1].find('a').get('href'), 'foo%3A%3A3.txt')
            self.assertEqual(rows[1].find('a').text, 'foo::3.txt')
            # Test files without escaping
            self.assertEqual(rows[2].find('a').get('href'), 'subdir.txt')
            self.assertEqual(rows[2].find('a').text, 'subdir.txt')

    def test_index_files_trailing_slash(self):
        '''Test index generation with a trailing slash'''
        with FileList() as fl:
            with FileFixture() as file_fixture:
                fl.add(os.path.join(file_fixture.root, 'logs/'))
                ix = Indexer(fl)
                ix.make_indexes()

                self.assert_files(fl, [
                    ('', 'application/directory', None),
                    ('controller', 'application/directory', None),
                    ('zuul-info', 'application/directory', None),
                    ('job-output.json', 'application/json', None),
                    (u'\u13c3\u0e9a\u0e9a\u03be-unicode.txt',
                     'text/plain', None),
                    ('index.html', 'text/html', None),
                    ('controller/subdir', 'application/directory', None),
                    ('controller/compressed.gz', 'text/plain', 'gzip'),
                    ('controller/cpu-load.svg', 'image/svg+xml', None),
                    ('controller/journal.xz', 'text/plain', 'xz'),
                    ('controller/service_log.txt', 'text/plain', None),
                    ('controller/syslog', 'text/plain', None),
                    ('controller/index.html', 'text/html', None),
                    ('controller/subdir/foo::3.txt', 'text/plain', None),
                    ('controller/subdir/subdir.txt', 'text/plain', None),
                    ('controller/subdir/index.html', 'text/html', None),
                    ('zuul-info/inventory.yaml', 'text/plain', None),
                    ('zuul-info/zuul-info.controller.txt', 'text/plain', None),
                    ('zuul-info/index.html', 'text/html', None),
                ])

            top_index = self.find_file(fl, 'index.html')
            page = open(top_index.full_path).read()
            page = BeautifulSoup(page, 'html.parser')
            rows = page.find_all('tr')[1:]

            self.assertEqual(len(rows), 4)

            self.assertEqual(rows[0].find('a').get('href'),
                             'controller/index.html')
            self.assertEqual(rows[0].find('a').text, 'controller/')

            self.assertEqual(rows[1].find('a').get('href'),
                             'zuul-info/index.html')
            self.assertEqual(rows[1].find('a').text, 'zuul-info/')

            subdir_index = self.find_file(fl, 'controller/subdir/index.html')
            page = open(subdir_index.full_path).read()
            page = BeautifulSoup(page, 'html.parser')
            rows = page.find_all('tr')[1:]
            self.assertEqual(rows[0].find('a').get('href'), '../index.html')
            self.assertEqual(rows[0].find('a').text, '../')

            # Test proper escaping of files with funny names
            self.assertEqual(rows[1].find('a').get('href'), 'foo%3A%3A3.txt')
            self.assertEqual(rows[1].find('a').text, 'foo::3.txt')
            # Test files without escaping
            self.assertEqual(rows[2].find('a').get('href'), 'subdir.txt')
            self.assertEqual(rows[2].find('a').text, 'subdir.txt')

    def test_topdir_parent_link(self):
        '''Test index generation creates topdir parent link'''
        with FileList() as fl:
            with FileFixture() as file_fixture:
                fl.add(os.path.join(file_fixture.root, 'logs/'))
                ix = Indexer(fl)
                ix.make_indexes(
                    create_parent_links=True,
                    create_topdir_parent_link=True)

                self.assert_files(fl, [
                    ('', 'application/directory', None),
                    ('controller', 'application/directory', None),
                    ('zuul-info', 'application/directory', None),
                    ('job-output.json', 'application/json', None),
                    (u'\u13c3\u0e9a\u0e9a\u03be-unicode.txt',
                     'text/plain', None),
                    ('index.html', 'text/html', None),
                    ('controller/subdir', 'application/directory', None),
                    ('controller/compressed.gz', 'text/plain', 'gzip'),
                    ('controller/cpu-load.svg', 'image/svg+xml', None),
                    ('controller/journal.xz', 'text/plain', 'xz'),
                    ('controller/service_log.txt', 'text/plain', None),
                    ('controller/syslog', 'text/plain', None),
                    ('controller/index.html', 'text/html', None),
                    ('controller/subdir/foo::3.txt', 'text/plain', None),
                    ('controller/subdir/subdir.txt', 'text/plain', None),
                    ('controller/subdir/index.html', 'text/html', None),
                    ('zuul-info/inventory.yaml', 'text/plain', None),
                    ('zuul-info/zuul-info.controller.txt', 'text/plain', None),
                    ('zuul-info/index.html', 'text/html', None),
                ])

                top_index = self.find_file(fl, 'index.html')
                page = open(top_index.full_path).read()
                page = BeautifulSoup(page, 'html.parser')
                rows = page.find_all('tr')[1:]

                self.assertEqual(len(rows), 5)

                self.assertEqual(rows[0].find('a').get('href'),
                                 '../index.html')
                self.assertEqual(rows[0].find('a').text, '../')

                self.assertEqual(rows[1].find('a').get('href'),
                                 'controller/index.html')
                self.assertEqual(rows[1].find('a').text, 'controller/')

                self.assertEqual(rows[2].find('a').get('href'),
                                 'zuul-info/index.html')
                self.assertEqual(rows[2].find('a').text, 'zuul-info/')

                subdir_index = self.find_file(
                    fl, 'controller/subdir/index.html'
                )
                page = open(subdir_index.full_path).read()
                page = BeautifulSoup(page, 'html.parser')
                rows = page.find_all('tr')[1:]
                self.assertEqual(
                    rows[0].find('a').get('href'), '../index.html'
                )
                self.assertEqual(rows[0].find('a').text, '../')

                # Test proper escaping of files with funny names
                self.assertEqual(
                    rows[1].find('a').get('href'), 'foo%3A%3A3.txt'
                )
                self.assertEqual(rows[1].find('a').text, 'foo::3.txt')
                # Test files without escaping
                self.assertEqual(rows[2].find('a').get('href'), 'subdir.txt')
                self.assertEqual(rows[2].find('a').text, 'subdir.txt')

    def test_no_parent_links(self):
        '''Test index generation creates topdir parent link'''
        with FileList() as fl:
            with FileFixture() as file_fixture:
                fl.add(os.path.join(file_fixture.root, 'logs/'))
                ix = Indexer(fl)
                ix.make_indexes(
                    create_parent_links=False,
                    create_topdir_parent_link=False)

                self.assert_files(fl, [
                    ('', 'application/directory', None),
                    ('controller', 'application/directory', None),
                    ('zuul-info', 'application/directory', None),
                    ('job-output.json', 'application/json', None),
                    (u'\u13c3\u0e9a\u0e9a\u03be-unicode.txt',
                     'text/plain', None),
                    ('index.html', 'text/html', None),
                    ('controller/subdir', 'application/directory', None),
                    ('controller/compressed.gz', 'text/plain', 'gzip'),
                    ('controller/cpu-load.svg', 'image/svg+xml', None),
                    ('controller/journal.xz', 'text/plain', 'xz'),
                    ('controller/service_log.txt', 'text/plain', None),
                    ('controller/syslog', 'text/plain', None),
                    ('controller/index.html', 'text/html', None),
                    ('controller/subdir/foo::3.txt', 'text/plain', None),
                    ('controller/subdir/subdir.txt', 'text/plain', None),
                    ('controller/subdir/index.html', 'text/html', None),
                    ('zuul-info/inventory.yaml', 'text/plain', None),
                    ('zuul-info/zuul-info.controller.txt', 'text/plain', None),
                    ('zuul-info/index.html', 'text/html', None),
                ])

                top_index = self.find_file(fl, 'index.html')
                page = open(top_index.full_path).read()
                page = BeautifulSoup(page, 'html.parser')
                rows = page.find_all('tr')[1:]

                self.assertEqual(len(rows), 4)

                self.assertEqual(rows[0].find('a').get('href'),
                                 'controller/index.html')
                self.assertEqual(rows[0].find('a').text,
                                 'controller/')

                self.assertEqual(rows[1].find('a').get('href'),
                                 'zuul-info/index.html')
                self.assertEqual(rows[1].find('a').text,
                                 'zuul-info/')

                subdir_index = self.find_file(
                    fl, 'controller/subdir/index.html'
                )
                page = open(subdir_index.full_path).read()
                page = BeautifulSoup(page, 'html.parser')
                rows = page.find_all('tr')[1:]

                # Test proper escaping of files with funny names
                self.assertEqual(
                    rows[0].find('a').get('href'), 'foo%3A%3A3.txt'
                )
                self.assertEqual(rows[0].find('a').text, 'foo::3.txt')
                # Test files without escaping
                self.assertEqual(rows[1].find('a').get('href'), 'subdir.txt')
                self.assertEqual(rows[1].find('a').text, 'subdir.txt')


class TestFileDetail(testtools.TestCase):

    def test_get_file_detail(self):
        '''Test files info'''
        with FileFixture() as file_fixture:
            path = os.path.join(file_fixture.root, 'logs/job-output.json')
            file_detail = FileDetail(path, '')
            path_stat = os.stat(path)
            self.assertEqual(
                time.gmtime(path_stat[stat.ST_MTIME]),
                file_detail.last_modified)
            self.assertEqual(16, file_detail.size)

    def test_get_file_detail_missing_file(self):
        '''Test files that go missing during a walk'''

        file_detail = FileDetail('missing/file/that/we/cant/find', '')

        self.assertEqual(time.gmtime(0), file_detail.last_modified)
        self.assertEqual(0, file_detail.size)


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
        with FileFixture() as file_fixture:
            files = [
                FileDetail(
                    os.path.join(file_fixture.root, "logs/job-output.json"),
                    "job-output.json",
                ),
                FileDetail(
                    os.path.join(
                        file_fixture.root, "logs/zuul-info/inventory.yaml"
                    ),
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
