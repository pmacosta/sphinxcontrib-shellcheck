# pylint_codes.py
# Copyright (c) 2018-2019 Pablo Acosta-Serafini
# See LICENSE for details
# pylint: disable=C0111

# Standard library imports
import re
import sys

# PyPI imports
from pylint.interfaces import IRawChecker
from pylint.checkers import BaseChecker


###
# Functions
###
def _tostr(line):
    if isinstance(line, str):
        return line
    if sys.hexversion > 0x03000000:
        return line.decode()
    return line.encode()


def check_pylint(self, node):
    """Check that there are no repeated Pylint codes per file."""
    # pylint: disable=R0914
    rec = re.compile
    soline = rec(r"(^\s*)#\s*pylint\s*:\s*disable\s*=\s*([\w|\s|,]+)\s*")
    # Regular expression to get a Pylint disable directive but only
    # if it is not in a string
    template = r"#\s*pylint:\s*disable\s*=\s*([\w|\s|\s*,\s*]+)"
    quoted_eol = rec(r'(.*)(\'|")\s*' + template + r"\s*\2\s*")
    eol = rec(r"(.*)\s*" + template + r"\s*")
    file_tokens = []
    ret = []
    with node.stream() as stream:
        for num, input_line in enumerate(stream):
            input_line = _tostr(input_line).rstrip()
            line_match = soline.match(input_line)
            quoted_eol_match = quoted_eol.match(
                input_line.replace("\\n", "\n").replace("\\r", "\r")
            )
            eol_match = eol.match(input_line)
            if eol_match and (not quoted_eol_match) and (not line_match):
                ret.append((self.PYLINT_CODES_AT_EOL, num + 1))
            if line_match:
                unsorted_tokens = line_match.groups()[1].rstrip().split(",")
                sorted_tokens = sorted(unsorted_tokens)
                if any([item in file_tokens for item in sorted_tokens]):
                    ret.append((self.REPEATED_PYLINT_CODES, num + 1))
                if unsorted_tokens != sorted_tokens:
                    ret.append((self.UNSORTED_PYLINT_CODES, num + 1))
                file_tokens.extend(sorted_tokens)
    return ret


###
# Classes
###
class PylintCodesChecker(BaseChecker):
    """Check Pylint disable codes are unique, sorted and not at end of source line."""

    __implements__ = IRawChecker

    REPEATED_PYLINT_CODES = "repeated-pylint-disable-codes"
    PYLINT_CODES_AT_EOL = "pylint-disable-codes-at-eol"
    UNSORTED_PYLINT_CODES = "unsorted-pylint-disable-codes"

    name = "pylint-codes"
    msgs = {
        "W9901": (
            "Repeated Pylint disable codes",
            REPEATED_PYLINT_CODES,
            "There are repeated Pylint disable codes throughout the file",
        ),
        "W9902": (
            "Pylint disable code(s) at EOL",
            PYLINT_CODES_AT_EOL,
            "There are Pylint disable codes at end of code line",
        ),
        "W9903": (
            "Unsorted Pylint disable codes",
            UNSORTED_PYLINT_CODES,
            "There are unsorted Pylint disable codes",
        ),
    }
    options = ()

    def process_module(self, node):
        # pylint: disable=R0201
        """Process a module. Content is accessible via node.stream() function."""
        for code, lineno in check_pylint(self, node):
            self.add_message(code, line=lineno)


def register(linter):
    """Register checker."""
    linter.register_checker(PylintCodesChecker(linter))
