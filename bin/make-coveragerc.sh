#!/bin/bash
# make-coveragerc.sh
# Copyright (c) 2018-2019 Pablo Acosta-Serafini
# See LICENSE for details

function strcat () {
  local IFS=""
  echo -n "$*"
}

mode=$1
if [ "${mode}" != "tox" ] && [ "${mode}" != "ci" ]; then
    >&2 echo "Unsupported mode: ${mode} (case sensitive)"
fi
mode_msg="Tox"
xml_lines=""
if [ "${mode}" == "ci" ]; then
    mode_msg="CI"
    # Environment variable RESULTS_DIR is defined in the CI environment
    xml_lines="\n[xml]\noutput = ${RESULTS_DIR}/codecoverage/coverage.xml"
fi

env_name=$2
source_dir=$3
share_dir=$4
fname="${source_dir}/.coveragerc_${mode}_${env_name}"

msg=$(strcat \
    "# .coveragerc_${mode} to control coverage.py during ${mode_msg} runs\n" \
    "[report]\n" \
    "show_missing = True\n" \
    "[run]\n" \
    "branch = True\n" \
    "data_file = ${share_dir}/.coverage_${env_name}\n" \
    "include = ${source_dir}/shellcheck.py\n" \
    "omit = ${source_dir}/websupport/*" \
    "${xml_lines}" \
)

mkdir -p "$(dirname "${fname}")"
echo -e "${msg}" > "${fname}"
echo -e "###"
echo -e "# File: ${fname}"
echo -e "###"
cat "${fname}"
echo -e "###"
echo -e "Coverage HTML report, if applicable, in ${share_dir}/share/sphinxcontrib-shellcheck/tests/htmlcov/index.html"
echo -e "###"
