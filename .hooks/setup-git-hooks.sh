#!/bin/bash
# Find directory where script is (from http://stackoverflow.com/questions/59895/can-a-bash-script-tell-what-directory-its-stored-in)
source="${BASH_SOURCE[0]}"
while [ -h "$source" ]; do # resolve $source until the file is no longer a symlink
	dir="$( cd -P "$( dirname "$source" )" && pwd )"
	source="$(readlink "$source")"
	[[ $source != /* ]] && source="$dir/$source" # if $source was a relative symlink, we need to resolve it relative to the path where the symlink file was located
done
dir="$( cd -P "$( dirname "$source" )" && pwd )"
repo_dir=$(dirname ${dir})

cpwd=${PWD}
git_hooks_dir=${repo_dir}/.git/hooks
hooks=(pre-commit)
cd ${git_hooks_dir}
for hook in ${hooks[@]}; do
	ln -s -f ${dir}/${hook} ${hook}
done
cd ${cpwd}
