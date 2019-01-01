#!/usr/bin/env bash
# cprint.sh
# Copyright (c) 2018-2019 Pablo Acosta-Serafini
# See LICENSE for details
# shellcheck disable=SC1090,SC2046

source "$(dirname "${BASH_SOURCE[0]}")"/functions.sh

cprint () {
	ctype=$1
	if [ "${ctype,,}" == "banner" ]; then
		print_banner "$2"
	elif [ "${ctype,,}" == "line" ]; then
		color=$2
		case "${color,,}" in
			cyan)
				print_cyan_line "$3"
				;;
			green)
				print_green_line "$3"
				;;
			red)
				print_red_line "$3"
				;;
			*)
				echo "Unsupported color: $2" >&2
				exit 1
				;;
		esac
	else
		echo "Unsupported command: $1" >&2
		exit 1
	fi
}

if [ "${BASH_SOURCE[0]}" == "$0" ]; then
	# Script is not being sourced
	cprint "$@"
fi
