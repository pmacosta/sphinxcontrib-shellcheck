# setup.py
# Copyright (c) 2018 Pablo Acosta-Serafini
# See LICENSE for details
# pylint: disable=C0111,W0122

# Standard library imports
import os

# PyPI imports
from setuptools import setup, find_packages

###
# Global variables
###
# From PyPI pplot package
PKG_DIR = os.path.abspath(os.path.dirname(__file__))
VERSION_PY = os.path.join(PKG_DIR, 'sphinxcontrib/version.py')
with open(VERSION_PY) as fobj:
    __version__ = VERSION_INFO = ""
    # Execute the code in version.py.
    exec(compile(fobj.read(), VERSION_PY, 'exec'))
if VERSION_INFO[3] == 'alpha':
    DEVSTAT = "3 - Alpha"
elif VERSION_INFO[3] in ['beta', 'candidate']:
    DEVSTAT = "4 - Beta"
else:
    assert VERSION_INFO[3] == 'final'
    DEVSTAT = "5 - Production/Stable"


###
# Processing
###
setup(
    name='sphinxcontrib-shellcheck',
    version=__version__,
    url='http://shellcheck.readthedocs.io',
    license='MIT',
    author='Pablo Acosta-Serafini',
    author_email='pmasdev@gmail.com',
    description='Sphinx extension to lint shell code blocks',
    long_description='Sphinx extension to lint shell code blocks',
    install_requires=['sphinx'],
    packages=find_packages(),
    zip_safe=False,
    platforms='any',
    namespace_packages=['sphinxcontrib'],
    classifiers=[
        'Programming Language :: Python',
        'Development Status :: '+DEVSTAT,
        'Natural Language :: English',
        'Environment :: Web Environment',
        'Intended Audience :: Developers',
        'License :: MIT',
        'Operating System :: OS Independent',
        'Topic :: Software Development :: Libraries :: Python Modules'
    ],
)
