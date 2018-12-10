#!/bin/bash

strcat() {
  local IFS=""
  echo -n "$*"
}

env_name=$1
source_dir=$2
share_dir=$3
fname="${source_dir}/.coveragerc_tox_${env_name}"

msg=$(strcat \
    "# .coveragerc_tox to control coverage.py during Tox runs\n" \
    "[report]\n" \
    "show_missing = True\n" \
    "[run]\n" \
    "branch = True\n" \
    "data_file = ${share_dir}/.coverage_${env_name}\n" \
    "include = ${source_dir}/shellcheck.py\n" \
    "omit = ${source_dir}/websupport/*" \
)

mkdir -p "$(dirname "${fname}")"
echo -e "${msg}" > "${fname}"
echo -e "###"
echo -e "# File: ${fname}"
echo -e "###"
cat "${fname}"
