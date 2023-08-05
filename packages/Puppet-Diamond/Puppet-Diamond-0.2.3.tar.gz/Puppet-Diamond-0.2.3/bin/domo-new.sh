#!/bin/bash
# Puppet-Diamond
# http://diamond-methods.org/puppet-diamond.html

source $HOME/.puppet-diamond

SKEL_TYPE=$1
SKEL_NAME=$2

echo "Usage: domo-new.sh [type] [name]"
echo
echo "available types:"
echo
echo "- profile"
echo "- puppet-module"
echo "- diamond-module"
echo "- digitalocean-host"
echo "- puppetmaster"
echo "- puppet-diamond"
# echo "- xen-host"
# echo "- kvm-host"
# echo "- kvm-guest"
# echo "- ec2-host"
echo

if [[ "${SKEL_TYPE}" == "puppet-module" ]]; then
    echo "Create a git repo called '${SKEL_NAME}' for this module."
    open "${PD_GIT_WEB_URL}/${PD_GIT_WEB_CREATE_URL}"
    echo "Press ENTER when the repo has been created."
    read

    echo "create module '${SKEL_NAME}' in ${PD_PATH}/${PD_MASTER}/modules/puppet/${SKEL_NAME}"
    mrbob -w "${VIRTUAL_ENV}/share/skels/puppet-module" -O /tmp/${PD_GIT_GROUP}

    pushd /tmp/${PD_GIT_GROUP}
    git init
    git add -A
    git commit -m 'first commit'
    git remote add origin ${PD_GIT_HOST}:${PD_GIT_GROUP}/${SKEL_NAME}.git
    git push -u origin master
    popd

    pushd ${PD_PATH}/${PD_MASTER}
    git submodule add ${PD_GIT_HOST}:${PD_GIT_GROUP}/${SKEL_NAME}.git modules/puppet/${SKEL_NAME}
    popd

    rm -rf /tmp/${PD_GIT_GROUP}
fi

if [[ "${SKEL_TYPE}" == "diamond-module" ]]; then
    echo "Create a git repo called '${SKEL_NAME}' for this module."
    open "${PD_GIT_WEB_URL}/${PD_GIT_WEB_CREATE_URL}"
    echo "Press ENTER when the repo has been created."
    read

    echo "create module '${SKEL_NAME}' in ${PD_PATH}/${PD_MASTER}/modules/diamond/${SKEL_NAME}"
    mrbob -w "${VIRTUAL_ENV}/share/skels/diamond-module" -O /tmp/${PD_GIT_GROUP}

    pushd /tmp/${PD_GIT_GROUP}
    git init
    git add -A
    git commit -m 'first commit'
    git remote add origin ${PD_GIT_HOST}:${PD_GIT_GROUP}/${SKEL_NAME}.git
    git push -u origin master
    popd

    pushd ${PD_PATH}/${PD_MASTER}
    git submodule add ${PD_GIT_HOST}:${PD_GIT_GROUP}/${SKEL_NAME}.git modules/diamond/${SKEL_NAME}
    popd

    rm -rf /tmp/${PD_GIT_GROUP}
fi

if [[ "${SKEL_TYPE}" == "digitalocean-host" ]]; then
    echo "create host '${SKEL_NAME}' in ${PD_PATH}/${PD_MASTER}/hosts/${SKEL_NAME}"
    mrbob -w "${VIRTUAL_ENV}/share/skels/digitalocean-host" -O "${PD_PATH}/${PD_MASTER}/hosts/${SKEL_NAME}"
fi

if [[ "${SKEL_TYPE}" == "profile" ]]; then
    echo "create profile '${SKEL_NAME}.pp' in ${PD_PATH}/${PD_MASTER}/profiles"
    mrbob -w "${VIRTUAL_ENV}/share/skels/profile" -O "${PD_PATH}/${PD_MASTER}/profiles"
fi

if [[ "${SKEL_TYPE}" == "puppetmaster" ]]; then
    echo "create puppet master '${SKEL_NAME}' in ${PD_PATH}/${SKEL_NAME}"
    mrbob -w "${VIRTUAL_ENV}/share/skels/puppetmaster" -O "${PD_PATH}/${SKEL_NAME}"
    find "${PD_PATH}/${SKEL_NAME}" -name .gitignore -exec sh -c "rm {}" \;
fi

if [[ "${SKEL_TYPE}" == "puppet-diamond" ]]; then
    echo "create puppet-diamond configuration in $HOME/.puppet-diamond"
    mrbob "${VIRTUAL_ENV}/share/skels/puppet-diamond" -O $HOME
fi
