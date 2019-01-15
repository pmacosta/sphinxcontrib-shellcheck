#!/bin/bash
# shellcheck disable=SC1090,SC1091

# Copyright (c) 2018-2019, Pablo Acosta-Serafini
# All rights reserved.
#
# Redistribution and use in source and binary forms, with or without
# modification, are permitted provided that the following conditions are met:
#
#     * Redistributions of source code must retain the above copyright
#       notice, this list of conditions and the following disclaimer.
#
#     * Redistributions in binary form must reproduce the above copyright
#       notice, this list of conditions and the following disclaimer in the
#       documentation and/or other materials provided with the distribution.
#
#     * Neither the name of the <organization> nor the
#       names of its contributors may be used to endorse or promote products
#       derived from this software without specific prior written permission.
#
# THIS SOFTWARE IS PROVIDED BY THE COPYRIGHT HOLDERS AND CONTRIBUTORS "AS IS" AND
# ANY EXPRESS OR IMPLIED WARRANTIES, INCLUDING, BUT NOT LIMITED TO, THE IMPLIED
# WARRANTIES OF MERCHANTABILITY AND FITNESS FOR A PARTICULAR PURPOSE ARE
# DISCLAIMED. IN NO EVENT SHALL <COPYRIGHT HOLDER> BE LIABLE FOR ANY
# DIRECT, INDIRECT, INCIDENTAL, SPECIAL, EXEMPLARY, OR CONSEQUENTIAL DAMAGES
# (INCLUDING, BUT NOT LIMITED TO, PROCUREMENT OF SUBSTITUTE GOODS OR SERVICES;
# LOSS OF USE, DATA, OR PROFITS; OR BUSINESS INTERRUPTION) HOWEVER CAUSED AND
# ON ANY THEORY OF LIABILITY, WHETHER IN CONTRACT, STRICT LIABILITY, OR TORT
# (INCLUDING NEGLIGENCE OR OTHERWISE) ARISING IN ANY WAY OUT OF THE USE OF THIS
# SOFTWARE, EVEN IF ADVISED OF THE POSSIBILITY OF SUCH DAMAGE.

### Functions

# Find directory where script is
# from http://stackoverflow.com/questions/59895/
# can-a-bash-script-tell-what-directory-its-stored-in)
# BASH_SOURCE[0] is the pathname of the currently executing function or script
# -h True if file exists and is a symbolic link
# cd -P does not follow symbolic links
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

### Processing
cwd=${PWD}
print_banner=0
finish() {
    if [ "${print_banner}" == 0 ]; then
        echo "Cleaning up..."
        print_banner=1
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
    echo "Using default repo config"
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
