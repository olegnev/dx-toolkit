#!/usr/bin/env python
# -*- coding: utf-8 -*-
#
# Copyright (C) 2014 DNAnexus, Inc.
#
# This file is part of dx-toolkit (DNAnexus platform client libraries).
#
#   Licensed under the Apache License, Version 2.0 (the "License"); you may not
#   use this file except in compliance with the License. You may obtain a copy
#   of the License at
#
#       http://www.apache.org/licenses/LICENSE-2.0
#
#   Unless required by applicable law or agreed to in writing, software
#   distributed under the License is distributed on an "AS IS" BASIS, WITHOUT
#   WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied. See the
#   License for the specific language governing permissions and limitations
#   under the License.

from __future__ import print_function, unicode_literals

import os
import sys
import unittest
import random
import time
import tempfile
import subprocess
import pipes
from contextlib import contextmanager
import pexpect

import dxpy
from dxpy.scripts import dx_build_app
from dxpy_testutil import DXTestCase, check_output, temporary_project, select_project
import dxpy_testutil as testutil
from dxpy.packages import requests
from dxpy.exceptions import DXAPIError
from dxpy.compat import str, sys_encoding


@contextmanager
def chdir(dirname=None):
    curdir = os.getcwd()
    try:
        if dirname is not None:
            os.chdir(dirname)
        yield
    finally:
        os.chdir(curdir)

def run(command, **kwargs):
    print("$ %s" % (command,))
    output = check_output(command, shell=True, **kwargs)
    print(output)
    return output


# Create a random file. Return the file-id, and filename.
def create_file_in_project(trg_proj_id):
    testdir = tempfile.mkdtemp()
    with tempfile.NamedTemporaryFile(dir=testdir) as fd:
        fd.write("foo")
        fd.flush()
        file_id = run("dx upload {fname} --path {trg_proj} --brief --wait ".
                      format(trg_proj=trg_proj_id, fname=fd.name)).strip()
        return file_id, os.path.basename(fd.name)


def create_file_in_project_folder(trg_proj_id, path):
    testdir = tempfile.mkdtemp()
    with tempfile.NamedTemporaryFile(dir=testdir) as fd:
        fd.write("foo")
        fd.flush()
        file_id = run("dx upload {fname} --path {trg_proj}:{path} --brief --wait ".
                      format(trg_proj=trg_proj_id, fname=fd.name, path=path)).strip()
        return file_id, os.path.basename(fd.name)


def create_proj():
    project_name = "test_dx_cp_" + str(random.randint(0, 1000000)) + "_" + str(int(time.time() * 1000))
    proj_id = run("dx new project {name} --brief".format(name=project_name)).strip()
    return proj_id


def rm_project(projID):
    run("dx rmproject -y {p1}".format(p1=projID))


class TestDXCp(DXTestCase):
    # General question: a file can be specified by a name, or file-id.
    # How does that effect the cases below?
    #
    # list of test cases, that should work on the current implementation.
    #   files
    #     create new file with the same name in the target
    #       dx cp  proj-1111:/file-1111   proj-2222:/
    #     copy and rename
    #       dx cp  proj-1111:/file-1111   proj-2222:/file-2222
    #     multiple arguments
    #       dx cp  proj-1111:/file-1111 proj-2222:/file-2222 proj-3333:/
    #   folders
    #     copy recursively
    #       cp  proj-1111:/folder-xxxx  proj-2222:/
    #     what is supposed to happen here?
    #       cp  proj-1111:/folder-xxxx  proj-2222:/folder-xxxx
    #
    # Two new
    def test_legacy(self):
        print("Starting")

        # setup two projects
        projID1 = create_proj()
        projID2 = create_proj()

        # create new file with the same name in the target
        #    dx cp  proj-1111:/file-1111   proj-2222:/
        def file_with_same_name():
            file_id, _ = create_file_in_project(projID1)
            run("dx cp {p1}:/{f} {p2}".format(f=file_id, p1=projID1, p2=projID2))

            # make sure the file was copied
            listing_proj1 = run("dx ls --brief {p}".format(p=projID1))
            listing_proj2 = run("dx ls --brief {p}".format(p=projID2))
            self.assertEqual(listing_proj1, listing_proj2)

        # copy and rename
        #   dx cp  proj-1111:/file-1111   proj-2222:/file-2222
        def cp_rename():
            file_id, basename = create_file_in_project(projID1)
            run("dx cp {p1}:/{f1} {p2}:/{f2}".format(f1=basename, f2="AAA.txt", p1=projID1, p2=projID2))

        # multiple arguments
        #   dx cp  proj-1111:/file-1111 proj-2222:/file-2222 proj-3333:/
        def multiple_args():
            _, fname1 = create_file_in_project(projID1)
            _, fname2 = create_file_in_project(projID1)
            _, fname3 = create_file_in_project(projID1)
            run("dx cp {p1}:/{f1} {p1}:/{f2} {p1}:/{f3} {p2}:/".
                format(f1=fname1, f2=fname2, f3=fname3, p1=projID1, p2=projID2))

        # copy an entire directory
        def cp_dir():
            run("dx mkdir {p}:/foo".format(p=projID1))
            run("dx cp {p1}:/foo {p2}:/".format(p1=projID1, p2=projID2))

        # Wierd error code:
        #   This part makes sense:
        #     InvalidState: If cloned, a folder would conflict with the route of an existing folder.
        #   This does not:
        #     Successfully cloned from project: None, code 422
        #
        # TODO: causes an error, we need to catch it, and continue.
        # Hint from Phil: assert_subprocess_failure
        def copy_empty_folder_on_existing_folder():
            run("dx mkdir {p}:/foo".format(p=projID1))
            run("dx mkdir {p}:/foo".format(p=projID2))
            run("dx cp {p1}:/foo {p2}:/".format(p1=projID1, p2=projID2))

        # Should and does fail.
        # TODO: catch the error
        def copy_folder_on_existing_folder():
            run("dx mkdir {p}:/foo".format(p=projID1))
            fileID1, _ = create_file_in_project_folder(projID1, "/foo")
            fileID2, _ = create_file_in_project_folder(projID2, "/foo")
            run("dx cp {p1}:/foo {p2}:/".format(p1=projID1, p2=projID2))
            run("dx cp {p1}:/foo {p2}:/".format(p1=projID1, p2=projID2))

        # Passes, but gives a wierd error message:
        # dx cp project-BV80zyQ0Ffb7fj64v03fffqX:/foo/XX.txt  project-BV80vzQ0P9vk785K1GgvfZKv:/foo/XX.txt
        # The following objects already existed in the destination container and were not copied:
        #   [
        #   "
        #   f
        #   i
        #   l
        #   ...
        def copy_overwrite_wierd_error():
            fileID1, fname1 = create_file_in_project(projID1)
            run("dx cp {p1}:/{f} {p2}:/{f}".format(p1=projID1, f=fname1, p2=projID2))
            output = run("dx cp {p1}:/{f} {p2}:/{f}".format(p1=projID1, f=fname1, p2=projID2))
            words = output.split()
            self.assertTrue("already" in words)
            self.assertTrue("existed" in words)
            self.assertTrue("destination" in words)
            # uncomment this check, once the implementation improves
            #self.assertTrue(fileID1 in words)

        file_with_same_name()
        cp_rename()
        multiple_args()
        cp_dir()
        #copy_empty_folder_on_existing_folder()
        #copy_folder_on_existing_folder()
        copy_overwrite_wierd_error()

        #cleanup
        rm_project(projID1)
        rm_project(projID2)

    # This case did not work before
    def test_dx_cp_found_in_other_project(self):
        ''' Copy a file-id, where the file is not located in the default project-id.

        Main idea: create projects A and B. Create a file in A, and copy it to project B,
        -without- specifying a source project.
        '''
        projID1 = create_proj()
        projID2 = create_proj()

        file_id, _ = create_file_in_project(projID1)
        run('dx cp ' + file_id + ' ' + projID2)

        #cleanup
        rm_project(projID1)
        rm_project(projID2)

    # This case did not work before
    @unittest.skipUnless(testutil.TEST_ENV,
                         'skipping test that would clobber your local environment')
    def test_dx_cp_no_env(self):
        ''' Try to copy a file when the context is empty.
        '''
        # create a file
        testdir = tempfile.mkdtemp()
        with tempfile.NamedTemporaryFile(dir=testdir) as fd:
            fd.write("foo")
            fd.flush()
            file_id = run("dx upload " + fd.name + " --brief --wait").strip()
            self.assertTrue(file_id.startswith('file-'))

        # Unset environment
        from dxpy.utils.env import write_env_var
        write_env_var('DX_PROJECT_CONTEXT_ID', None)
        del os.environ['DX_PROJECT_CONTEXT_ID']
        self.assertNotIn('DX_PROJECT_CONTEXT_ID', run('dx env --bash'))

        # Copy the file to a new project.
        # This should work even though the context is not set.
        projID = create_proj()
        run('dx cp ' + file_id + ' ' + projID)

        #cleanup
        rm_project(projID)

if __name__ == '__main__':
    if 'DXTEST_FULL' not in os.environ:
        sys.stderr.write(
            'WARNING: env var DXTEST_FULL is not set; tests that create apps or run jobs will not be run\n')
    unittest.main()
