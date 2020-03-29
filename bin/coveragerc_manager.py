#!/usr/bin/env python
# coveragerc_manager.py
# Copyright (c) 2013-2020 Pablo Acosta-Serafini
# See LICENSE for details
# pylint: disable=C0111,C0413,W0403

# Standard library imports
from __future__ import print_function
import datetime
import os
import platform
import sys

# Intra-package imports
sys.path.append(os.path.dirname(os.path.abspath(__file__)))
import functions


###
# Functions
###
def _exclude_files(sdir=None):
    ver = 3 if sys.hexversion < 0x03000000 else 2
    isf = ["conftest.py", "pkgdata.py", "compat{0}.py".format(ver)]
    isf += functions.get_coverage_exclude_files()
    if sdir:
        isf = [os.path.join(sdir, item) for item in isf]
    return sorted(isf)


def _write(fobj, data):
    """Do a simple file write."""
    fobj.write(data)


def get_source_files(sdir, inc_init=False):
    """Get Python source files that are not __init__.py and interpreter-specific."""
    exclude_list = _exclude_files()
    fnames = [item for item in os.listdir(sdir) if item.endswith(".py")]
    fnames = [
        fname
        for fname in fnames
        if not any([fname.endswith(item) for item in exclude_list])
    ]
    if not inc_init:
        fnames = [fname for fname in fnames if fname != "__init__.py"]
    return sorted(fnames)


def main(argv):
    """Generate configuration file."""
    # pylint: disable=R0912,R0914,R0915,W0702
    debug = True
    env = argv[0].strip('"').strip("'")
    pkg_name = os.path.basename(
        os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    )
    if "-" in pkg_name:
        pkg_name = pkg_name.split("-")[0]
    print("File: {0}".format(os.path.abspath(__file__)))
    # Unpack command line arguments
    print("Coverage manager")
    print("Package name: {0}".format(pkg_name))
    print("Arguments received: {0}".format(argv))
    if env == "tox":
        print("Tox mode")
        if len(argv[1:]) == 4:
            mode_flag, interp, _, site_pkg_dir, module = argv[1:] + [""]
            if platform.system().lower() == "windows":
                tokens = site_pkg_dir.split("/")
                site_pkg_dir = "\\".join(tokens)
            print("   mode_flag: {0}".format(mode_flag))
            print("   interp: {0}".format(interp))
            print("   site_pkg_dir: {0}".format(site_pkg_dir))
            print("   module: {0}".format(module))
        else:
            mode_flag, interp, _, module = argv[1:] + [""]
            print("   mode_flag: {0}".format(mode_flag))
            print("   interp: {0}".format(interp))
            print("   module: {0}".format(module))
    elif env == "ci":
        print("Continuous integration mode")
        mode_flag, interp, _, site_pkg_dir, module = (
            argv[1],
            argv[2],
            os.environ["REPO_DIR"],
            argv[3],
            "",
        )
        print("   mode_flag: {0}".format(mode_flag))
        print("   interp: {0}".format(interp))
        print("   site_pkg_dir: {0}".format(site_pkg_dir))
        print("   module: {0}".format(module))
    elif env == "local":
        print("Local mode")
        if len(argv[1:]) == 4:
            mode_flag, interp, _, site_pkg_dir, module = (
                argv[1],
                argv[2],
                argv[3],
                argv[3],
                argv[4],
            )
        else:
            mode_flag, interp, _, site_pkg_dir, module = (
                argv[1],
                argv[2],
                argv[3],
                argv[3],
                "",
            )
        print("   mode_flag: {0}".format(mode_flag))
        print("   interp: {0}".format(interp))
        print("   site_pkg_dir: {0}".format(site_pkg_dir))
        print("   module: {0}".format(module))
    # Generate .coveragerc file
    source_dir = os.path.join(site_pkg_dir, pkg_name)
    output_file_name = os.path.join(
        site_pkg_dir, pkg_name, ".coveragerc_{0}_{1}".format(env, interp)
    )
    print("Output file: {0}".format(output_file_name))
    coverage_file_name = os.path.join(
        site_pkg_dir, pkg_name, ".coverage_{0}".format(interp)
    )
    conf_file = []
    conf_file.append(os.path.join(source_dir, "conftest.py"))
    conf_file.append(os.path.join(source_dir, "plot", "conftest.py"))
    if mode_flag == "1":
        lines = []
        lines.append("# File {0}".format(output_file_name))
        lines.append(
            "# .coveragerc_{0} to control coverage.py during {1} runs".format(
                env, env.capitalize()
            )
        )
        lines.append("[report]")
        lines.append("show_missing = True")
        lines.append("[run]")
        lines.append("branch = True")
        lines.append("disable_warnings = no-data-collected")
        lines.append("data_file = {0}".format(coverage_file_name))
        start_flag = True
        # Include modules
        # source_files = get_source_files(os.path.join(site_pkg_dir, pkg_name), True)
        # for file_name in [item for item in source_files]:
        #    start_flag, prefix = (
        #        (False, "include = ") if start_flag else (False, 10 * " ")
        #    )
        #    lines.append(
        #        "{0}{1}".format(
        #            prefix, os.path.join(site_pkg_dir, pkg_name, file_name)
        #        )
        #    )
        start_flag = True
        for file_name in _exclude_files(os.path.join(site_pkg_dir, pkg_name)):
            start_flag, prefix = (False, "omit = ") if start_flag else (False, 7 * " ")
            lines.append("{0}{1}".format(prefix, file_name))
        # Generate XML reports for continuous integration
        if env == "ci":
            lines.append("[xml]")
            lines.append(
                "output = {0}".format(
                    os.path.join(
                        os.environ["RESULTS_DIR"], "codecoverage", "coverage.xml"
                    )
                )
            )
            lines.append("[html]")
            lines.append(
                "directory = {0}".format(
                    os.path.join(os.environ["RESULTS_DIR"], "codecoverage", "htmlcov")
                )
            )
        # Write file
        with open(output_file_name, "w") as fobj:
            _write(fobj, ("\n".join(lines)) + "\n")
        # Echo file
        if debug:
            print("File: {0}".format(output_file_name))
            with open(output_file_name, "r") as fobj:
                print("".join(fobj.readlines()))
        # Generate conftest.py files to selectively
        # skip Python 2 or Python 3 files
        year = datetime.datetime.now().year
        skip_file = (
            "# conftest.py\n"
            "# Copyright (c) 2013-" + str(year) + " Pablo Acosta-Serafini\n"
            "# See LICENSE for details\n"
            "# pylint: disable=C0103,C0111,C0411,E0012\n"
            "import sys\n"
            "collect_ignore = []\n"
            "if sys.hexversion < 0x03000000:\n"
            "    collect_ignore.append('compat3.py')\n"
            "else:\n"
            "    collect_ignore.append('compat2.py')\n"
        )
        with open(conf_file[0], "w") as fobj:
            _write(fobj, skip_file)
    else:
        del_files = conf_file
        del_files.append(output_file_name)
        del_files.append(coverage_file_name)
        try:
            for fname in del_files:
                print("Deleting file {0}".format(fname))
                os.remove(fname)
        except:
            pass


if __name__ == "__main__":
    main(sys.argv[1:])
