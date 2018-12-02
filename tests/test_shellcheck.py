# test_shellcheck.py
# Copyright (c) 2018 Pablo Acosta-Serafini
# See LICENSE for details
# pylint: disable=C0111,W0212

# Standard library import
from __future__ import print_function
import os
import uuid

# Intra-package imports
import sphinxcontrib.shellcheck as shellcheck


###
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
