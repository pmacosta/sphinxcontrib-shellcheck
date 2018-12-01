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
VERSION_INFO = (1, 0, 0, 'final', 0)


def _make_version(major, minor, micro, level, serial):
    """Generate version string from tuple (almost entirely from coveragepy)."""
    level_dict = {'alpha': 'a', 'beta': 'b', 'candidate': 'rc', 'final':''}
    if level not in level_dict:
        raise RuntimeError('Invalid release level')
    version = '{0:d}.{1:d}'.format(major, minor)
    if micro:
        version += '.{0:d}'.format(micro)
    if level != 'final':
        version += "{0}{1:d}".format(level_dict[level], serial)
    return version


__version__ = _make_version(*VERSION_INFO)

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
