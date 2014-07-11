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

'''
This module provides support for file download and upload. It calculates the
   location of the input and output directories. It also has a utility for parsing
   the job input file ('job_input.json').

We use the following shorthands
   <idir> == input directory     $HOME/in
   <odir> == output directory    $HOME/out

A simple example of the job input, when run locally, is:

{
    "seq2": {
        "$dnanexus_link": {
            "project": "project-1111",
            "id": "file-1111"
        }
    }, 
    "seq1": {
        "$dnanexus_link": {
            "project": "project-2222",
            "id": "file-2222"
        }
    }
    "blast_args": "", 
    "evalue": 0.01
}

The first two elements are files {seq1, seq2}, the other elements are
{blast_args, evalue}. The file for seq1,seq2 should be saved into:
<idir>/seq1/<filename>
<idir>/seq2/<filename>

An example for a shell command that would create these arguments is:
    $ dx run coolapp -iseq1=NC_000868.fasta -iseq2=NC_001422.fasta
It would run an app named "coolapp", with file arguments for seq1 and seq2. Both NC_*
files should have been uploaded to the cloud. File seq1 is supposed to appear in
the execution environment at path:  <idir>/seq1/NC_000868.fasta

File Arrays

{
    "reads": [{
        "$dnanexus_link": {
            "project": "project-3333",
            "id": "file-3333"
        }
    }, 
    {
        "$dnanexus_link": {
            "project": "project-4444",
            "id": "file-4444"
        }
    }]
}

This is a file array with two files. Running a command like this:
    $ dx run coolapp -ireads=A.fastq -ireads=B.fasta
will download into the execution environment:
<idir>/reads/A.fastq
             B.fastq

'''


import json, os
import dxpy
from ..exceptions import DXError
    
def get_input_dir():
    '''
    :rtype string
    :returns path to input directory

    Returns the input directory, where all inputs are downloaded
    '''
    home_dir = os.environ.get('HOME')
    idir = os.path.join(home_dir, 'in')
    return idir

def get_output_dir():
    '''
    :rtype string
    :returns path to output directory

    Returns the output directory, where all outputs are created, and
    uploaded from
    '''
    home_dir = os.environ.get('HOME')
    odir = os.path.join(home_dir, 'out')
    return odir

def get_input_json_file():
    """
    :rtype : string
    :returns: path to input JSON file
    """
    home_dir = os.environ.get('HOME')
    return os.path.join(home_dir, "job_input.json")

def get_output_json_file():
    """
    :rtype : string
    :returns : Path to output JSON file
    """
    home_dir = os.environ.get('HOME')
    return os.path.join(home_dir, "job_output.json")

def ensure_dir(path):
    """
    :param path: path to directory to be created

    Create a directory if it does not already exist.
    """
    if not os.path.exists(path):
        # path does not exist, create the directory
        os.mkdir(path)
    else:
        # The path exists, check that it is not a file
        if os.path.isfile(path):
            raise Exception("Path %s already exists, and it is a file, not a directory" % path)

def make_unix_filename(fname):
    """
    :param fname: filename
    :return: a valid unix filename
    :rtype: string

    The *fname* is just the file name, not the full path (e.g., xxx in /zzz/yyy/xxx).
    The problem being solved here is that *fname* is just a python string, it
    may contain characters that are invalid for a file name. For example, unicode chars, or
    any of these: ".?|!"

    Currently, all we do is replace the slashes, like in other places in the code.
    """
    if True:
        return fname.replace('/', '%2F')
    else:
        """ Normalize a string. Accept all alphanumeric characters, and "_-.", all
        other characters are converted into hyphens. Then, add for some bad names (for example,
        ".", "..").
        """
        bad_filenames = [".", ".."]
        valid_chars = "_-."
        retval=''
        for c in fname:
            if c in valid_chars:
                retval += c
            elif c.isalnum():
                retval += c
            else:
                retval += '_'
        # sanity check for filenames
        if len(retval) == 0:
            raise DXError("Empty filename origin{}".format(fname))
        if retval in bad_filenames:
            raise DXError("Normalized filename {norm} is invalid, original name={org}".format(retval, fname))
        return retval

def get_job_input_filenames(idir):
    """
    :param idir: input directory

    Extract list of files, returns a set of directories to create, and
    a set of files, with sources and destinations. The paths created are
    absolute, they include *idir*
    """
    job_input_file = get_input_json_file()
    with open(job_input_file) as fh:
        job_input = json.load(fh)
        files = []
        dirs = set()  # directories to create under <idir>
        
        # Local function for adding a file to the list of files to be created
        # for example: 
        #    iname == "seq1"
        #    value == { "$dnanexus_link": {
        #       "project": "project-BKJfY1j0b06Z4y8PX8bQ094f", 
        #       "id": "file-BKQGkgQ0b06xG5560GGQ001B"
        #    }
        def add_file(iname, value):
            handler = dxpy.get_handler(value)
            if not isinstance(handler, dxpy.DXFile):
                return
            filename = make_unix_filename(handler.name)
            files.append({'trg_fname': os.path.join(idir, iname, filename),
                         'trg_dir': os.path.join(idir, iname),
                         'src_file_id': handler.id,
                         'iname': iname})
            dirs.add(iname)

        for input_name, value in job_input.iteritems():
            if dxpy.is_dxlink(value):
                # This is a single file
                add_file(input_name, value)
            elif isinstance(value, list):
                # This is a file array, we use the field name as the directory
                for link in value:
                    handler = dxpy.get_handler(link)
                    if isinstance(handler, dxpy.DXFile):
                        add_file(input_name, link)
                    else:
                        # we need to make sure this is a file. Is it possible that it won't be?
                        print("Warning: link={} is not a file link".format(link))
        return dirs, files

def get_input_spec():
    ''' Extract the inputSpec, if it exists
    '''
    input_spec = None
    if 'DX_JOB_ID' in os.environ:
        # works in the cloud, not locally
        # print("found the job id");
        job_desc = dxpy.describe(dxpy.JOB_ID)
        desc = dxpy.describe(job_desc.get("app", job_desc.get("applet")))
        if "inputSpec" in desc:
            input_spec = desc["inputSpec"]
    elif 'DX_TEST_DXAPP_JSON' in os.environ:
        # works only locally
        path_to_dxapp_json = os.environ['DX_TEST_DXAPP_JSON']
        with open(path_to_dxapp_json, 'r') as fd:
            dxapp_json = json.load(fd)
            input_spec = dxapp_json.get('inputSpec')

    # convert to a dictionary. Each record in the output spec
    # has {name, class, optional} attributes.
    if input_spec is None:
        return {}

    # for each field name, we want to know its class, and if it
    # is optional
    recs = {}
    for spec in input_spec:
        name = spec['name']
        recs[name] = {'class': spec['class']}
        recs[name]['optional'] = spec.get('optional', False)
    return recs
