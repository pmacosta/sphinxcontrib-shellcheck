#!/bin/bash
# Functions
current_dir() {
    local sdir="$1"
    local udir=""
    # Resolve ${sdir} until the file is no longer a symlink
    while [ -h "${sdir}" ]; do
        udir="$(cd -P "$(dirname "${sdir}")" && pwd)"
        sdir="$(readlink "${sdir}")"
        # If ${sdir} was a relative symlink, we need to resolve it
        # relative to the path where the symlink file was located
        [[ "${sdir}" != /* ]] && sdir="${udir}/${sdir}"
    done
    udir="$(cd -P "$(dirname "${sdir}")" && pwd)"
    echo "${udir}"
}
### Unofficial strict mode
set -euo pipefail
IFS=$'\n\t'
cwd=${PWD}
print_banner=0
finish() {
    if [ "${print_banner}" == 0 ]; then
        echo "Cleaning up..."
        print_banner=0
    fi
    cd "${cwd}" || exit 1
    exit "${1:-1}"
}
sdir=$(current_dir "${BASH_SOURCE[0]}")
repo_dir=$(dirname "${sdir}")
# Use pre-commit framework if possible
if [ -f "${repo_dir}/.pre-commit-config.yaml" ]; then
    if which pre-commit &> /dev/null; then
        cd "${repo_dir}" || exit 1
        pre-commit install
        finish 0
    fi
fi
# Default to legacy shell-based framework
git_hooks_dir=${repo_dir}/.git/hooks
hooks=(pre-commit)
cd "${git_hooks_dir}" || exit 1
for hook in ${hooks[*]}; do
	ln -s -f "${sdir}/${hook}" "${hook}"
done
finish 0
