#!/bin/bash
# Puppet-Diamond
# http://diamond-methods.org/puppet-diamond.html

source $HOME/.puppet-diamond

SSH_HOST=$1

ssh ${PD_PUPPETMASTER_SSH_USER}@${SSH_HOST} "sudo puppet agent --test --noop"
