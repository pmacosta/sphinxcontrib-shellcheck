#!/bin/bash
# make-pkg.sh
# Copyright (c) 2018-2019 Pablo Acosta-Serafini
# See LICENSE for details
# shellcheck disable=SC1090,SC2046

source "$(dirname "${BASH_SOURCE[0]}")"/functions.sh

cwd=${PWD}
pkg_dir=$(dirname "$(current_dir "${BASH_SOURCE[0]}")")
cd "${pkg_dir}" || exit 1
python setup.py sdist
cd "${cwd}" || exit 1
