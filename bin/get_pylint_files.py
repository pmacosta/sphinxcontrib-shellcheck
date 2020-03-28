#!/usr/bin/env python
# get_pylint_files.py
# Copyright (c) 2013-2020 Pablo Acosta-Serafini
# See LICENSE for details
# pylint: disable=C0111

# Standard library imports
from __future__ import print_function
import argparse
from fnmatch import fnmatch
import glob
import os
import sys


###
# Global variables
###
IS_PY3 = sys.hexversion > 0x03000000


###
# Functions
###
def _read_file(fname):
    """Return file lines as strings."""
    with open(fname) as fobj:
        for line in fobj:
            yield _tostr(line).strip()


def _tostr(obj):  # pragma: no cover
    """Convert to string if necessary."""
    return obj if isinstance(obj, str) else (obj.decode() if IS_PY3 else obj.encode())


def _validate_dir(value):
    """Validate directory exists."""
    if not os.path.isdir(value):
        raise argparse.ArgumentTypeError("directory {0} does not exist".format(value))
    return os.path.abspath(value)


def _validate_file(value):
    """Validate file exists."""
    value = os.path.abspath(value)
    if not os.path.exists(value):
        raise argparse.ArgumentTypeError("file {0} does not exist".format(value))
    return value


def main(argv):
    """Return files for linting."""
    repo_dir, source_dir, extra_dir, exclude_fname = setup_cli(argv)
    patterns = []
    if os.path.exists(exclude_fname):
        patterns = [
            os.path.abspath(item.format(**os.environ))
            for item in _read_file(exclude_fname)
        ]
    ret = glob.glob(os.path.join(repo_dir, "*.py"))
    for tdir in [source_dir, extra_dir]:
        for (dirpath, _, fnames) in os.walk(tdir):
            for fname in fnames:
                _, ext = os.path.splitext(fname)
                fname = os.path.join(dirpath, fname)
                if (ext == ".py") and (
                    not any(fnmatch(fname, pattern) for pattern in patterns)
                ):
                    ret.append(fname)
    print(" ".join(sorted(ret)))


def setup_cli(argv):
    """Implement CLI."""
    parser = argparse.ArgumentParser("Create list of files to lint")
    parser.add_argument(
        "-r",
        "--repo-dir",
        help="specify repository directory",
        type=_validate_dir,
        nargs=1,
        required=True,
    )
    parser.add_argument(
        "-s",
        "--source-dir",
        help="specify top package sources directory",
        type=_validate_dir,
        nargs=1,
        required=True,
    )
    parser.add_argument(
        "-e",
        "--extra-dir",
        help="specify package extra directory",
        type=_validate_dir,
        nargs=1,
        required=True,
    )
    parser.add_argument(
        "-x",
        "--exclude",
        help="specify file with glob patterns of files to exclude from linting",
        type=_validate_file,
        nargs=1,
    )
    args = parser.parse_args(argv)
    repo_dir = args.repo_dir[0]
    source_dir = args.source_dir[0]
    extra_dir = args.extra_dir[0]
    exclude_fname = args.exclude[0] if args.exclude else ""
    return repo_dir, source_dir, extra_dir, exclude_fname


if __name__ == "__main__":
    main(sys.argv[1:])
