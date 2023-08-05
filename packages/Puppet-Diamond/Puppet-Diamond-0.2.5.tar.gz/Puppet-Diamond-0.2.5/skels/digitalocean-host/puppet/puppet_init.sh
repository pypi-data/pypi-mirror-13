#!/bin/bash

PUPPET_VERSION=3.8.4-1puppetlabs1

if [[ ! -f /usr/bin/puppet ]]; then
    cp /vagrant/puppet/puppet.list /etc/apt/sources.list.d/puppet.list
    apt-key adv --keyserver keyserver.ubuntu.com --recv 4BD6EC30
    apt-get update
    apt-get upgrade -y
    apt-get install -y puppet-common=$PUPPET_VERSION puppet=$PUPPET_VERSION
fi

if [[ -d /vagrant/puppet/ssl ]]; then
    mkdir -p /var/lib/puppet/ssl
    rsync -a /vagrant/puppet/ssl/ /var/lib/puppet/ssl/
    cp /vagrant/puppet/puppet.conf /etc/puppet/puppet.conf

    rsync -a /vagrant/puppet/sshd/ /etc/ssh/
    chown root:root /etc/ssh/*
    chmod 600 /etc/ssh/ssh_host_dsa_key
    chmod 600 /etc/ssh/ssh_host_rsa_key
fi
