# pkgdata.py
# Copyright (c) 2013-2020 Pablo Acosta-Serafini
# See LICENSE for details
# pylint: disable=C0111

###
# Global variables
###
VERSION_INFO = (1, 1, 0, "final", 0)
SUPPORTED_INTERPS = ["3.5", "3.6", "3.7", "3.8"]
COPYRIGHT_START = 2018
PKG_DESC = "Sphinx extension to lint shell code in documentation"
PKG_LONG_DESC = (
    "The shellcheck Sphinx builder is an extension that uses the `shellcheck"
    + "<https://github.com/koalaman/shellcheck>`_ utility to lint shell code in the"
    + "documentation."
)
COV_EXCLUDE_FILES = [
    "applehelp/*.py",
    "devhelp/*.py",
    "htmlhelp/*.py",
    "jsmath/*.py",
    "qthelp/*.py",
    "serializinghtml/*.py",
]

PKG_PIPELINE_ID = 2


###
# Functions
###
def _make_version(major, minor, micro, level, serial):
    """Generate version string from tuple (almost entirely from coveragepy)."""
    level_dict = {"alpha": "a", "beta": "b", "candidate": "rc", "final": ""}
    if level not in level_dict:
        raise RuntimeError("Invalid release level")
    version = "{0:d}.{1:d}".format(major, minor)
    if micro:
        version += ".{0:d}".format(micro)
    if level != "final":
        version += "{0}{1:d}".format(level_dict[level], serial)
    return version


__version__ = _make_version(*VERSION_INFO)
