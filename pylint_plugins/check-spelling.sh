#!/bin/bash
# shellcheck disable=SC2094
ddir=$(readlink -f "$1")
fname=$(readlink -f "$2")
aspell --lang=en --personal="${ddir}" list < "${fname}" | \
    while read -r word; do \
        grep -on "\<${word}\>" "${fname}";
    done
