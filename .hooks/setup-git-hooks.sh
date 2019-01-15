#!/bin/bash
# shellcheck disable=SC1090,SC1091
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
###
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
# Configure Git user name and email
email=0
personal_repo=0
cfg_fname="${sdir}/repo-cfg.sh"
if [ -f "${cfg_fname}" ]; then
    source "${sdir}/repo-cfg.sh"
else
    echo -e "\tConfiguration file not found, using defaults"
fi
if [ "${email}" == 1 ]; then
    if [ "${personal_repo}" == 1 ]; then
        if [ "${PERSONAL_NAME}" != "" ] && [ "${PERSONAL_EMAIL}" != "" ]; then
            echo "Configuring personal Git author information"
            git config user.name "${PERSONAL_NAME}"
            git config user.email "${PERSONAL_EMAIL}"
        fi
    else
        if [ "${WORK_NAME}" != "" ] && [ "${WORK_EMAIL}" != "" ]; then
            echo "Configuring work Git author information"
            git config user.name "${WORK_NAME}"
            git config user.email "${WORK_EMAIL}"
        fi
    fi
fi
finish 0
repo_dir=$(dirname "${sdir}")
# Use pre-commit framework if possible
if [ -f "${repo_dir}/.pre-commit-config.yaml" ]; then
    if which pre-commit &> /dev/null; then
        cd "${repo_dir}" || exit 1
        echo "Setting up pre-commit framework"
        pre-commit install
        finish 0
    fi
fi
# Default to legacy shell-based framework
echo "Setting up shell pre-commit hook"
git_hooks_dir=${repo_dir}/.git/hooks
hooks=(pre-commit)
cd "${git_hooks_dir}" || exit 1
for hook in ${hooks[*]}; do
	ln -s -f "${sdir}/${hook}" "${hook}"
done
finish 0
