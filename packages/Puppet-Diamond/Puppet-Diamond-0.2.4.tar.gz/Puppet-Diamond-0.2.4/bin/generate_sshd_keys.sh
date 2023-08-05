#!/bin/bash
# Puppet-Diamond
# http://diamond-methods.org/puppet-diamond.html

mkdir -p puppet/sshd
ssh-keygen -t rsa -f puppet/sshd/ssh_host_rsa_key -N ''
ssh-keygen -t dsa -f puppet/sshd/ssh_host_dsa_key -N ''
ssh-keygen -t ecdsa -f puppet/sshd/ssh_host_ecdsa_key -N ''
