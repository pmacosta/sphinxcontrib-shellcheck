# header.py
# Copyright (c) 2018-2019 Pablo Acosta-Serafini
# See LICENSE for details
# pylint: disable=C0111

# Standard library imports
from __future__ import print_function
import datetime
import os
import re
import sys

# PyPI imports
from pylint.interfaces import IRawChecker
from pylint.checkers import BaseChecker


###
# Global variables
###
IS_PY3 = sys.hexversion > 0x03000000


###
# Functions
###
def _find_header_ref(fname):
    """Find .headerrc file."""
    curr_dir = ""
    next_dir = os.path.dirname(os.path.abspath(fname))
    while next_dir != curr_dir:
        curr_dir = next_dir
        rcfile = os.path.join(curr_dir, ".headerrc")
        if os.path.exists(rcfile):
            return rcfile
        next_dir = os.path.dirname(curr_dir)
    return ""


def _read_file(fname):
    """Return file lines as strings."""
    with open(fname) as fobj:
        for line in fobj:
            yield _tostr(line).strip()


def _tostr(obj):  # pragma: no cover
    """Convert to string if necessary."""
    return obj if isinstance(obj, str) else (obj.decode() if IS_PY3 else obj.encode())


def check_header(node, comment="#", header_ref=""):
    """Check that all files have header line and copyright notice."""
    # pylint: disable=W0702
    header_ref = header_ref.strip() or _find_header_ref(node.file)
    if not header_ref:
        print(
            "Reference header file .headerrc not found, skipping header check",
            file=sys.stderr,
        )
        return []
    fullname = os.path.basename(os.path.abspath(node.file))
    basename = os.path.basename(os.path.abspath(node.file))
    current_year = datetime.datetime.now().year
    header_lines = []
    for line in _read_file(header_ref):
        header_lines.append(
            line.format(
                comment=comment,
                fullname=fullname,
                basename=basename,
                current_year=current_year,
            )
        )
    linenos = []
    with node.stream() as stream:
        for (num, line), ref in zip(content_lines(stream, comment), header_lines):
            if num > len(header_lines):
                break
            if line != ref:
                linenos.append(num)
    return linenos


def content_lines(stream, comment="#"):
    """Return non-empty lines of a package."""
    shebang_line_regexp = re.compile(r"^#!.*[ \\/](bash|python)$")
    encoding_dribble = "\xef\xbb\xbf"
    encoded = False
    cregexp = re.compile(r"^{0} -\*- coding: utf-8 -\*-\s*".format(comment))
    for num, line in enumerate(stream):
        line = _tostr(line).rstrip()
        if (not num) and line.startswith(encoding_dribble):
            line = line[len(encoding_dribble) :]
        coding_line = (num == 0) and (cregexp.match(line) is not None)
        encoded = coding_line if not encoded else encoded
        shebang_line = (num == int(encoded)) and shebang_line_regexp.match(line)
        if line and (not coding_line) and (not shebang_line):
            yield num + 1, line


###
# Classes
###
class HeaderChecker(BaseChecker):
    """
    Check for header compliance.

    A compliant header includes the name of the file in the first usable line, and
    an up-to-date copyright notice.
    """

    __implements__ = IRawChecker

    NON_COMPLIANT_HEADER = "non-compliant-header"

    name = "header-compliance"
    msgs = {
        "W9900": (
            "Header does not meet code standard",
            NON_COMPLIANT_HEADER,
            (
                "Headers must have the name of the efile in the first usable line, "
                "and an up-to-date copyright notice"
            ),
        )
    }

    options = (
        (
            "header-ref",
            {
                "default": "",
                "type": "string",
                "metavar": "<header reference>",
                "help": "Header reference",
            },
        ),
    )

    def process_module(self, node):
        """Process a module. Content is accessible via node.stream() function."""
        # pylint: disable=E1101
        linenos = check_header(node, header_ref=self.config.header_ref)
        for lineno in linenos:
            self.add_message(self.NON_COMPLIANT_HEADER, line=lineno)


def register(linter):
    """Register checker."""
    linter.register_checker(HeaderChecker(linter))
