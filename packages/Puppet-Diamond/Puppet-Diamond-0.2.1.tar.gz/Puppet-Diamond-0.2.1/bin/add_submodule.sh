#!/bin/bash
# Puppet-Diamond
# http://diamond-methods.org/puppet-diamond.html

source $HOME/.puppet-diamond

MODULE_NAME=$1

if [[ ! -z ${MODULE_NAME} ]]; then
	echo "run the following command:"
    echo git submodule add ${PD_GIT_HOST}:${PD_GIT_GROUP}/${MODULE_NAME} ${PD_PATH}/${PD_MASTER}/modules/puppet/${MODULE_NAME}
else
    echo "usage: add_submodule.sh [module]"
fi
