# mymodule.py
# Copyright (c) 2018 Pablo Acosta-Serafini
# See LICENSE for details
# pylint: disable=C0111

def func1():
    """
    Test sphinxcontrib-shellcheck.

    This function has shell code in its docstring:

    .. code-block:: bash

        $ cd mydir
        $ echo "HELLO"

    """
    return 1


def func2():
    """
    Test sphinxcontrib-shellcheck.

    This function also has shell code in its docstring:

    .. code-block:: bash

        $ cd mydir || exit 1
        $ echo " WORLD!"

    """
    return 2
