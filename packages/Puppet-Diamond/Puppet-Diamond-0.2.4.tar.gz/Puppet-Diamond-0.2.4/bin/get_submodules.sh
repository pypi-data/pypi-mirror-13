#!/bin/bash
# Puppet-Diamond
# http://diamond-methods.org/puppet-diamond.html
# http://stackoverflow.com/questions/11258737/restore-git-submodules-from-gitmodules

set -e

git config -f .gitmodules --get-regexp '^submodule\..*\.path$' |
    while read path_key path
    do
        url_key=$(echo $path_key | sed 's/\.path/.url/')
        url=$(git config -f .gitmodules --get "$url_key")
        echo $url $path
        git submodule add $url $path
    done
