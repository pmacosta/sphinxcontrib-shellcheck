# aspell.py
# Copyright (c) 2018-2019 Pablo Acosta-Serafini
# See LICENSE for details
# pylint: disable=C0111

# Standard library imports
import os
import subprocess
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


def check_spelling(node):
    """Check spelling against whitelist."""
    # pylint: disable=R0914
    fname = os.path.abspath(node.file)
    sdir = os.path.dirname(os.path.abspath(__file__))
    ddir = os.path.join(os.path.dirname(sdir), "data", "whitelist.en.pws")
    script = os.path.join(sdir, "check-spelling.sh")
    ret = []
    if which("aspell") and which("grep"):
        obj = subprocess.Popen(
            [script, ddir, fname], stdout=subprocess.PIPE, stderr=subprocess.PIPE
        )
        lines, _ = obj.communicate()
        lines = [_tostr(line).strip() for line in lines.split()]
        for line in lines:
            lnum, word = int(line.split(":")[0]), line.split(":")[1]
            ret.append((lnum, (word,)))
    return ret


def which(name):
    """Search PATH for executable files with the given name."""
    # Inspired by https://twistedmatrix.com/trac/browser/tags/releases/
    # twisted-8.2.0/twisted/python/procutils.py
    # pylint: disable=W0141
    result = []
    path = os.environ.get("PATH", None)
    if path is None:
        return []
    for pdir in os.environ.get("PATH", "").split(os.pathsep):
        fname = os.path.join(pdir, name)
        if os.path.isfile(fname) and os.access(fname, os.X_OK):
            result.append(fname)
    return result[0] if result else None


###
# Classes
###
class AspellChecker(BaseChecker):
    """
    Check for header compliance.

    A compliant header includes the name of the file in the first usable line, and
    an up-to-date copyright notice.
    """

    __implements__ = IRawChecker

    MISPELLED_WORD = "aspell"

    name = "header-compliance"
    msgs = {"W9904": ("Misspelled word %s", MISPELLED_WORD, "Misspelled word")}
    options = ()

    def process_module(self, node):
        """Process a module. Content is accessible via node.stream() function."""
        for line, args in check_spelling(node):
            self.add_message(self.MISPELLED_WORD, line=line, args=args)


def register(linter):
    """Regiester checker."""
    linter.register_checker(AspellChecker(linter))
