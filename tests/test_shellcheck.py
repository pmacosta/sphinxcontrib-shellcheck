# test_shellcheck.py
# Copyright (c) 2018 Pablo Acosta-Serafini
# See LICENSE for details
# pylint: disable=C0111,E0401,E0611,E1101,W0212

# Standard library import
from __future__ import print_function
import os
import re
import uuid

# PyPI imports
import sphinx.cmd.build

# Intra-package imports
import sphinxcontrib.shellcheck as shellcheck


###
# Helper functions
###
def run_sphinx():
    sdir = os.path.join(os.path.dirname(os.path.abspath(__file__)), "support")
    dir1 = os.path.join(sdir, "_build", "doctrees")
    dir2 = os.path.join(sdir, "_build", "shellcheck")
    exe = shellcheck._which("sphinx-build")
    with shellcheck.TmpFile() as fname:
        sphinx_argv = [
            exe,
            "--no-color",
            "-b",
            "shellcheck",
            "-d",
            dir1,
            sdir,
            dir2,
            "-W",
            fname,
        ]
        sphinx_argv[0] = re.sub(r"(-script\.pyw?|\.exe)?$", "", sphinx_argv[0])
        sphinx.cmd.build.main(sphinx_argv[1:])
        with open(fname, "r") as fobj:
            lines = fobj.readlines()
    return lines


###
# Test functions
###
def test_which():
    """Test _which function."""
    fname = os.path.abspath(__file__)
    cwd = os.path.dirname(fname)
    bin_dir = os.path.join(os.path.dirname(cwd), "bin")
    # Put binary directory first in path to make sure scripts there are first ones found
    os.environ["PATH"] = bin_dir + os.pathsep + os.environ["PATH"]
    assert shellcheck._which("make-pkg.sh") == os.path.join(bin_dir, "make-pkg.sh")
    assert shellcheck._which(os.path.join(fname)) == ""
    assert shellcheck._which("_not_a_file_" + str(uuid.uuid4())) == ""


def test_shellcheck():
    """Test main sphinx extension."""
    print(run_sphinx())
