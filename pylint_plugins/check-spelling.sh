#!/bin/bash
# check-spelling.sh
# Copyright (c) 2018-2019 Pablo Acosta-Serafini
# See LICENSE for details
# pylint: disable=C0111

# shellcheck disable=SC2094
ddir=$(readlink -f "$1")
fname=$(readlink -f "$2")
aspell --lang=en --personal="${ddir}" list < "${fname}" | \
    while read -r word; do \
        grep -on "\<${word}\>" "${fname}";
    done
