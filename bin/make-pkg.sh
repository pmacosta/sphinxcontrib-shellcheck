#!/bin/bash

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

cwd=${PWD}
pkg_dir=$(dirname "$(current_dir "${BASH_SOURCE[0]}")")
cd "${pkg_dir}" || exit 1
python setup.py sdist
cd "${cwd}" || exit 1
