#!/usr/bin/env python2.7

import os
import sys
import argparse
import subprocess

parser = argparse.ArgumentParser()
parser.add_argument('demo_file', help='Path to the demo file')

args = parser.parse_args()

with open(args.demo_file, 'r') as demo:
    for line in demo:
        sys.stdout.write("+ " + line)
        os.system('bash -c "read -p \'\'"')
        subprocess.call(line, shell=True)
        print
