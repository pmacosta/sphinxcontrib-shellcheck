# test_sphinxcontrib.py
# Copyright (c) 2018-2019 Pablo Acosta-Serafini
# See LICENSE for details
# pylint: disable=C0111,E0401,E0611,E1101,R1702,W0212,W0703

# Standard library import
from __future__ import print_function
import os
import re

# PyPI imports
import sphinx.cmd.build

# Intra-package imports
from shellcheck import _tostr, which

###
# Global variables
###
SDIR = os.path.join(os.path.dirname(os.path.abspath(__file__)), "support")
CONF_FNAME = os.path.join(SDIR, "conf.py")


###
# Helper functions
###
def _get_ex_msg(obj):
    """Get exception message."""
    return obj.value.args[0] if hasattr(obj, "value") else obj.args[0]


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
    try:
        ret_code = sphinx.cmd.build.main(argv[1:])
    except Exception as obj:
        lines = _tostr(_get_ex_msg(obj))
        ret_code = 1
        return ret_code, lines
    fname = os.path.join(dir2, "output.txt")
    lines = []
    if os.path.exists(fname):
        with open(fname, "r") as fobj:
            lines = fobj.readlines()
    return ret_code, lines


###
# Test functions
###
def test_shellcheck_error():  # noqa: D202
    """Test main sphinx extension."""

    def validate(opt):
        ret = run_sphinx(["-D", opt])
        assert ret == (2, [])

    validate("shellcheck_dialects=bash,xonsh")
    validate('shellcheck_executable="not_an_exe"')
    validate('shellcheck_prompt="###"')
    validate("shellcheck_debug=5")


def test_shellcheck():
    """Test main sphinx extension."""
    ret_code, act_lines = run_sphinx()
    if ret_code:
        print("act_lines:" + os.linesep + os.linesep.join(act_lines))
    assert ret_code == 0
    act_lines = [act_line.rstrip() for act_line in act_lines]
    # For version 0.3.3
    ref_lines_1 = [
        "README.rst: " + os.path.join(SDIR, "README.rst"),
        (
            "README.rst: Line 32, column 11 [2164]: "
            "Use 'cd ... || exit' or 'cd ... || return' in case cd fails."
        ),
        "README.rst: Line 34, column 17 [2154]: myvar is referenced but not assigned.",
        "api.rst: " + os.path.join(SDIR, "mymodule.py"),
        (
            "api.rst: Line 30, column 11 [1091]: Not following: "
            "myfile.sh was not specified as input (see shellcheck -x)."
        ),
    ]
    # For version 0.4.4
    ref_lines_2 = [
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
    ref_lines_3 = [
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
    flag = any(
        [
            (ref_lines_1 == act_lines),
            (ref_lines_2 == act_lines),
            (ref_lines_3 == act_lines),
        ]
    )
    if not flag:
        print("Actual")
        print("Number of lines: {}".format(len(act_lines)))
        print(act_lines)
        for case, value in zip([1, 2, 3], [ref_lines_1, ref_lines_2, ref_lines_3]):
            print("Reference {}".format(case))
            print("Number of lines: {}".format(len(value)))
            print(value)
            print(value == act_lines)
            print("---")
            for line_1, line_2 in zip(value, act_lines):
                print(repr(line_1))
                print(repr(line_2))
                if line_1 != line_2:
                    if len(line_1) != len(line_2):
                        print(
                            "Length difference: {0} vs. {1}".format(
                                len(line_1), len(line_2)
                            )
                        )
                    else:
                        for num, (char_1, char_2) in enumerate(zip(line_1, line_2)):
                            if char_1 != char_2:
                                print(
                                    (
                                        "First difference at character "
                                        "{0}, {1} vs. {2}"
                                    ).format(num, char_1, char_2)
                                )
            print("---")
    assert flag
