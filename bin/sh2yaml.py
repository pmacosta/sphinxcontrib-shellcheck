#!/usr/bin/env python
# sh2yaml.py
# Copyright (c) 2018 Pablo Acosta-Serafini
# See LICENSE for details
# pylint: disable=C0103,C0111

# Standard library imports
from __future__ import print_function
import argparse
import os
import re
import sys

# Intra-package imports

###
# Functions
###
def script_lines(lines, open_mark="#<<<", close_mark="#>>>"):
    """Remove blocks between given marker lines."""
    exclude_block = False
    for line in lines:
        if (not exclude_block) and (line.strip() != open_mark):
            yield line
        else:
            exclude_block = (
                (line.strip() == open_mark)
                if (not exclude_block)
                else (line.strip() != close_mark)
            )


def main(argv):
    """Script entry point."""
    ifname, ofname = setup_cli(argv)
    opath, _ = os.path.split(os.path.abspath(ofname))
    if not os.path.exists(opath):
        try:
            os.makedirs(opath)
        except OSError:
            raise argparse.ArgumentTypeError("Path {0} cannot be created".format(opath))
    with open(ifname, "r") as obj:
        ilines = [iline.rstrip() for iline in obj.readlines()]
    olines = []
    for iline in verbatim_lines(script_lines(ilines)):
        print(iline)


def make_dir(fname):
    """Create the directory of a fully qualified file name if it does not exist."""
    file_path, fname = os.path.split(os.path.abspath(fname))
    if not os.path.exists(file_path):
        os.makedirs(file_path)


def setup_cli(argv):
    """Define command line interface."""
    parser = argparse.ArgumentParser(description="Convert a shell file to Yaml")
    parser.add_argument(
        "-i",
        "--input-file",
        help="input file",
        nargs=1,
        type=valid_existing_file,
        default=None,
    )
    parser.add_argument("-o", "--output-file", help="output file", nargs=1)
    args = parser.parse_args(argv)
    ifname = args.input_file[0]
    ofname = args.output_file[0]
    return ifname, ofname


def valid_existing_file(value):
    """Check file exists."""
    if not os.path.exists(value):
        raise argparse.ArgumentTypeError("File {0} does not exist".format(value))
    return os.path.abspath(value)


def verbatim_lines(lines):
    regexp = re.compile(r"^\s*#\s*\[VERBATIM\](.*)")
    for line in lines:
        match = regexp.match(line.lstrip())
        yield match.groups()[0] if match else line


if __name__ == "__main__":
    main(sys.argv[1:])
