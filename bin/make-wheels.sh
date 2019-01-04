#!/bin/bash
# make-wheels.sh
# Copyright (c) 2018-2019 Pablo Acosta-Serafini
# See LICENSE for details

set -e

# shellcheck disable=SC1090,SC1091
source "$(dirname "${BASH_SOURCE[0]}")/functions.sh"
pkg_dir=$(dirname "$(current_dir "${BASH_SOURCE[0]}")")

cwd=${PWD}
cpath="${PATH}"
finish() {
    cp -rf "${pkg_dir}/MANIFEST.in.test" "${pkg_dir}/MANIFEST.in"
    sed -i -e "s/MANIFEST.in.test/MANIFEST.in/g" "${pkg_dir}/MANIFEST.in"
    export PATH="${cpath}"
    cd "${cwd}" || exit 1
}

trap finish EXIT ERR SIGINT

cp -rf "${pkg_dir}/MANIFEST.in.wheel" "${pkg_dir}/MANIFEST.in"
bin_dir=${pkg_dir}/bin
echo "pkg_dir: ${pkg_dir}"
echo "bin_dir: ${bin_dir}"
cd "${pkg_dir}" || exit 1
vers=(2.7 3.5 3.6 3.7)
for ver in "${vers[@]}"; do
    export PATH=${HOME}/python/python${ver}/bin:${PATH}
    "${bin_dir}/cprint.sh" line cyan "Building Python ${ver} wheel"
    "${HOME}/python/python${ver}/bin/python${ver}" setup.py bdist_wheel --python-tag py"${ver/./}"
done
