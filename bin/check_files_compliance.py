#!/usr/bin/env python
# check_files_compliance.py
# Copyright (c) 2018-2019 Pablo Acosta-Serafini
# See LICENSE for details
# pylint: disable=C0103,C0111,C0413,R0205,R0903,R0912,R0914,W0622

# Standard library imports
from __future__ import print_function
import argparse
import glob
import os
import sys

# Intra-package imports
PYLINT_PLUGINS_DIR = os.environ["PYLINT_PLUGINS_DIR"]
if PYLINT_PLUGINS_DIR:
    sys.path.append(PYLINT_PLUGINS_DIR)
import aspell
import header
import pylint_codes


###
# Functions
###
def pkg_files(sdir, mdir, files, extensions):
    """Return package files of a given extension."""
    pkgdir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    files = [os.path.join(pkgdir, item) for item in files]
    # Define directories to look files in
    fdirs = [
        os.path.join(mdir, ""),
        os.path.join(mdir, "bin"),
        os.path.join(sdir, "sphinxcontrib"),
        os.path.join(mdir, "tests"),
        os.path.join(mdir, "tests", "support"),
    ]
    # Defines files to be excluded from check
    efiles = [
        os.path.join(mdir, "LICENSE"),
        os.path.join(mdir, "data", "whitelist.en.pws"),
    ]
    # Processing
    for fdir in fdirs:
        for item in glob.glob(os.path.join(fdir, "*")):
            if (
                (os.path.splitext(item)[1] in extensions)
                and (not os.path.isdir(item))
                and (item not in efiles)
            ):
                if (not files) or (files and (item in files)):
                    yield item


def check_header(sdir, mdir, files, no_print=False):
    """Check that all files have header line and copyright notice."""
    # Processing
    fdict = {
        ".py": "#",
        ".rst": "..",
        ".yml": "#",
        ".ini": "#",
        ".in": "#",
        ".sh": "#",
        ".cfg": "#",
        "": "#",
    }
    errors = False
    for fname in pkg_files(sdir, mdir, files, list(fdict)):
        extension = os.path.splitext(fname)[1]
        comment = fdict[extension]
        node = Node(fname)
        linenos = header.check_header(node, comment)
        if linenos:
            errors = True
            if not no_print:
                print(
                    "File {0} does not have a standard header (line{1} {2})".format(
                        fname,
                        "s" if len(linenos) > 1 else "",
                        ", ".join(str(item) for item in linenos),
                    )
                )
    if (not errors) and (not no_print):
        print("All files header compliant")
    return errors


def check_pylint(sdir, mdir, files, no_print=False):
    """Check that there are no repeated Pylint codes per file."""
    errors = False
    self = PylintCodes()
    for fname in pkg_files(sdir, mdir, files, ".py"):
        node = Node(fname)
        header_printed = False
        for code, lineno in pylint_codes.check_pylint(self, node):
            errors = True
            if not no_print:
                if not header_printed:
                    header_printed = True
                    print("File {0}".format(fname))
                if code == "pylint-disable-codes-at-eol":
                    print("   Line {0} (EOL)".format(lineno + 1))
                if code == "repeated-pylint-disable-codes":
                    print("   Line {0} (repeated)".format(lineno + 1))
                if code == "unsorted-pylint-disable-codes":
                    print("   Line {0} (unsorted)".format(lineno + 1))
    if (not errors) and (not no_print):
        print("All files Pylint compliant")
    return errors


def check_aspell(sdir, mdir, files, no_print=False):
    """Check files word spelling."""
    errors = False
    if aspell.which("aspell"):
        for fname in pkg_files(sdir, mdir, files, [".py", ".rst"]):
            node = Node(fname)
            header_printed = False
            for lineno, tword in aspell.check_spelling(node):
                errors = True
                if not no_print:
                    if not header_printed:
                        header_printed = True
                        print("File {0}".format(fname))
                    print("   Line {0}: {1}".format(lineno, tword[0]))
        if (not errors) and (not no_print):
            print("All files free of typos")
    else:
        print("Files spell check omitted, aspell could not be found")
    return errors


###
# Classes
###
class Node(object):
    """Mimic Pylint node class for plugin functions reusability."""

    def __init__(self, file):
        """Initialize class."""
        self.file = file

    def stream(self):
        """Stream file lines."""
        return Stream(self.file)


class PylintCodes(object):
    """Mimic codes in Pylint checker."""

    REPEATED_PYLINT_CODES = "repeated-pylint-disable-codes"
    PYLINT_CODES_AT_EOL = "pylint-disable-codes-at-eol"
    UNSORTED_PYLINT_CODES = "unsorted-pylint-disable-codes"


class Stream(object):
    """Create file stream context manager."""

    def __init__(self, file):  # noqa
        self.file = file

    def __enter__(self):  # noqa
        with open(self.file, "r") as obj:
            for line in obj:
                yield line

    def __exit__(self, exc_type, exc_value, exc_tb):  # noqa
        return not exc_type is not None


###
# Entry point
###
if __name__ == "__main__":
    PKG_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    PARSER = argparse.ArgumentParser(
        description="Perform various checks on package files"
    )
    PARSER.add_argument(
        "-s", "--spell", help="check files spelling", action="store_true"
    )
    PARSER.add_argument(
        "-t", "--top", help="check files top (headers)", action="store_true"
    )
    PARSER.add_argument(
        "-p", "--pylint", help="check files PyLint lines", action="store_true"
    )
    PARSER.add_argument("-q", "--quiet", help="suppress messages", action="store_true")
    PARSER.add_argument(
        "-d",
        "--source-dir",
        help="source files directory (default ../sphinxcontrib)",
        nargs=1,
        default=PKG_DIR,
    )
    PARSER.add_argument(
        "-m",
        "--misc-dir",
        help="miscellaneous files directory (default ../)",
        nargs=1,
        default=PKG_DIR,
    )
    PARSER.add_argument("files", help="Files to check", nargs="*")
    ARGS = PARSER.parse_args()
    SOURCE_DIR = (
        ARGS.source_dir[0] if isinstance(ARGS.source_dir, list) else ARGS.source_dir
    )
    MISC_DIR = ARGS.misc_dir[0] if isinstance(ARGS.misc_dir, list) else ARGS.misc_dir
    TERRORS = False
    if not ARGS.quiet:
        print("Source directory: {0}".format(SOURCE_DIR))
        print("Miscellaneous directory: {0}".format(MISC_DIR))
    if ARGS.spell:
        TERRORS = TERRORS or check_aspell(SOURCE_DIR, MISC_DIR, ARGS.files, ARGS.quiet)
    if ARGS.top:
        TERRORS = TERRORS or check_header(SOURCE_DIR, MISC_DIR, ARGS.files, ARGS.quiet)
    if ARGS.pylint:
        TERRORS = TERRORS or check_pylint(SOURCE_DIR, MISC_DIR, ARGS.files, ARGS.quiet)
    if TERRORS:
        sys.exit(1)
