#!/usr/bin/env python3
#
# Copyright 2014 Rackspace Australia
# Copyright 2018-2019 Red Hat, Inc
#
# Licensed under the Apache License, Version 2.0 (the "License"); you may
# not use this file except in compliance with the License. You may obtain
# a copy of the License at
#
# http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS, WITHOUT
# WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied. See the
# License for the specific language governing permissions and limitations
# under the License.

# Make coding more python3-ish
from __future__ import (absolute_import, division, print_function)
__metaclass__ = type


"""
Generic utilities used for log upload.
"""

import gzip
import io
import logging
import mimetypes
import os
import shutil
import stat
import tempfile
import time
try:
    import urllib.parse as urlparse
except ImportError:
    import urllib as urlparse
import zlib
import collections


try:
    # Python 3.3+
    from collections.abc import Sequence
except ImportError:
    from collections import Sequence

mimetypes.init()
mimetypes.add_type('text/plain', '.yaml')

MAX_UPLOAD_THREADS = 24
POST_ATTEMPTS = 3

# Map mime types to apache icons
APACHE_MIME_ICON_MAP = {
    '_default': 'unknown.png',
    'application/gzip': 'compressed.png',
    'application/directory': 'folder.png',
    'text/html': 'text.png',
    'text/plain': 'text.png',
}

# Map mime types to apache icons
APACHE_FILE_ICON_MAP = {
    '..': 'back.png',
}

# These icon files are from the Apache project and are in the public
# domain.
ICON_IMAGES = {
    'back.png': 'iVBORw0KGgoAAAANSUhEUgAAABQAAAAWCAMAAAD3n0w0AAAAElBMVEX/'
                '///M//+ZmZlmZmYzMzMAAACei5rnAAAAAnRSTlP/AOW3MEoAAABWSURB'
                'VHjabdBBCgAhDEPRRpv7X3kwEMsQ//IRRC08urjRHbha5VLFUsVSxVI9'
                'lmDh5hMpHD6n0EgoiZG0DNINpnWlcVXaRix76e1/8dddcL6nG0Ri9gHj'
                'tgSXKYeLBgAAAABJRU5ErkJggg==',
    'compressed.png': 'iVBORw0KGgoAAAANSUhEUgAAABQAAAAWCAMAAAD3n0w0AAADAFBM'
                      'VEX//////8z//5n//2b//zP//wD/zP//zMz/zJn/zGb/zDP/zAD/'
                      'mf//mcz/mZn/mWb/mTP/mQD/Zv//Zsz/Zpn/Zmb/ZjP/ZgD/M///'
                      'M8z/M5n/M2b/MzP/MwD/AP//AMz/AJn/AGb/ADP/AADM///M/8zM'
                      '/5nM/2bM/zPM/wDMzP/MzMzMzJnMzGbMzDPMzADMmf/MmczMmZnM'
                      'mWbMmTPMmQDMZv/MZszMZpnMZmbMZjPMZgDMM//MM8zMM5nMM2bM'
                      'MzPMMwDMAP/MAMzMAJnMAGbMADPMAACZ//+Z/8yZ/5mZ/2aZ/zOZ'
                      '/wCZzP+ZzMyZzJmZzGaZzDOZzACZmf+ZmcyZmZmZmWaZmTOZmQCZ'
                      'Zv+ZZsyZZpmZZmaZZjOZZgCZM/+ZM8yZM5mZM2aZMzOZMwCZAP+Z'
                      'AMyZAJmZAGaZADOZAABm//9m/8xm/5lm/2Zm/zNm/wBmzP9mzMxm'
                      'zJlmzGZmzDNmzABmmf9mmcxmmZlmmWZmmTNmmQBmZv9mZsxmZplm'
                      'ZmZmZjNmZgBmM/9mM8xmM5lmM2ZmMzNmMwBmAP9mAMxmAJlmAGZm'
                      'ADNmAAAz//8z/8wz/5kz/2Yz/zMz/wAzzP8zzMwzzJkzzGYzzDMz'
                      'zAAzmf8zmcwzmZkzmWYzmTMzmQAzZv8zZswzZpkzZmYzZjMzZgAz'
                      'M/8zM8wzM5kzM2YzMzMzMwAzAP8zAMwzAJkzAGYzADMzAAAA//8A'
                      '/8wA/5kA/2YA/zMA/wAAzP8AzMwAzJkAzGYAzDMAzAAAmf8AmcwA'
                      'mZkAmWYAmTMAmQAAZv8AZswAZpkAZmYAZjMAZgAAM/8AM8wAM5kA'
                      'M2YAMzMAMwAAAP8AAMwAAJkAAGYAADPuAADdAAC7AACqAACIAAB3'
                      'AABVAABEAAAiAAARAAAA7gAA3QAAuwAAqgAAiAAAdwAAVQAARAAA'
                      'IgAAEQAAAO4AAN0AALsAAKoAAIgAAHcAAFUAAEQAACIAABHu7u7d'
                      '3d27u7uqqqqIiIh3d3dVVVVEREQiIiIREREAAAD7CIKZAAAAJXRS'
                      'TlP///////////////////////////////////////////////8A'
                      'P89CTwAAAGtJREFUeNp9z9ENgDAIhOEOco+dybVuEXasFMRDY/x5'
                      '+xJCO6Znu6kSx7BhXyjtKBWWNlwW88Loid7hFRKBXiIYCMfMEYUQ'
                      'QohC3CjFA5nIjqx1CqlDLGR/EhM5O06yvin0ftGOyIS7lV14AsQN'
                      'aR7rMEBYAAAAAElFTkSuQmCC',
    'folder.png': 'iVBORw0KGgoAAAANSUhEUgAAABQAAAAWCAMAAAD3n0w0AAAAElBMVEX/'
                  '////zJnM//+ZZjMzMzMAAADCEvqoAAAAA3RSTlP//wDXyg1BAAAASElE'
                  'QVR42s3KQQ6AQAhDUaXt/a/sQDrRJu7c+NmQB0e99B3lnqjT6cYx6zSI'
                  'bV40n3D7psYMoBoz4w8/EdNYQsbGEjNxYSljXTEsA9O1pLTvAAAAAElF'
                  'TkSuQmCC',
    'text.png': 'iVBORw0KGgoAAAANSUhEUgAAABQAAAAWCAMAAAD3n0w0AAAAD1BMVEX/'
                '///M//+ZmZkzMzMAAABVsTOVAAAAAnRSTlP/AOW3MEoAAABISURBVHja'
                'tcrRCgAgCENRbf7/N7dKomGvngjhMsPLD4NdMPwia438NRIyxsaL/XQZ'
                'hyxpkC6zyjLXGVXnkhqWJWIIrOgeinECLlUCjBCqNQoAAAAASUVORK5C'
                'YII=',
    'unknown.png': 'iVBORw0KGgoAAAANSUhEUgAAABQAAAAWCAMAAAD3n0w0AAAAD1BMVEX/'
                   '///M//+ZmZkzMzMAAABVsTOVAAAAAnRSTlP/AOW3MEoAAABYSURBVHja'
                   'ncvRDoAgDEPRruX/v1kmNHPBxMTLyzgD6FmsILg56g2hQnJkOco4yZhq'
                   'tN5nYd5Zq0LsHblwxwP9GTCWsaGtoelANKzOlz/RfaLYUmLE6E28ALlN'
                   'AupSdoFsAAAAAElFTkSuQmCC'}


# Begin vendored code
# This code is licensed under the Public Domain/CC0 and comes from
# https://github.com/leenr/gzip-stream/blob/master/gzip_stream.py
# Code was modified:
#   removed type annotations to support python2.
#   removed use of *, somearg for positional anonymous args.
#   Default compression level to 9.
#
#   changed read method argument name from length to size and
#   added read method default value size=-1 for parent class compatibility

class GZIPCompressedStream(io.RawIOBase):
    def __init__(self, stream, compression_level=9):
        assert 1 <= compression_level <= 9

        self._compression_level = compression_level
        self._stream = stream

        self._compressed_stream = io.BytesIO()
        self._compressor = gzip.GzipFile(
            mode='wb',
            fileobj=self._compressed_stream,
            compresslevel=compression_level
        )

        # because of the GZIP header written by `GzipFile.__init__`:
        self._compressed_stream.seek(0)
        self.count = 0

    def read(self, size=-1):
        r = super().read(size)
        self.count += len(r)
        return r

    def tell(self):
        return self.count

    @property
    def compression_level(self):
        return self._compression_level

    @property
    def stream(self):
        return self._stream

    def readable(self):
        return True

    def _read_compressed_into(self, b):
        buf = self._compressed_stream.read(len(b))
        b[:len(buf)] = buf
        return len(buf)

    def readinto(self, b):
        b = memoryview(b)

        offset = 0
        size = len(b)
        while offset < size:
            offset += self._read_compressed_into(b[offset:])
            if offset < size:
                # self._compressed_buffer now empty
                if self._compressor.closed:
                    # nothing to compress anymore
                    break
                # compress next bytes
                self._read_n_compress(size)

        return offset

    def _read_n_compress(self, size):
        assert size > 0

        data = self._stream.read(size)

        # rewind buffer to the start to free up memory
        # (because anything currently in the buffer should be already
        #  streamed off the object)
        self._compressed_stream.seek(0)
        self._compressed_stream.truncate(0)

        if data:
            self._compressor.write(data)
        else:
            # this will write final data (will flush zlib with Z_FINISH)
            self._compressor.close()

        # rewind to the buffer start
        self._compressed_stream.seek(0)

    def __repr__(self):
        return (
            '{self.__class__.__name__}('
            '{self.stream!r}, '
            'compression_level={self.compression_level!r}'
            ')'
        ).format(self=self)

# End vendored code


def get_mime_icon(mime, filename=''):
    icon = (APACHE_FILE_ICON_MAP.get(filename) or
            APACHE_MIME_ICON_MAP.get(mime) or
            APACHE_MIME_ICON_MAP['_default'])
    return "data:image/png;base64,%s" % ICON_IMAGES[icon]


def retry_function(func):
    for attempt in range(1, POST_ATTEMPTS + 1):
        try:
            return func()
        except Exception:
            if attempt >= POST_ATTEMPTS:
                raise
            else:
                logging.exception("Error on attempt %d" % attempt)
                time.sleep(attempt * 10)


def sizeof_fmt(num, suffix='B'):
    # From http://stackoverflow.com/questions/1094841/
    # reusable-library-to-get-human-readable-version-of-file-size
    for unit in ['', 'K', 'M', 'G', 'T', 'P', 'E', 'Z']:
        if abs(num) < 1024.0:
            return "%3.1f%s%s" % (num, unit, suffix)
        num /= 1024.0
    return "%.1f%s%s" % (num, 'Y', suffix)


class FileDetail():
    """
    Used to generate indexes with links or as the file path
    to push to storage.
    """

    def __init__(self, full_path, relative_path, filename=None):
        """
        Args:
            full_path (str): The absolute path to the file on disk.
            relative_path (str): The relative path from the artifacts source
                                 used for links.
            filename (str): An optional alternate filename in links.
        """
        # Make FileNotFoundError exception to be compatible with python2
        try:
            FileNotFoundError  # noqa: F823
        except NameError:
            FileNotFoundError = OSError

        self.full_path = full_path
        if filename is None:
            self.filename = os.path.basename(full_path)
        else:
            self.filename = filename
        self.relative_path = relative_path

        if self.full_path and os.path.isfile(self.full_path):
            mime_guess, encoding = mimetypes.guess_type(self.full_path)
            self.mimetype = mime_guess if mime_guess else 'text/plain'
            self.encoding = encoding
            self.folder = False
        else:
            self.mimetype = 'application/directory'
            self.encoding = None
            self.folder = True
        try:
            st = os.stat(self.full_path)
            self.last_modified = time.gmtime(st[stat.ST_MTIME])
            self.size = st[stat.ST_SIZE]
        except (FileNotFoundError, TypeError):
            self.last_modified = time.gmtime(0)
            self.size = 0

    def __repr__(self):
        t = 'Folder' if self.folder else 'File'
        return '<%s %s>' % (t, self.relative_path)


class FileList(Sequence):
    '''A collection of FileDetail objects

    This is a list-like group of FileDetail objects, intended to be
    used as a context manager around the upload process.
    '''
    def __init__(self):
        self.file_list = []
        self.file_list.append(FileDetail(None, '', ''))
        self.tempdirs = []

    def __enter__(self):
        return self

    def __exit__(self, type, value, traceback):
        for tempdir in self.tempdirs:
            shutil.rmtree(tempdir)

    def __getitem__(self, item):
        return self.file_list.__getitem__(item)

    def __len__(self):
        return self.file_list.__len__()

    def get_tempdir(self):
        '''Get a temporary directory

        Returns path to a private temporary directory which will be
        cleaned on exit
        '''
        tempdir = tempfile.mkdtemp(prefix='s-u-l-tmp')
        self.tempdirs.append(tempdir)
        return tempdir

    @staticmethod
    def _path_in_tree(root, path):
        full_path = os.path.realpath(os.path.abspath(
            os.path.expanduser(path)))
        if not full_path.startswith(root):
            logging.debug("Skipping path outside root: %s" % (path,))
            return False
        return True

    def add(self, file_path):
        """
        Generate a list of files to upload to storage. Recurses through
        directories
        """

        # file_list: A list of FileDetails to push to storage
        file_list = []

        if os.path.isfile(file_path):
            relative_path = os.path.basename(file_path)
            file_list.append(FileDetail(file_path, relative_path))
        elif os.path.isdir(file_path):
            original_root = os.path.realpath(os.path.abspath(
                os.path.expanduser(file_path)))

            parent_dir = os.path.dirname(file_path)
            if not file_path.endswith('/'):
                filename = os.path.basename(file_path)
                full_path = file_path
                relative_name = os.path.relpath(full_path, parent_dir)
                file_list.append(FileDetail(full_path, relative_name,
                                            filename))
            # TODO: this will copy the result of symlinked files, but
            # it won't follow directory symlinks.  If we add that, we
            # should ensure that we don't loop.
            for path, folders, files in os.walk(file_path):
                # Sort folder in-place so that we recurse in order.
                files.sort(key=lambda x: x.lower())
                folders.sort(key=lambda x: x.lower())
                # relative_path: The path between the given directory
                # and the one being currently walked.
                relative_path = os.path.relpath(path, parent_dir)

                for filename in folders:
                    full_path = os.path.join(path, filename)
                    if not self._path_in_tree(original_root, full_path):
                        continue
                    relative_name = os.path.relpath(full_path, parent_dir)
                    file_list.append(FileDetail(full_path, relative_name,
                                                filename))

                for filename in files:
                    full_path = os.path.join(path, filename)
                    if not self._path_in_tree(original_root, full_path):
                        continue
                    relative_name = os.path.relpath(full_path, parent_dir)
                    file_detail = FileDetail(full_path, relative_name)
                    file_list.append(file_detail)

        self.file_list += file_list


class Indexer():
    """Index a FileList

    Functions to generate indexes and other collated data for a
    FileList

     - make_indexes() : make index.html in folders
    """
    def __init__(self, file_list):
        '''
        Args:
            file_list (FileList): A FileList object with all files
             to be indexed.
        '''
        assert isinstance(file_list, FileList)
        self.file_list = file_list

    def _make_index_file(self, folder_links, title, tempdir, append_footer):
        """Writes an index into a file for pushing"""
        for file_details in folder_links:
            # Do not generate an index file if one exists already.
            # This may be the case when uploading other machine generated
            # content like python coverage info.
            if self.index_filename == file_details.filename:
                return
        index_content = self._generate_log_index(
            folder_links, title, append_footer)
        fd = open(os.path.join(tempdir, self.index_filename), 'w')
        fd.write(index_content)
        return os.path.join(tempdir, self.index_filename)

    def _generate_log_index(self, folder_links, title, append_footer):
        """Create an index of logfiles and links to them"""

        output = '<html><head><title>%s</title></head><body>\n' % title
        output += '<h1>%s</h1>\n' % title
        output += '<table><tr><th></th><th>Name</th><th>Last Modified</th>'
        output += '<th>Size</th></tr>'

        file_details_to_append = None
        for file_details in folder_links:
            output += '<tr>'
            output += (
                '<td><img alt="[ ]" title="%(m)s" src="%(i)s"></img></td>' % ({
                    'm': file_details.mimetype,
                    'i': get_mime_icon(file_details.mimetype,
                                       file_details.filename),
                }))
            filename = file_details.filename
            link_filename = filename
            if file_details.folder:
                filename += '/'
                link_filename += '/index.html'
            output += '<td><a href="%s">%s</a></td>' % (
                urlparse.quote(link_filename),
                filename)
            output += '<td>%s</td>' % time.asctime(
                file_details.last_modified)
            size = sizeof_fmt(file_details.size, suffix='')
            output += '<td style="text-align: right">%s</td>' % size
            output += '</tr>\n'

            if (append_footer and
                append_footer in file_details.filename):
                file_details_to_append = file_details

        output += '</table>'

        if file_details_to_append:
            output += '<br /><hr />'
            try:
                with open(file_details_to_append.full_path, 'r') as f:
                    output += f.read()
            except IOError:
                logging.exception("Error opening file for appending")

        output += '</body></html>\n'
        return output

    def make_indexes(self, create_parent_links=True,
                     create_topdir_parent_link=False,
                     append_footer='index_footer.html'):
        '''Make index.html files

        Iterate the file list and crete index.html files for folders

        Args:
          create_parent_links (bool): Create parent links
          create_topdir_parent_link (bool): Create topdir parent link
          append_footer (str): Filename of a footer to append to each
             generated page

        Return:
            No value, the self.file_list will be updated
        '''
        self.index_filename = 'index.html'

        folders = collections.OrderedDict()
        for f in self.file_list:
            if f.folder:
                folders[f.relative_path] = []
                folder = os.path.dirname(os.path.dirname(
                    f.relative_path + '/'))
                if folder == '/':
                    folder = ''
            else:
                folder = os.path.dirname(f.relative_path)
            folders[folder].append(f)

        indexes = {}
        parent_file_detail = FileDetail(None, '..', '..')
        for folder, files in folders.items():
            # Don't add the pseudo-top-directory
            if files and files[0].full_path is None:
                files = files[1:]
                if create_topdir_parent_link:
                    files = [parent_file_detail] + files
            elif create_parent_links:
                files = [parent_file_detail] + files

            # Do generate a link to the parent directory
            full_path = self._make_index_file(files, 'Index of %s' % (folder,),
                                              self.file_list.get_tempdir(),
                                              append_footer)

            if full_path:
                filename = os.path.basename(full_path)
                relative_name = os.path.join(folder, filename)
                indexes[folder] = FileDetail(full_path, relative_name)

        # This appends the index file at the end of the group of files
        # for each directory.
        new_list = []
        last_dirname = None
        for f in reversed(list(self.file_list)):
            if f.folder:
                relative_path = f.relative_path + '/'
            else:
                relative_path = f.relative_path
            dirname = os.path.dirname(relative_path)
            if dirname == '/':
                dirname = ''
            if dirname != last_dirname:
                index = indexes.pop(dirname, None)
                if index:
                    new_list.append(index)
                    last_dirname = dirname
            new_list.append(f)
        new_list.reverse()
        self.file_list.file_list = new_list


class GzipFilter():
    chunk_size = 16384

    def __init__(self, infile):
        self.gzipfile = GZIPCompressedStream(infile)
        self.done = False

    def __iter__(self):
        return self

    def __next__(self):
        if self.done:
            self.gzipfile.close()
            raise StopIteration()
        data = self.gzipfile.read(self.chunk_size)
        if not data:
            self.done = True
        return data


class DeflateFilter():
    chunk_size = 16384

    def __init__(self, infile):
        self.infile = infile
        self.encoder = zlib.compressobj()
        self.done = False

    def __iter__(self):
        return self

    def __next__(self):
        if self.done:
            raise StopIteration()
        ret = b''
        while True:
            data = self.infile.read(self.chunk_size)
            if data:
                ret = self.encoder.compress(data)
                if ret:
                    break
            else:
                self.done = True
                ret = self.encoder.flush()
                break
        return ret
