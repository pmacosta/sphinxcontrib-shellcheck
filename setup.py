# setup.py
# Copyright (c) 2018-2019 Pablo Acosta-Serafini
# See LICENSE for details
# pylint: disable=C0111,W0122

# Standard library imports
from __future__ import print_function
import io
import os

# PyPI imports
from setuptools import setup, find_packages

###
# Global variables
###
PKG_NAME = "sphinxcontrib-shellcheck"
VERSION_INFO = (1, 0, 9, "final", 0)
INSTALL_MODE_IS_TEST = os.environ.get("SHELLCHECK_TEST_ENV", "")
VERSION_QUERY = os.environ.get("SHELLCHECK_CI_ENV", "")


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


def _read(*filenames, **kwargs):
    """Read plain text file(s)."""
    encoding = kwargs.get("encoding", "utf-8")
    sep = kwargs.get("sep", "\n")
    buf = []
    for filename in filenames:
        with io.open(filename, encoding=encoding) as fobj:
            buf.append(fobj.read())
    return sep.join(buf)


__version__ = _make_version(*VERSION_INFO)

if VERSION_INFO[3] == "alpha":
    DEVSTAT = "3 - Alpha"
elif VERSION_INFO[3] in ["beta", "candidate"]:
    DEVSTAT = "4 - Beta"
else:
    assert VERSION_INFO[3] == "final"
    DEVSTAT = "5 - Production/Stable"

# Actual directory is os.join(sys.prefix, "share", PKG_NAME)
PWD = os.path.dirname(os.path.abspath(__file__))
SHARE_DIR = os.path.join("share", PKG_NAME)
TEST_REQS = ["coverage", "pylint", "pytest>=3.6", "pytest-cov", "pydocstyle"]
if INSTALL_MODE_IS_TEST:
    DATA_FILES = [
        (
            SHARE_DIR,
            [
                os.path.join(PWD, "AUTHORS.rst"),
                os.path.join(PWD, "CHANGELOG.rst"),
                os.path.join(PWD, "LICENSE"),
                os.path.join(PWD, "Makefile"),
                os.path.join(PWD, "MANIFEST.in"),
                os.path.join(PWD, "README.rst"),
                os.path.join(PWD, "tox.ini"),
                os.path.join(PWD, ".headerrc"),
                os.path.join(PWD, ".pydocstyle"),
                os.path.join(PWD, ".pylintrc"),
            ],
        ),
        (
            os.path.join(SHARE_DIR, "bin"),
            [
                os.path.join(PWD, "bin", "cprint.sh"),
                os.path.join(PWD, "bin", "coveragerc_manager.py"),
                os.path.join(PWD, "bin", "fix_windows_symlinks.py"),
                os.path.join(PWD, "bin", "functions.sh"),
                os.path.join(PWD, "bin", "get_pylint_files.py"),
                os.path.join(PWD, "bin", "get-pylint-files.sh"),
                os.path.join(PWD, "bin", "make-pkg.sh"),
                os.path.join(PWD, "bin", "print-env.sh"),
                os.path.join(PWD, "bin", "winnorm_path.py"),
            ],
        ),
        (
            os.path.join(SHARE_DIR, "tests"),
            [os.path.join(PWD, "tests", "test_sphinxcontrib.py")],
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
        (
            os.path.join(SHARE_DIR, "data"),
            [
                os.path.join(PWD, "data", "exclude-spelling"),
                os.path.join(PWD, "data", "exclude-linting"),
                os.path.join(PWD, "data", "whitelist.en.pws"),
            ],
        ),
        (
            os.path.join(SHARE_DIR, "pylint_plugins"),
            [
                os.path.join(PWD, "pylint_plugins", "header.py"),
                os.path.join(PWD, "pylint_plugins", "pylint_codes.py"),
                os.path.join(PWD, "pylint_plugins", "spellcheck.py"),
                os.path.join(PWD, "pylint_plugins", ".headerrc"),
            ],
        ),
        (
            os.path.join(SHARE_DIR, "pylint_plugins", "dicts"),
            [
                os.path.join(PWD, "pylint_plugins", "dicts", "en_US.aff"),
                os.path.join(PWD, "pylint_plugins", "dicts", "en_US.dic"),
            ],
        ),
    ]
    EXTRA_REQS = TEST_REQS
else:
    DATA_FILES = []
    EXTRA_REQS = []

PKG_DIR = os.path.abspath(os.path.dirname(__file__))
LONG_DESCRIPTION = _read(
    os.path.join(PKG_DIR, "README.rst"), os.path.join(PKG_DIR, "CHANGELOG.rst")
)

###
# Processing
###
if not VERSION_QUERY:
    setup(
        name=PKG_NAME,
        version=__version__,
        url="http://shellcheck.readthedocs.io",
        license="MIT",
        author="Pablo Acosta-Serafini",
        author_email="pmasdev@gmail.com",
        description="Sphinx extension to lint shell code blocks",
        long_description=LONG_DESCRIPTION,
        long_description_content_type="text/x-rst",
        install_requires=["decorator", "docutils", "sphinx", "six"] + EXTRA_REQS,
        tests_require=TEST_REQS,
        data_files=DATA_FILES,
        packages=find_packages(),
        zip_safe=False,
        platforms="any",
        namespace_packages=["sphinxcontrib"],
        classifiers=[
            "Programming Language :: Python :: 2.7",
            "Programming Language :: Python :: 3.5",
            "Programming Language :: Python :: 3.6",
            "Programming Language :: Python :: 3.7",
            "Development Status :: " + DEVSTAT,
            "Natural Language :: English",
            "Environment :: Console",
            "Intended Audience :: Developers",
            "License :: OSI Approved :: MIT License",
            "Operating System :: OS Independent",
            "Framework :: Sphinx :: Extension",
            "Topic :: Software Development :: Documentation",
        ],
    )
