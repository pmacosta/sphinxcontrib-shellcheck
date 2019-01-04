#!/bin/bash
# sort-whitelist.sh
# Copyright (c) 2018-2019 Pablo Acosta-Serafini
# See LICENSE for details

fname=$1
tmp1=$(mktemp)
tmp2=$(mktemp)
tail -n +2 "${fname}" | sort -u > "${tmp1}"
lines=$(wc -l "${tmp1}" | cut -d " " -f 1)
echo "personal_ws-1.1 en ${lines} utf-8" > "${tmp2}"
cat "${tmp2}" "${tmp1}" > "${fname}"
rm -rf "${tmp1}" "${tmp2}"
