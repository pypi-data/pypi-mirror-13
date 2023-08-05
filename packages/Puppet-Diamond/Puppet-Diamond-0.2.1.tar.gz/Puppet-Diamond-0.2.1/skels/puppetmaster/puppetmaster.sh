#!/bin/bash

# ssh puppetmaster "sudo su"

# puppet labs modules

puppet module install puppetlabs-java
puppet module install puppetlabs-apt
puppet module install puppetlabs-concat
puppet module install puppetlabs-firewall
puppet module install puppetlabs-inifile
puppet module install puppetlabs-mysql
puppet module install puppetlabs-postgresql
puppet module install puppetlabs-ruby
puppet module install puppetlabs-stdlib

# third-party modules

# puppet module install mkrakowitzer-deploy
# puppet module install puppet-jira
# puppet module install rtyler-jenkins
# puppet module install camptocamp-archive
# puppet module install example42-puppi
# puppet module install example42-postfix
# puppet module install thewired-bitbucket --ignore-dependencies
# puppet module install yguenane-repoforge
