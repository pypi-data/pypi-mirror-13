node domo_core {
    $system_packages = [
        "libaugeas-ruby",
        "libaugeas0",
        "augeas-tools",
        "augeas-lenses",
        'libc6-dev',
        "build-essential",
        "python-software-properties",
        "libssl-dev",
        "bsdmainutils",
        "groff-base",
        "man-db",
        'rsync',
        'unison',
        "wget",
        "git-core",
        "virtualenvwrapper",
        "libsqlite3-dev",
        "sqlite3",
        ]
    ensure_packages($system_packages)

    Class['network::iptables'] ->
        Class['logrotate'] ->
        Class['aide']

    Class['monit'] ->
        Class['psad'] ->
        Class['fail2ban']

    class {
        'aide': ;
        #'monit': ;
        #'logrotate': ;
        'cron': ;
        'sshd': ;
        'tmux': ;
        #'python': ;
        #'mosh': ;
        'psad': ;
        'fail2ban': ;
        'zsh': ;
        'network::iptables': ;
    }

    aide::rule {
        "/etc/mtab VarFile":
            seq => "1",
            prog => "mtab";
        "/etc/resolv.conf VarFile":
            seq => "1",
            prog => "resolv.conf";
        "!/home/idm/Maildir":
            seq => "1",
            prog => "homes";
    }

    file {
        "/etc/init/tty2.conf": ensure => absent;
        "/etc/init/tty3.conf": ensure => absent;
        "/etc/init/tty4.conf": ensure => absent;
        "/etc/init/tty5.conf": ensure => absent;
        "/etc/init/tty6.conf": ensure => absent;
    }

    file {
        "/etc/cron.daily/ntpdate":
            ensure => file,
            owner => root,
            group => root,
            mode => 0755,
            content => "#!/bin/sh\n/usr/sbin/ntpdate ntp.ubuntu.com 2>&1 >/dev/null\n"
    }

    network::iptables::rule {
        'allow establihed input':
            seq => '01',
            cmd => "-A INPUT -m state --state RELATED,ESTABLISHED -j ACCEPT";
        'allow local':
            seq => '05',
            cmd => "-A INPUT -i lo -j ACCEPT";
        #"ignore itunes":
        #    seq => '11',
        #    cmd => "-A INPUT -p udp -m udp --dport 5353 -j DROP";
        "ignore 67:68":
            seq => '11',
            cmd => "-A INPUT -p udp -m udp --dport 67:68 -j DROP";
        "ignore 137:138":
            seq => '11',
            cmd => "-A INPUT -p udp -m udp --dport 137:138 -j DROP";
        "ignore dropbox":
            seq => '11',
            cmd => "-A INPUT -p udp -m udp --dport 17500 -j DROP";
        'log input to iptables':
            seq => '25',
            cmd => "-A INPUT -j LOG --log-prefix 'iptables: ' --log-level info";
        'drop all other input':
            seq => '29',
            cmd => "-A INPUT -j DROP";
        'log forwards to iptables':
            seq => '35',
            cmd => "-A FORWARD -j LOG --log-prefix 'iptables: ' --log-level info";
        'drop all other forwards':
            seq => '49',
            cmd => "-A FORWARD -j DROP";
        'allow establihed output':
            seq => '75',
            cmd => "-A OUTPUT -m state --state NEW,RELATED,ESTABLISHED -j ACCEPT";
        'drop all other output':
            seq => '99',
            cmd => "-A OUTPUT -m state --state INVALID -j DROP ";
    }
}

node domo_users inherits domo_core {
    class {
        'sudo': user => 'domo';
    }

    group { 'admin_group':
        name => "admin",
        ensure => present;
    }

    user {
        'ubuntu':
            ensure => absent;
        'domo':
            ensure => present,
            shell => "/bin/zsh",
            groups => ['admin'],
            home => "/home/domo",
            managehome => true;
    }

    zsh::zshrc {
        "domo zshrc":
            homedir => "/home/domo",
            username => "domo";
    }

    ssh::authorized_key {
        "domo":
            user => "domo",
            home => "/home/domo",
            keyfile => "domo_keys";
    }
}

node domo_lucid inherits domo_users {
    class { 'apt::release':
      release_id => 'lucid',
    }

    class {
        'puppet':
            distribution => "lucid";
            #puppet_version => "2.7.23-1puppetlabs1" ;
        'monit': distribution => "lucid" ;
        'logrotate': distribution => "lucid" ;
    }
}

node domo_precise inherits domo_users {
    $distribution = "precise"

    apt::pin { 'precise': priority => 700 }
    apt::pin { 'precise-updates': priority => 700 }
    apt::pin { 'precise-security': priority => 700 }

    class {
        'puppet':
            distribution => "precise",
            puppet_version => "3.8.4-1puppetlabs1";
        'monit': distribution => "precise" ;
        'logrotate': distribution => "precise" ;
    }
}

node domo_diamond inherits domo_precise {
    class {
        'python': ;
        'nginx-src': ;
        #'msmtp': ;
        #'monit::nginx': ;
    }
}
