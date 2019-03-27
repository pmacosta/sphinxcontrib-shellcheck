.. README.rst
.. Copyright (c) 2018-2019 Pablo Acosta-Serafini
.. See LICENSE for details

.. role:: bash(code)
	:language: bash

Description
===========

This reStructuredText file is a test vehicle for the shellcheck extension. For
example, the code below should not give any error:

.. code-block:: bash

	$ pip install mypkg

Now a list:

1. Abide by the adopted code of conduct

2. Fork the repository from the host provider:

    .. code-block:: bash

        $ github_user=myname
        $ git clone \
              https://github.com/"${github_user}"/ \
              myrepo.git
        Cloning into 'myrepo'...
        ...
        $ cd myrepo
        $ export MYREPO_DIR=${PWD}
        $ echo "${myvar}"

3. Install the project's Git hooks and build the documentation.
