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
"""
Handle file name special characters in a file tree.

All files stored in a filetree can be renamed to urlencoded filenames.
A file tree can also be copied to a temporary location with file names
decoded, to be used in tests with special characters that are not always
possible to store on all file systems.

"""

from __future__ import print_function

import os
try:
    from urllib.parse import quote as urlib_quote
    from urllib.parse import unquote as urlib_unquote
except ImportError:
    from urllib import quote as urlib_quote
    from urllib import unquote as urlib_unquote
import argparse
import fixtures
import tempfile
import shutil


FIXTURE_DIR = os.path.join(os.path.dirname(__file__),
                           'test-fixtures')

SAFE_CHARS = "\\/"


def portable_makedirs_exist_ok(path):
    try:
        os.makedirs(path, exist_ok=True)
    except TypeError as err:
        if "unexpected keyword argument" not in str(err):
            raise err
    if not os.path.exists(path):
        try:
            os.makedirs(path)
        except OSError as err:
            if "File exists" not in err:
                raise err


def urlencode_filetree():
    for root, _, files in os.walk(FIXTURE_DIR):
        for filename in files:
            os.rename(
                os.path.join(root, filename),
                os.path.join(
                    root, urlib_quote(urlib_unquote(filename), SAFE_CHARS)
                )
            )


def populate_filetree(dst_dir=None):

    if not os.path.exists(FIXTURE_DIR):
        return None

    if not dst_dir:
        dst_dir = tempfile.mkdtemp()

    portable_makedirs_exist_ok(dst_dir)

    for root, dirs, files in os.walk(FIXTURE_DIR):
        dst_root = root.replace(FIXTURE_DIR, dst_dir, 1)
        for directory in dirs:
            portable_makedirs_exist_ok(os.path.join(dst_root, directory))
        for filename in files:
            try:
                shutil.copyfile(
                    os.path.join(root, filename),
                    os.path.join(dst_root, urlib_unquote(filename))
                )
            except IOError as err:
                print(
                    "\nFile {}".format(
                        os.path.join(dst_root, urlib_unquote(filename))
                    ),
                    "\nnot possible to write to disk,",
                    "\npossibly due to filename not being valid on Windows?\n"
                )
                shutil.rmtree(dst_dir)
                raise err

    return dst_dir


class FileFixture(fixtures.Fixture):

    def _setUp(self):
        self.root = tempfile.mkdtemp()
        self.addCleanup(self.local_clean_up)
        populate_filetree(self.root)
        # There is no cleanup action, as the filetree is left intact for other
        # tests to use

    def local_clean_up(self):
        shutil.rmtree(self.root)


if __name__ == '__main__':

    parser = argparse.ArgumentParser(__doc__)
    parser.add_argument(
        '--populate',
        help="Causes files in {}".format(FIXTURE_DIR) +
             "to be copied with decoded file name to a tmp dir" +
             "Overrides --encode",
        action='store_true'
    )
    parser.add_argument(
        '--encode',
        help="Causes files under {} to be renamed with urlencoding.".format(
            FIXTURE_DIR
        ) + "DEFAULT behaviour, overridden by --populate",
        action='store_true'
    )
    args = parser.parse_args()

    if args.populate:
        print(populate_filetree())
    else:
        urlencode_filetree()
