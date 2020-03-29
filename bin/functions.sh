#!/bin/bash
# functions.sh
# Copyright (c) 2013-2020 Pablo Acosta-Serafini
# See LICENSE for details

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

print_banner () {
	local slength=${#1}
	local line="+-"
	local i=1
	while ((i<=slength)); do
		line=${line}'-'
		let i++
	done
	line=${line}'-+'
	local cyan="\e[1;36m"
	local bold="\033[1m"
	local reset="\033[0m"
	echo -e "${cyan}${bold}${line}${reset}"
	echo -e "${cyan}${bold}| $1 |${reset}"
	echo -e "${cyan}${bold}${line}${reset}"
}

print_cyan_line () {
	local cyan="\e[1;36m"
	local bold="\033[1m"
	local reset="\033[0m"
	echo -e "${cyan}${bold}$1${reset}"
}

print_green_line () {
	local green="\e[1;32m"
	local bold="\033[1m"
	local reset="\033[0m"
	echo -e "${green}${bold}$1${reset}"
}

print_red_line () {
	local red="\e[1;31m"
	local bold="\033[1m"
	local reset="\033[0m"
	echo -e "${red}${bold}$1${reset}"
}

# Mostly From https://stackoverflow.com/questions/12199631/
# convert-seconds-to-hours-minutes-seconds-in-bash
show_time () {
	num=$1
	local sec=0
	local min=0
	local hour=0
	local day=0
	if ((num>59)); then
		((sec=num%60))
		((num=num/60))
		if ((num>59)); then
			((min=num%60))
			((num=num/60))
			if ((num>23)); then
				((hour=num%24))
				((day=num/24))
			else
				((hour=num))
			fi
		else
			((min=num))
		fi
	else
		((sec=num))
	fi
	local ret="Elapsed time: "
	if [ "${day}" != 0 ]; then
		ret="${ret} ${day}d"
		if [ "${hour}" != 0 ] || \
		   [ "${min}" != 0 ] || \
		   [ "${sec}" != 0 ]; then
			ret="${ret}, "
		fi
	fi
	if [ "${hour}" != 0 ]; then
		ret="${ret} ${hour}h"
		if [ "${min}" != 0 ] || [ "${sec}" != 0 ]; then
			ret="${ret}, "
		fi
	fi
	if [ "${min}" != 0 ]; then
		ret="${ret} ${min}m"
		if [ "${sec}" != 0 ]; then
			ret="${ret}, "
		fi
	fi
	if [ "${sec}" != 0 ]; then
		ret="${ret} ${sec}s"
	fi
	echo -e "\n${ret}\n"
}

validate_num_cpus () {
	local script_name=$1
	local num_cpus=$2
	if [ "${num_cpus}" == "" ]; then
		echo ""
		return 0
	fi
	if echo "${num_cpus}" | grep -q "^[1-9][0-9]*$"; then
		num_cpus=$(echo "${num_cpus}" | grep "^[1-9][0-9]*$")
	else
		num_cpus=""
	fi
	if [ "${num_cpus}" == "" ]; then
		echo "${script_name}: number of CPUs has to be"\
		     "an integer greater than 0" >&2
		echo "ERROR"
		return 1
	fi
	if ! pip freeze | grep -q pytest-xdist; then
		echo "${script_name}: pytest-xdist needs to be installed"\
		     "to use multiple CPUS" >&2
		echo "ERROR"
		return 1
	fi
	max_cpus=$(grep -c ^processor /proc/cpuinfo)
	if (( num_cpus > max_cpus )); then
		echo "${script_name}: Requested CPUs (${num_cpus}) greater than"\
		     "available CPUs (${max_cpus})" >&2
		echo "ERROR"
		return 1
	fi
	echo "-n ${num_cpus}"
}

strcat() {
  local IFS=""
  echo -n "$*"
}

get_pyvers () {
    sdir=$(readlink -f "$(dirname "${BASH_SOURCE[0]}")")
    # shellcheck disable=SC1090,SC1091
    source "${sdir}/functions.sh"
    pkgname="$(basename "$(dirname "${sdir}")" | sed -r -e "s/-/_/g")"
    cmd=$(strcat \
        "from __future__ import print_function;" \
        "from ${pkgname}.pkgdata import SUPPORTED_INTERPS;" \
        "print(' '.join(reversed(SUPPORTED_INTERPS)))" \
    )
    pyvers=$(python -c "${cmd}")
    echo "${pyvers}"
}
