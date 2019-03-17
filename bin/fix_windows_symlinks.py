#!/usr/bin/env python
# fix_windows_symlinks.py
# Copyright (c) 2013-2019 Pablo Acosta-Serafini
# See LICENSE for details
# pylint: disable=C0111

# Standard library imports
from __future__ import print_function
import filecmp
import os
import platform
import shutil
import subprocess
import sys


###
# Functions
###
def read_file(fname):
    """Read file in Python 2 or Python 3."""
    if sys.hexversion < 0x03000000:
        with open(fname, "r") as fobj:
            return fobj.readlines()
    else:
        try:
            with open(fname, "r") as fobj:
                return fobj.readlines()
        except UnicodeDecodeError:
            with open(fname, "r", encoding="utf-8") as fobj:
                return fobj.readlines()


def resolve_win_symlinks():
    """Follow Git 'symlink' under Windows."""
    # pylint: disable=R0912,R0914
    if platform.system().lower() == "windows":
        pkg_dir = os.path.dirname(os.path.dirname(__file__))
        pobj = subprocess.Popen(
            ["git", "ls-files", "-s"], stdout=subprocess.PIPE, stderr=subprocess.STDOUT
        )
        lines, _ = pobj.communicate()
        if sys.hexversion >= 0x03000000:
            lines = lines.decode("utf-8")
        lines = [item.rstrip() for item in lines.split("\n") if item.rstrip()]
        symlinks = []
        for line in lines:
            mode, _, _, fname = line.split()
            if mode == "120000":
                symlinks.append(os.path.join(pkg_dir, fname))
        sdict = {}
        for fname in symlinks:
            line = read_file(fname)[0].strip()
            src = os.path.abspath(
                os.path.normpath(os.path.join(os.path.dirname(fname), line))
            )
            sdict[src] = os.path.abspath(os.path.normpath(fname))
        for src, dest in sdict.items():
            print("{src} -> {dest}".format(src=src, dest=dest))
            try:
                os.remove(dest)
            except OSError:
                pass
            shutil.copy(src, dest)
            if not filecmp.cmp(src, dest):
                raise OSError("Symlink fix failed")


if __name__ == "__main__":
    resolve_win_symlinks()
