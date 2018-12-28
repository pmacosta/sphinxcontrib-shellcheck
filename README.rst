.. README.rst
.. Copyright (c) 2018 Pablo Acosta-Serafini
.. See LICENSE for details

.. image:: https://badge.fury.io/py/shellcheck-contrib.svg
    :target: https://pypi.org/project/shellcheck-contrib
    :alt: PyPI version

.. image:: https://img.shields.io/pypi/l/shellcheck-contrib.svg
    :target: https://pypi.org/project/shellcheck-contrib
    :alt: License

.. image:: https://img.shields.io/pypi/pyversions/shellcheck-contrib.svg
    :target: https://pypi.org/project/shellcheck-contrib
    :alt: Python versions supported

.. image:: https://img.shields.io/pypi/format/shellcheck-contrib.svg
    :target: https://pypi.org/project/shellcheck-contrib
    :alt: Format

|

.. image::
    https://travis-ci.org/pmacosta/shellcheck-contrib.svg?branch=master

.. image::
    https://ci.appveyor.com/api/projects/status/
    7dpk342kxs8kcg5t/branch/master?svg=true
    :alt: Windows continuous integration

.. image::
    https://codecov.io/github/pmacosta/shellcheck-contrib/coverage.svg?branch=master
    :target: https://codecov.io/github/pmacosta/shellcheck-contrib?branch=master
    :alt: Continuous integration coverage

|

########################
sphinxcontrib-shellcheck
########################

The shellcheck Sphinx builder is an extension that uses the `shellcheck
<https://github.com/koalaman/shellcheck>`_ utility to line shell code in the
documentation.

###########
Interpreter
###########

The extension has been developed and tested with Python 3.5, 3.6 and 3.7 under
Linux (Debian, Ubuntu), and Microsoft Windows

############
Installation
############

The extension is on `PyPI <https://pypi.org>`_, so:

.. code:: console

   $ pip install sphinxcontrib-shellcheck


Add the shellcheck extension to the extension list in your Sphinx
``conf.py`` file to enable it:

.. code:: python

   extensions = [
       ...
       "sphinxcontrib.shellcheck",
       ...
   ]

#####
Usage
#####

For example, if a reStructuredText file ``example.rst`` has the following
content:

.. code:: rst

   Follow these instructions:
   
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

   And all will be good

Then with the extension installed:

.. code:: console

   $ sphinx-build -b shellcheck . _build example.rst
   Running Sphinx v1.8.3
   making output directory...
   building [mo]: targets for 0 po files that are specified
   building [shellcheck]: 1 source files given on command line
   updating environment: 4 added, 0 changed, 0 removed
   reading sources... [100%] index                                                                          
   looking for now-outdated files... none found
   pickling environment... done
   checking consistency... done
   preparing documents... done
   example.rst                                  
   Line 11, column 11 [2164]: Use cd ... || exit in case cd fails.
   Line 13, column 17 [2154]: myvar is referenced but not assigned.
   build succeeded.

#######################
Configuration variables
#######################

These are the configurable aspects of the extension:

* **shellcheck_dialects** (*list or tuple of strings*): shell dialects to be
  linted. The default dialects are those supported by shellcheck, :code:`("sh",
  "bash", "dash", "ksh")`, and only a subset of these is valid.

* **shellcheck_executable** (*string*): name of the shellcheck executable
  (potentially full path to it too). The default is :code:`"shellcheck"`.

* **shellcheck_prompt** (*string*): single character representing the terminal
  prompt. The default is :code:`$`.

* **shellcheck_debug** (*boolean*): flag that indicates whether debug
  information shall be printed via the Sphinx logger (True) or not (False). The
  default is :code:`False`. This configuration option is only useful while
  developing the extension.

#######
License
#######

The MIT License (MIT)

Copyright (c) 2018, Pablo Acosta-Serafini
All rights reserved.

Redistribution and use in source and binary forms, with or without
modification, are permitted provided that the following conditions are met:

    * Redistributions of source code must retain the above copyright
      notice, this list of conditions and the following disclaimer.

    * Redistributions in binary form must reproduce the above copyright
      notice, this list of conditions and the following disclaimer in the
      documentation and/or other materials provided with the distribution.

    * Neither the name of the <organization> nor the
      names of its contributors may be used to endorse or promote products
      derived from this software without specific prior written permission.

THIS SOFTWARE IS PROVIDED BY THE COPYRIGHT HOLDERS AND CONTRIBUTORS "AS IS" AND
ANY EXPRESS OR IMPLIED WARRANTIES, INCLUDING, BUT NOT LIMITED TO, THE IMPLIED
WARRANTIES OF MERCHANTABILITY AND FITNESS FOR A PARTICULAR PURPOSE ARE
DISCLAIMED. IN NO EVENT SHALL <COPYRIGHT HOLDER> BE LIABLE FOR ANY
DIRECT, INDIRECT, INCIDENTAL, SPECIAL, EXEMPLARY, OR CONSEQUENTIAL DAMAGES
(INCLUDING, BUT NOT LIMITED TO, PROCUREMENT OF SUBSTITUTE GOODS OR SERVICES;
LOSS OF USE, DATA, OR PROFITS; OR BUSINESS INTERRUPTION) HOWEVER CAUSED AND
ON ANY THEORY OF LIABILITY, WHETHER IN CONTRACT, STRICT LIABILITY, OR TORT
(INCLUDING NEGLIGENCE OR OTHERWISE) ARISING IN ANY WAY OUT OF THE USE OF THIS
SOFTWARE, EVEN IF ADVISED OF THE POSSIBILITY OF SUCH DAMAGE.
