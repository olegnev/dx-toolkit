#!/usr/bin/env python
# -*- coding: utf-8 -*-
#
# Copyright (C) 2013-2014 DNAnexus, Inc.
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

import os, sys, unittest, json, tempfile, subprocess, csv, shutil, re, base64, random, time
import pipes
from contextlib import contextmanager
import pexpect

import dxpy
from dxpy.scripts import dx_build_app
from dxpy_testutil import DXTestCase, check_output, temporary_project, select_project
import dxpy_testutil as testutil
from dxpy.packages import requests
from dxpy.exceptions import DXAPIError, EXPECTED_ERR_EXIT_STATUS
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

class TestDXCp(DXTestCase):
    def test_dx_cp_2(self):
        print("Starting")
        def create_file_in_project(trg_proj_id):
            testdir = tempfile.mkdtemp()
            with tempfile.NamedTemporaryFile(dir=testdir) as fd:
                fd.write("foo")
                fd.flush()
                file_id = run("dx upload {fname} --path {trg_proj} --brief --wait ".
                              format(trg_proj=trg_proj_id, fname=fd.name)).strip()
            return file_id

        # setup two projects, source, and target
        project_name = "test_dx_cp_" + str(random.randint(0, 1000000)) + "_" + str(int(time.time() * 1000))
        proj_src = run("dx new project {name} --brief".format(name=project_name)).strip()
        project_name = "test_dx_cp_" + str(random.randint(0, 1000000)) + "_" + str(int(time.time() * 1000))
        proj_trg = run("dx new project {name} --brief".format(name=project_name)).strip()

        print("copying files 1")
        for i in range(1,4):
            file_id = create_file_in_project(proj_src)
            run("dx cp {f} {p}".format(f=file_id, p=proj_trg))

        # make sure all the files were copied
        listing_proj1 = run("dx ls --brief {p}".format(p=proj_src))
        listing_proj2 = run("dx ls --brief {p}".format(p=proj_trg))
        self.assertEqual(listing_proj1, listing_proj2)

        # create including target path
        print("copying files to a directory")
        run("dx mkdir {p}:/foo".format(p=proj_trg))
        for i in range(1,4):
            file_id = create_file_in_project(proj_src)
            run("dx cp {p1}:/{f} {p2}:/foo/".format(p1=proj_src, f=file_id, p2=proj_trg))

        # TODO:
        #  destination folder does not exist
        #     cp  X  Y:/

        # copy an entire directory
        print("copying files 2")
        run("dx cp {p1}:/foo {p2}:/clue".format(p1=proj_trg, p2=proj_src))

        #cleanup
        run("dx rmproject -y {p1} {p2}".format(p1=proj_src, p2=proj_trg))

    def test_dx_cp_found_in_other_project(self):
        ''' Copy a file-id, where the file is not located in the default project-id.

        Main idea: create projects A and B. Create a file in A, and copy it to project B,
        -without- specifying a source project.
        '''
        def create_file(trg_proj_id):
            testdir = tempfile.mkdtemp()
            with tempfile.NamedTemporaryFile(dir=testdir) as fd:
                fd.write("foo")
                fd.flush()
                file_id = run("dx upload {fname} --path {trg_proj} --brief --wait ".
                              format(trg_proj=projID1, fname=fd.name)).strip()
            return file_id

        project_name = "test_dx_cp_" + str(random.randint(0, 1000000)) + "_" + str(int(time.time() * 1000))
        projID1 = run("dx new project {name} --brief".format(name=project_name)).strip()
        project_name = "test_dx_cp_" + str(random.randint(0, 1000000)) + "_" + str(int(time.time() * 1000))
        projID2 = run("dx new project {name} --brief".format(name=project_name)).strip()

        file_id = create_file(projID1)
        run('dx cp ' + file_id + ' ' + projID2)

        #cleanup
        run("dx rmproject -y {p1} {p2}".format(p1=projID1, p2=projID2))


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
        project_name = "test_dx_cp_" + str(random.randint(0, 1000000)) + "_" + str(int(time.time() * 1000))
        projID = run("dx new project {name} --brief".format(name=project_name)).strip()
        run('dx cp ' + file_id + ' ' + projID)

if __name__ == '__main__':
    if 'DXTEST_FULL' not in os.environ:
        sys.stderr.write('WARNING: env var DXTEST_FULL is not set; tests that create apps or run jobs will not be run\n')
    unittest.main()
