#!/bin/bash
# rtest.sh
# Copyright (c) 2018-2020 Pablo Acosta-Serafini
# See LICENSE for details


sdir=$(dirname "${BASH_SOURCE[0]}")
# shellcheck disable=SC1090,SC1091,SC2024
source "${sdir}/functions.sh"
opath=${PATH}
### Unofficial strict mode
set -euo pipefail
IFS=$'\n\t'
finish() {
    export PATH=${opath}
}
trap finish EXIT ERR SIGINT
pyvers=(3.5 3.6 3.7 3.8)
for pyver in ${pyvers[*]}; do
    pdir="${HOME}/python/python${pyver}/bin"
    if [ -d "${pdir}" ]; then
        export PATH=${pdir}:${PATH}
    fi
done
# shellcheck disable=SC2068
PKG_NAME=sphinxcontrib-shellcheck tox -- $@
