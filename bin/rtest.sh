#!/bin/bash
# rtest.sh
# Copyright (c) 2018 Pablo Acosta-Serafini
# See LICENSE for details

opath=${PATH}
export PATH=${HOME}/python/python3.5/bin:${HOME}/python/python3.6/bin:${HOME}/python/python3.7/bin:${PATH}
tox
export PATH=${opath}
