#!/usr/bin/env python
# winnorm_path.py
# Copyright (c) 2013-2020 Pablo Acosta-Serafini
# See LICENSE for details
# pylint: disable=C0111

# Standard library imports
from __future__ import print_function
import os
import platform
import re
import sys

# PyPI imports
# Intra-package imports


###
# Global variables
###


###
# Functions
###
def main(arg):
    arg = arg.strip().strip(":")
    regexp = re.compile(r"^((?:[a-zA-Z]:)?[^:]*).*")
    match = regexp.match(arg)
    if not match:
        return arg
    paths = []
    while arg and match:
        path = match.groups()[0]
        paths.append(path.replace("/", os.sep))
        arg = arg[len(path) + 1 :]
        match = regexp.match(arg)
    if arg:
        paths.append(arg.replace("/", os.sep))
    print((";" if platform.system().lower() == "windows" else ":").join(paths))


if __name__ == "__main__":
    main(sys.argv[1])
