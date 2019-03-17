#!/bin/bash
# get-pylint-files.sh
# Copyright (c) 2013-2019 Pablo Acosta-Serafini
# See LICENSE for details

sdir=$(dirname "${BASH_SOURCE[0]}")
# shellcheck disable=SC1090,SC1091,SC2024
source "${sdir}/functions.sh"
### Unofficial strict mode
set -euo pipefail
IFS=$'\n\t'
#
add_to_output() {
    local ret addition
    ret="$1"
    addition="$2"
    if [ "${ret}" != "" ]; then
        ret="${ret} "
    fi
    ret="${ret}${addition}"
    echo "${ret}"
}
pkg_name=$1
repo_dir=$(readlink -f "$2")
source_dir=$(readlink -f "$3")
extra_dir=$(readlink -f "$4")
#
ret=("${repo_dir}"/setup.py)
fnames="$(\
    cd "${repo_dir}/${pkg_name}" && \
    find . -name "*.py" -printf '%p\n' | sort -u \
)"
for fname in ${fnames[*]}; do
    add_file=1
    if [ "${source_dir}" != "${repo_dir}/${pkg_name}" ]; then
        bname="$(readlink -f "${repo_dir}/${pkg_name}/${fname}")"
        if [ "${bname}" == "${repo_dir}/${pkg_name}/__init__.py" ]; then
            add_file=0
        fi
    fi
    if [ "${add_file}" == 1 ]; then
        ret+=("${source_dir}/${fname}")
    fi
done
if [ -d "${repo_dir}/tests" ]; then
    fnames="$(\
        cd "${repo_dir}/tests" && \
        find . -name "*.py" -printf '%p\n' | sort -u \
    )"
    for fname in ${fnames[*]}; do
        ret+=("${extra_dir}/tests/${fname}")
    done
fi
if [ -d "${repo_dir}/docs" ]; then
    fnames="$(\
        cd "${repo_dir}/docs" && \
        find . -name "*.py" -printf '%p\n' | sort -u \
    )"
    for fname in ${fnames[*]}; do
        ret+=("${extra_dir}/docs/${fname}")
    done
fi
echo "${ret[@]}"
