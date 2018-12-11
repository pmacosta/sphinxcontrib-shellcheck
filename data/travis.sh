#!/bin/bash
# shellcheck disable=SC1090,SC1091,SC1094,SC2155
# travis.sh
# Copyright (c) 2018 Pablo Acosta-Serafini
# See LICENSE for details

#<<<
set -e
tmp_dir=$(mktemp -d)
env_name="travis_test"
echo "Build directory: ${tmp_dir}"
exit_msg_printed=0
function travis_wait () {
    cmd=($@)
    "${cmd[@]}"
}
finish() {
    if [ "${exit_msg_printed}" == 0 ]; then
        exit_msg_printed=1
        echo "Cleaning up"
    fi
    rm -rf "${tmp_dir}"
    if [ "${TRAVIS_PYTHON_VERSION}" != "" ]; then
        rm -rf "${WORKON_HOME:?}/${env_name}"
    fi
}
echo "Sourcing mkvirtualenv"
if [ -f /usr/share/virtualenvwrapper/virtualenvwrapper.sh ]; then
    source /usr/share/virtualenvwrapper/virtualenvwrapper.sh;
    export WORKON_HOME=${HOME}/envs;
elif [ -f /usr/local/bin/virtualenvwrapper.sh ]; then
    source /usr/local/bin/virtualenvwrapper.sh;
    export WORKON_HOME=${HOME}/envs;
else
    >&2 echo "virtualenvwrapper not found"
fi
trap finish EXIT ERR SIGINT
echo "Going to build directory"
cd "${tmp_dir}" || exit 1
echo "Setting environment variables"
export TRAVIS_REPO_SLUG="pmacosta/sphinxcontrib-shellcheck"
export TRAVIS_BUILD_DIR="${tmp_dir}"
export TRAVIS_OS_NAME="linux"
export TRAVIS_PYTHON_VERSION="2.7"
echo "Creating virtual environment"
mkvirtualenv -p "${HOME}"/python/python"${TRAVIS_PYTHON_VERSION}"/bin/python "${env_name}" || true
source "${WORKON_HOME}/${env_name}/bin/activate"
which python
echo "Cloning directory"
git clone --recursive https://pmacosta@bitbucket.org/pmacosta/sphinxcontrib-shellcheck.git "${tmp_dir}"
echo "Start of CI output"
#>>>

#[VERBATIM]os:
#[VERBATIM]  - linux
#[VERBATIM]  # - osx

#[VERBATIM]sudo: required

#[VERBATIM]dist: trusty

#[VERBATIM]language: python

#[VERBATIM]python:
#[VERBATIM]  - "2.7"
#[VERBATIM]  - "3.5"
#[VERBATIM]  - "3.6"
#[VERBATIM]  - "3.7"

#[VERBATIM]before_install:
env
export PYTHONCMD=python
export PYTESTCMD=pytest
export SHELLCHECK_TEST_ENV=1
if [ "${TRAVIS_OS_NAME}" == "osx" ]; then
    export PIPCMD=${PYTHONCMD} -W 'ignore:a true SSLContext object' -m pip;
    export INTERP=py"${TRAVIS_PYTHON_VERSION//./}";
    export PKG_NAME=$(echo ${TRAVIS_REPO_SLUG} | sed -E "s|.*/(.*)|\1|g");
    wget https://repo.continuum.io/archive/Anaconda2-2.4.0-MacOSX-x86_64.sh;
    bash Anaconda2-2.4.0-MacOSX-x86_64.sh -b;
    export PATH=/Users/travis/anaconda2/bin/:${PATH};
    conda update -y conda;
    conda create -y --name "${INTERP}" python="${TRAVIS_PYTHON_VERSION}";
    source activate "${INTERP}";
    export PATH=/Users/travis/anaconda2/envs/${INTERP}/bin:${PATH};
    export PYTHON_SITE_PACKAGES=$(pip show pip | grep "Location" | sed -E "s/^.*Location\W (.*)/\1/g");
    ${PIPCMD} install --disable-pip-version-check --upgrade pip setuptools wheel;
fi
if [ "${TRAVIS_OS_NAME}" == "linux" ]; then
    export PIPCMD=pip;
    export INTERP=py"${TRAVIS_PYTHON_VERSION//./}";
    export PKG_NAME=$(echo ${TRAVIS_REPO_SLUG} | sed -r "s|.*/(.*)|\1|g");
    export PYTHON_SITE_PACKAGES=$(${PIPCMD} show pip | grep "Location" | sed -r "s/^.*Location\W (.*)/\1/g");
fi
###
# Set up environment variables
###
export REPO_DIR=${TRAVIS_BUILD_DIR}
export VIRTUALENV_DIR="$(dirname "$(dirname "$(dirname "${PYTHON_SITE_PACKAGES}")")")"
export BIN_DIR=${VIRTUALENV_DIR}/bin
export EXTRA_DIR=$(python -c "from __future__ import print_function; import sys; print(sys.prefix)")/share/${PKG_NAME}
export SBIN_DIR=${EXTRA_DIR}/bin
export RESULTS_DIR=${REPO_DIR}/results
export SOURCE_DIR=${PYTHON_SITE_PACKAGES}/$(echo "${PKG_NAME}" | sed -r "s/(.*)-.*/\1/g")
export TRACER_DIR=${EXTRA_DIR}/docs/support
export PYTHONPATH=${PYTHONPATH}:${PYTHON_SITE_PACKAGES}:${PYTHON_SITE_PACKAGES}/$(echo "${PKG_NAME}" | sed -r "s/(.*)-.*/\1/g"):${EXTRA_DIR}:${EXTRA_DIR}/tests:${EXTRA_DIR}/docs:${EXTRA_DIR}/docs/support
export COV_FILE=${SOURCE_DIR}/.coveragerc_ci_${INTERP}
export REQUIREMENTS_FILE=${REPO_DIR}/requirements.txt
export AFILE=${EXTRA_DIR}/artifacts_${INTERP}.tar.gz
export PYLINT_PLUGINS_DIR=${EXTRA_DIR}/pylint_plugins
echo "PYTHONCMD=${PYTHONCMD}"
echo "PIPCMD=${PIPCMD}"
echo "PYTESTCMD=${PYTESTCMD}"
echo "INTERP=${INTERP}"
echo "PKG_NAME=${PKG_NAME}"
echo "PYTHON_SITE_PACKAGES=${PYTHON_SITE_PACKAGES}"
echo "REPO_DIR=${REPO_DIR}"
echo "VIRTUALENV_DIR=${VIRTUALENV_DIR}"
echo "BIN_DIR=${BIN_DIR}"
echo "EXTRA_DIR=${EXTRA_DIR}"
echo "SBIN_DIR=${SBIN_DIR}"
echo "RESULTS_DIR=${RESULTS_DIR}"
echo "SOURCE_DIR=${SOURCE_DIR}"
echo "TRACER_DIR=${TRACER_DIR}"
echo "PYTHONPATH=${PYTHONPATH}"
echo "COV_FILE=${COV_FILE}"
echo "REQUIREMENTS_FILE=${REQUIREMENTS_FILE}"
echo "AFILE=${AFILE}"
echo "PYLINT_PLUGINS_DIR=${PYLINT_PLUGINS_DIR}"
###
# Install tools and dependencies of package dependencies
###
if [ "${TRAVIS_OS_NAME}" == "linux" ]; then
    #sudo apt-get update;
    if ! apt list --installed 2> /dev/null | grep -q -E "^aspell" >& /dev/null; then
        sudo apt-get install -qq -y aspell;
    fi
fi

#[VERBATIM]install:
###
# Report version numbers for all compiled packages installed
###
if [ "${TRAVIS_OS_NAME}" == "linux" ]; then
    dpkg --status aspell;
fi
###
# Install package dependencies
###
travis_wait ${PIPCMD} install -r"${REQUIREMENTS_FILE}"
${PIPCMD} install codecov
${PIPCMD} freeze

#[VERBATIM]before_script:
###
# Create directories for reports and artifacts
###
mkdir -p "${RESULTS_DIR}"/testresults
mkdir -p "${RESULTS_DIR}"/codecoverage
mkdir -p "${RESULTS_DIR}"/artifacts

#[VERBATIM]script:
###
# Install package
###
cat "${REPO_DIR}"/MANIFEST.in
${PYTHONCMD} setup.py sdist
# Change directory away from repository, otherwise pip does not install package
cd "${REPO_DIR}" || exit 1
export PKG_VERSION=$(SHELLCHECK_CI_ENV=1 python -c "import os, sys; sys.path.append(os.path.realpath('.'));import setup; print(setup.__version__)")
echo "PKG_VERSION=${PKG_VERSION}"
cd "${PYTHON_SITE_PACKAGES}" || exit 1
${PIPCMD} install "${REPO_DIR}/dist/${PKG_NAME}-${PKG_VERSION}.tar.gz"
###
# Write coverage configuration file
###
"${SBIN_DIR}"/make-coveragerc.sh 'ci' "${INTERP}" "${SOURCE_DIR}" "${EXTRA_DIR}"
cat "${COV_FILE}"
###
# Change to tests sub-directory to mimic Tox conditions
###
cd "${EXTRA_DIR}"/tests || exit 1
###
# Run tests
###
"${SBIN_DIR}"/cprint.sh line cyan "Testing project code compliance"
"${SBIN_DIR}"/check_files_compliance.py -tps -d "${SOURCE_DIR}" -m "${EXTRA_DIR}"
"${SBIN_DIR}"/cprint.sh line cyan "Testing Pylint compliance"
pylint_dirs=(${SOURCE_DIR} ${SBIN_DIR} ${EXTRA_DIR}/tests)
for pylint_dir in "${pylint_dirs[@]}"; do
    fnames=();
    while IFS=  read -r -d $'\0'; do
        fnames+=("$REPLY");
    done < <(find "${pylint_dir}" -name "*.py" -not -path "${pylint_dir}/websupport/*" -print0)
    for fname in "${fnames[@]}"; do
        echo "File: ${fname}";
        pylint --rcfile="${EXTRA_DIR}"/.pylintrc -f text -r no "${fname}";
    done
done
if ${PYTESTCMD} --collect-only --doctest-glob="*.rst" "${EXTRA_DIR}"/docs &> /dev/null; then
    "${SBIN_DIR}"/cprint.sh line cyan "Testing reStructuredText files";
    ${PYTESTCMD} --doctest-glob="*.rst" "${EXTRA_DIR}"/docs;
fi
if ${PYTESTCMD} --collect-only --doctest-modules "${SOURCE_DIR}" &> /dev/null; then
    "${SBIN_DIR}"/cprint.sh line cyan "Testing docstrings";
    ${PYTESTCMD} --doctest-modules "${SOURCE_DIR}";
fi
# Coverage tests runs all the unit tests, no need to run the non-coverage
# tests since the report is not being used
# - ${SBIN_DIR}/cprint.sh line cyan "Testing code"
# - ${PYTESTCMD} -s -vv --junitxml=${RESULTS_DIR}/testresults/pytest.xml
"${SBIN_DIR}"/cprint.sh line cyan "Testing coverage"
${PYTESTCMD} --cov-config "${COV_FILE}" --cov "${SOURCE_DIR}" --cov-report xml
if [ -f "${SBIN_DIR}"/build_docs.py ]; then
    "${SBIN_DIR}"/cprint.sh line cyan "Testing documentation";
    "${SBIN_DIR}"/build_docs.py -r -t -d "${SOURCE_DIR}";
fi

#[VERBATIM]notifications:
#[VERBATIM]  email:
#[VERBATIM]    on_success: change
#[VERBATIM]    on_failure: always

#[VERBATIM]after_success:
if [ "${CODECOV_TOKEN}" != "" ]; then
    cd "${REPO_DIR}" || exit 1;
    cp "${RESULTS_DIR}"/codecoverage/coverage.xml "${REPO_DIR}"/.;
    export DOT_SOURCE_DIR=${SOURCE_DIR//\//.};
    export DOT_REPO_DIR=${REPO_DIR//\//.};
    sed -r -i -e "s|${SOURCE_DIR}|${REPO_DIR}/${PKG_NAME}|g" coverage.xml;
    sed -r -i -e "s|${DOT_SOURCE_DIR}|${DOT_REPO_DIR}.${PKG_NAME}|g" coverage.xml;
    codecov --token="${CODECOV_TOKEN}" --file="${REPO_DIR}"/coverage.xml;
fi

#[VERBATIM]after_failure:
"${SBIN_DIR}"/zip-artifacts.sh "${INTERP}"
if [ -f "${AFILE}" ]; then
    "${REPO_DIR}"/bin/dropbox_uploader.sh upload "${AFILE}" .;
else
    echo "Artifacts could not be exported";
fi