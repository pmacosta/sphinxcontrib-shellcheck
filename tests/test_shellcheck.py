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
# Global variables
###
SDIR = os.path.join(os.path.dirname(os.path.abspath(__file__)), "support")
CONF_FNAME = os.path.join(SDIR, "conf.py")


###
# Helper functions
###
def run_sphinx(extra_argv=None):
    extra_argv = [] if extra_argv is None else extra_argv
    sdir = os.path.join(os.path.dirname(os.path.abspath(__file__)), "support")
    dir1 = os.path.join(sdir, "_build", "doctrees")
    dir2 = os.path.join(sdir, "_build", "shellcheck")
    exe = shellcheck._which("sphinx-build")
    argv = (
        [exe]
        + extra_argv
        + [
            "--no-color",
            "-Q",
            "-W",
            "-a",
            "-E",
            "-b",
            "shellcheck",
            "-d",
            dir1,
            sdir,
            dir2,
        ]
    )
    argv[0] = re.sub(r"(-script\.pyw?|\.exe)?$", "", argv[0])
    ret_code = sphinx.cmd.build.main(argv[1:])
    fname = os.path.join(dir2, "output.txt")
    with open(fname, "r") as fobj:
        lines = fobj.readlines()
    return ret_code, lines


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


def test_shellcheck_error():
    """Test main sphinx extension."""
    ret = run_sphinx(["-D", 'shellcheck_executable="not_an_exe"'])
    assert ret == (2, [])


def test_shellcheck():
    """Test main sphinx extension."""
    ret_code, act_lines = run_sphinx()
    assert ret_code == 0
    act_lines = [act_line.rstrip() for act_line in act_lines]
    ref_lines = [
        "README.rst: " + os.path.join(SDIR, "README.rst"),
        "README.rst: Line 32, column 11 [2164]: Use cd ... || exit in case cd fails.",
        "README.rst: Line 34, column 17 [2154]: myvar is referenced but not assigned.",
        "api.rst: " + os.path.join(SDIR, "mymodule.py"),
        (
            "api.rst: Line 30, column 11 [1091]: Not following: "
            "myfile.sh was not specified as input (see shellcheck -x)."
        ),
    ]
    assert ref_lines == act_lines