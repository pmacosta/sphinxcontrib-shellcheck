#!/bin/bash
# shellcheck disable=SC1090,SC1091
# make_wheels.sh
# Copyright (c) 2013-2018 Pablo Acosta-Serafini
# See LICENSE for details

source "$(dirname "${BASH_SOURCE[0]}")/functions.sh"
pkg_dir=$(dirname "$(current_dir "${BASH_SOURCE[0]}")")
sbin_dir=${pkg_dir}/sbin
source "${sbin_dir}"/ipath.sh
cwd=${PWD}
echo "pkg_dir: ${pkg_dir}"
echo "sbin_dir: ${sbin_dir}"
cd "${pkg_dir}" || exit 1
vers=(2.7 3.5 3.6)
for ver in "${vers[@]}"; do
    "${sbin_dir}/cprint.sh" line cyan "Building Python ${ver} wheel"
    "${HOME}/python/python${ver}/bin/python${ver}" setup.py bdist_wheel --python-tag py"${ver/./}"
done
cd "${cwd}" || exit 1
