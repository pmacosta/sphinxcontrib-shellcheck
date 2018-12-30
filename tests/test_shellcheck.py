# test_shellcheck.py
# Copyright (c) 2018 Pablo Acosta-Serafini
# See LICENSE for details
# pylint: disable=C0111,E0401,E0611,E1101,W0212

# Standard library import
from __future__ import print_function
import os
import re

# PyPI imports
import sphinx.cmd.build

# Intra-package imports
from shellcheck import which

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
    exe = which("sphinx-build")
    argv = (
        [exe]
        + extra_argv
        + [
            "--no-color",
            "-Q",
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
    lines = []
    if os.path.exists(fname):
        with open(fname, "r") as fobj:
            lines = fobj.readlines()
    return ret_code, lines


# Test functions
###
def test_shellcheck_error():
    """Test main sphinx extension."""
    def validate(opt):
        ret = run_sphinx(["-D", opt])
        assert ret == (2, [])
    validate('shellcheck_dialects=bash,xonsh')
    validate('shellcheck_executable="not_an_exe"')
    validate('shellcheck_prompt="###"')
    validate('shellcheck_debug=5')


def test_shellcheck():
    """Test main sphinx extension."""
    ret_code, act_lines = run_sphinx()
    assert ret_code == 0
    act_lines = [act_line.rstrip() for act_line in act_lines]
    # For version 0.4.4
    ref_lines_1 = [
        "README.rst: " + os.path.join(SDIR, "README.rst"),
        "README.rst: Line 32, column 11 [2164]: Use cd ... || exit in case cd fails.",
        "README.rst: Line 34, column 17 [2154]: myvar is referenced but not assigned.",
        "api.rst: " + os.path.join(SDIR, "mymodule.py"),
        (
            "api.rst: Line 30, column 11 [1091]: Not following: "
            "myfile.sh was not specified as input (see shellcheck -x)."
        ),
    ]
    # For version 0.6
    ref_lines_2 = [
        "README.rst: " + os.path.join(SDIR, "README.rst"),
        (
            "README.rst: Line 32, column 11 [2164]: "
            "Use 'cd ... || exit' or 'cd ... || return' in case cd fails."
        ),
        "README.rst: Line 34, column 17 [2154]: myvar is referenced but not assigned.",
        "api.rst: " + os.path.join(SDIR, "mymodule.py"),
        (
            "api.rst: Line 30, column 18 [1091]: Not following: "
            "myfile.sh was not specified as input (see shellcheck -x)."
        ),
    ]
    assert any([(ref_lines_1 == act_lines), (ref_lines_2 == act_lines)])
