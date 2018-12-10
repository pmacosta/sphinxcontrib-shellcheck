# setup.py
# Copyright (c) 2018 Pablo Acosta-Serafini
# See LICENSE for details
# pylint: disable=C0111,W0122

# Standard library imports
from __future__ import print_function
import os

# PyPI imports
from setuptools import setup, find_packages

###
# Global variables
###
PKG_NAME = "sphinxcontrib-shellcheck"
VERSION_INFO = (1, 0, 0, "final", 0)
INSTALL_MODE_IS_TEST = os.environ.get("SHELLCHECK_TEST_ENV", "")
print("SHELLCHECK_TEST_ENV = " + INSTALL_MODE_IS_TEST)


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

if VERSION_INFO[3] == "alpha":
    DEVSTAT = "3 - Alpha"
elif VERSION_INFO[3] in ["beta", "candidate"]:
    DEVSTAT = "4 - Beta"
else:
    assert VERSION_INFO[3] == "final"
    DEVSTAT = "5 - Production/Stable"

# Actual directory is os.join(sys.prefix, 'share', PKG_NAME)
PWD = os.path.dirname(os.path.abspath(__file__))
SHARE_DIR = os.path.join("share", PKG_NAME)
if INSTALL_MODE_IS_TEST:
    DATA_FILES = [
        (
            SHARE_DIR,
            [
                os.path.join(PWD, "AUTHORS.rst"),
                os.path.join(PWD, "CHANGELOG.rst"),
                os.path.join(PWD, "LICENSE"),
                os.path.join(PWD, "MANIFEST.in"),
                os.path.join(PWD, "README.rst"),
                os.path.join(PWD, "tox.ini"),
            ],
        ),
        (
            os.path.join(SHARE_DIR, "bin"),
            [
                os.path.join(PWD, "bin", "make-pkg.sh"),
            ],
        ),
        (
            os.path.join(SHARE_DIR, "tests"),
            [
                os.path.join(PWD, "tests", "test_shellcheck.py"),
                os.path.join(PWD, "tests", "make-coveragerc.sh"),
            ],
        ),
        (
            os.path.join(SHARE_DIR, "tests", "support"),
            [
                os.path.join(PWD, "tests", "support", "README.rst"),
                os.path.join(PWD, "tests", "support", "api.rst"),
                os.path.join(PWD, "tests", "support", "conf.py"),
                os.path.join(PWD, "tests", "support", "index.rst"),
                os.path.join(PWD, "tests", "support", "mymodule.py"),
            ],
        ),
    ]
else:
    DATA_FILES = []


###
# Processing
###
setup(
    name=PKG_NAME,
    version=__version__,
    url="http://shellcheck.readthedocs.io",
    license="MIT",
    author="Pablo Acosta-Serafini",
    author_email="pmasdev@gmail.com",
    description="Sphinx extension to lint shell code blocks",
    long_description="Sphinx extension to lint shell code blocks",
    install_requires=["decorator", "docutils", "sphinx", "six"],
    tests_require=["pytest", "coverage", "pytest-cov"],
    data_files=DATA_FILES,
    packages=find_packages(),
    zip_safe=False,
    platforms="any",
    namespace_packages=["sphinxcontrib"],
    classifiers=[
        "Programming Language :: Python",
        "Development Status :: " + DEVSTAT,
        "Natural Language :: English",
        "Environment :: Web Environment",
        "Intended Audience :: Developers",
        "License :: MIT",
        "Operating System :: OS Independent",
        "Topic :: Software Development :: Libraries :: Python Modules",
    ],
)
