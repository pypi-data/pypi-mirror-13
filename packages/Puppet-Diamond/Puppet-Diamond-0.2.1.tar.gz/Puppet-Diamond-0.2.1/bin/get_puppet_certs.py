#!/usr/bin/env python
# Puppet-Diamond
# http://diamond-methods.org/puppet-diamond.html

import sys
import os
from fabric.api import run, local, sudo, get, settings
from fabric.tasks import execute


def gen_certs(hostname):
    cfg = {
        'host': os.environ["PD_PUPPETMASTER_SSH_HOST"],
        'user': os.environ["PD_PUPPETMASTER_SSH_USER"]
    }

    # remove any existing keys for this host
    with settings(warn_only=True):
        sudo("puppet cert clean {host}".format(**cfg))

    # generate a new key and put it in a place where this user can get it
    sudo("puppet cert generate {host}".format(**cfg))

    # put the key in a place where this user can get it
    run("rm -rf puppet_tmp && mkdir -p puppet_tmp/{certs,private_keys,public_keys}")
    sudo("cp /var/lib/puppet/ssl/certs/ca.pem ~{user}/puppet_tmp/certs".format(**cfg))
    sudo("cp /var/lib/puppet/ssl/certs/{host}.pem ~{user}/puppet_tmp/certs".format(**cfg))
    sudo("cp /var/lib/puppet/ssl/private_keys/{host}.pem ~{user}/puppet_tmp/private_keys".format(**cfg))
    sudo("cp /var/lib/puppet/ssl/public_keys/{host}.pem ~{user}/puppet_tmp/public_keys".format(**cfg))
    sudo("chown -R {user}:{user} ~{user}/puppet_tmp".format(**cfg))

    # actually get the key
    get("puppet_tmp/", ".")
    local("mv puppet_tmp puppet/ssl")
    run("rm -rf puppet_tmp")

if __name__ == "__main__":
    if len(sys.argv) == 2:
        execute(gen_certs, hostname=sys.argv[1])
    else:
        print "usage: get_puppet_certs.py [hostname]"
