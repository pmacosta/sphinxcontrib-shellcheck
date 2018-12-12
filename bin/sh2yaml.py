#!/usr/bin/env python
# sh2yaml.py
# Copyright (c) 2018 Pablo Acosta-Serafini
# See LICENSE for details
# pylint: disable=C0103,C0111

# Standard library imports
from __future__ import print_function
import argparse
import os
import re
import sys

# Intra-package imports

###
# Functions
###
def block_lines(lines, open_mark, close_mark, keep=False, proc_in_block=None):
    """Remove blocks between given marker lines."""
    # pylint: disable=R0913,R0916
    proc_in_block = (
        proc_in_block if keep and (proc_in_block is not None) else (lambda x: x)
    )
    in_block = False
    for line in lines:
        open_match = open_mark.match(line)
        close_match = close_mark.match(line)
        if ((not keep) and (not in_block) and (open_match is None)) or (
            keep and in_block and (close_match is None)
        ):
            yield proc_in_block(line)
        else:
            in_block = (
                (open_match is not None) if (not in_block) else (close_match is None)
            )
            if keep and (not in_block) and (close_match is None):
                yield line


def clear_verbatim(lines):
    """Remove initial comment marker from lines."""
    line_mark = re.compile(r"(\s*)#(.*)")

    def proc_in_block(item):
        match = line_mark.match(item)
        return "".join(match.groups()) if match else item

    open_mark = re.compile(r"^\s*#\s*<<<\s*VERBATIM\s*", flags=re.IGNORECASE)
    close_mark = re.compile(r"^\s*#\s*>>>\s*VERBATIM\s*", flags=re.IGNORECASE)
    for line in block_lines(lines, open_mark, close_mark, True, proc_in_block):
        yield line


def main(argv):
    """Script entry point."""
    ifname, ofname = setup_cli(argv)
    opath, _ = os.path.split(os.path.abspath(ofname))
    if not os.path.exists(opath):
        try:
            os.makedirs(opath)
        except OSError:
            raise argparse.ArgumentTypeError("Path {0} cannot be created".format(opath))
    with open(ifname, "r") as obj:
        ilines = [iline.rstrip() for iline in obj.readlines()]
    olines = os.linesep.join(
        rename_header(
            remove_shebang(
                remove_shell_linting(
                    preppend_lines(clear_verbatim(remove_exclude_block(ilines)))
                )
            ),
            ifname,
            ofname,
        )
    )
    with open(ofname, "w") as obj:
        obj.write(olines)


def make_dir(fname):
    """Create the directory of a fully qualified file name if it does not exist."""
    file_path, fname = os.path.split(os.path.abspath(fname))
    if not os.path.exists(file_path):
        os.makedirs(file_path)


def preppend_lines(lines):
    """Add initial character, comment or hyphen, if necessary."""
    sh_open = re.compile(r"^\s*(case|for|if|select|while|until)\s+.*")
    sh_close = re.compile(r"^\s*(esac|done|fi)\s*")
    kwre = re.compile(r"^\s*\w+:.*")
    core = re.compile(r"^\s*#.*")
    dare = re.compile(r"^\s*-.*")
    header_done = False
    level = 0
    for line in lines:
        is_keyword = bool(kwre.match(line))
        is_comment = bool(core.match(line))
        plus = bool(sh_open.match(line))
        minus = bool(sh_close.match(line))
        starts_with_dash = bool(dare.match(line))
        header_done = header_done or is_keyword
        if (not line.strip()) or ((not header_done) and is_comment) or starts_with_dash:
            pass  # Yield line as is
        else:
            if is_keyword or (is_comment and line.startswith("  #")):
                pass  # Yield line as is
            elif is_comment:
                line = "  " + line
            else:
                line = "  - " + line if not level else "    " + line
                level = level + (1 if plus else 0) - (1 if minus else 0)
        yield line


def remove_exclude_block(lines, open_mark="#<<<", close_mark="#>>>"):
    """Remove blocks between given marker lines."""
    open_mark = re.compile(r"^\s*#\s*<<<\s*EXCLUDE\s*", flags=re.IGNORECASE)
    close_mark = re.compile(r"^\s*#\s*>>>\s*EXCLUDE\s*", flags=re.IGNORECASE)
    for line in block_lines(lines, open_mark, close_mark, keep=False):
        yield line


def remove_shebang(lines):
    """Remove shell shebang."""
    regexp = re.compile(r"^\s*#!.*/bash")
    for num, line in enumerate(lines):
        match = regexp.match(line)
        if (not num) and bool(match):
            pass
        else:
            yield line


def remove_shell_linting(lines):
    """Remove shell linter code disabling lines."""
    regexp = re.compile(r"^\s*#\s*shellcheck\s*disable\s*=\s*.*")
    for line in lines:
        match = regexp.match(line)
        if not bool(match):
            yield line


def rename_header(lines, ifname, ofname):
    """Print appropriate file name in header."""
    ifname = os.path.basename(ifname).replace(r".", r"\.")
    ofname = os.path.basename(ofname)
    regexp = re.compile(r"^(\s*#\s*)" + ifname + r"\s*")
    for line in lines:
        match = regexp.match(line)
        if bool(match):
            line = match.groups()[0] + ofname
        yield line


def setup_cli(argv):
    """Define command line interface."""
    parser = argparse.ArgumentParser(description="Convert a shell file to Yaml")
    parser.add_argument(
        "-i",
        "--input-file",
        help="input file",
        nargs=1,
        type=valid_existing_file,
        default=None,
    )
    parser.add_argument("-o", "--output-file", help="output file", nargs=1)
    args = parser.parse_args(argv)
    ifname = args.input_file[0]
    ofname = args.output_file[0]
    return ifname, ofname


def valid_existing_file(value):
    """Check file exists."""
    if not os.path.exists(value):
        raise argparse.ArgumentTypeError("File {0} does not exist".format(value))
    return os.path.abspath(value)


if __name__ == "__main__":
    main(sys.argv[1:])
