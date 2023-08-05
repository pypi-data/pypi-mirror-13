# http://projects.puppetlabs.com/projects/1/wiki/Simple_Text_Patterns
define line($file, $line, $ensure = 'present') {
    case $ensure {
        default: { err ( "unknown ensure value ${ensure}" ) }
        present: {
            exec { "/bin/echo '${line}' >> '${file}'":
                unless => "/bin/grep -qFx '${line}' '${file}'"
            }
        }
        absent: {
            exec { "/bin/grep -vFx '${line}' '${file}' | /usr/bin/tee '${file}' > /dev/null 2>&1":
              onlyif => "/bin/grep -qFx '${line}' '${file}'"
            }

            # Use this resource instead if your platform's grep doesn't support -vFx;
            # note that this command has been known to have problems with lines containing quotes.
            #exec { "/usr/bin/perl -ni -e 'print unless /^\\Q${line}\\E\$/' '${file}'":
            #    onlyif => "/bin/grep -qFx '${line}' '${file}'"
            #}
        }
        uncomment: {
            exec { "/bin/sed -i -e'/${line}/s/#\\+//' '${file}'" :
                onlyif => "/usr/bin/test `/bin/grep '${line}' '${file}' | /bin/grep '^#' | /usr/bin/wc -l` -ne 0"
            }
        }
        comment: {
            exec { "/bin/sed -i -e'/${line}/s/\\(.\\+\\)$/#\\1/' '${file}'" :
                onlyif => "/usr/bin/test `/bin/grep '${line}' '${file}' | /bin/grep -v '^#' | /usr/bin/wc -l` -ne 0"
            }
        }
    }
}

define replace($file, $pattern, $replacement) {
    #$pattern_no_slashes = slash_escape($pattern)
    #$replacement_no_slashes = slash_escape($replacement)

    $pattern_no_slashes = $pattern
    $replacement_no_slashes = $replacement

    exec { "/usr/bin/perl -pi -e 's/$pattern_no_slashes/$replacement_no_slashes/' '$file'":
        onlyif => "/usr/bin/perl -ne 'BEGIN { \$ret = 1; } \$ret = 0 if /$pattern_no_slashes/ && ! /$replacement_no_slashes/ ; END { exit \$ret; }' '$file'",
    }
}

################################################################################
# Definition: wget::fetch
#
# This class will download files from the internet.  You may define a web proxy
# using $http_proxy if necessary.
#
################################################################################
define wget::fetch($source,$destination) {
    if $http_proxy {
        exec { "wget-$name":
            command => "/usr/bin/wget --output-document=$destination $source",
            creates => "$destination",
            unless => "test -f $destination",
            environment => [ "HTTP_PROXY=$http_proxy", "http_proxy=$http_proxy" ],
        }
        } else {
        exec { "wget-$name":
            command => "/usr/bin/wget --output-document=$destination $source",
            creates => "$destination",
        }
    }
}

define rename() {
    #host { "$hostname": ensure => absent }
    #host { "$fqdn": ensure => absent }

    $alias = regsubst($name, '^([^.]*).*$', '\1')

    host { "$name":
        ensure => present,
        ip     => "127.0.1.1",
        alias  => $alias, # ? {
            #"$hostname" => undef,
            #default     => $alias
        #},
        before => Exec['hostname.sh'],
    }

    file { '/etc/mailname':
        ensure  => present,
        owner   => 'root',
        group   => 'root',
        mode    => 644,
        content => "${name}\n",
    }

    file { '/etc/hostname':
        ensure  => present,
        owner   => 'root',
        group   => 'root',
        mode    => 644,
        content => "${name}\n",
        notify  => Exec['hostname.sh'],
    }

    exec { 'hostname.sh':
        command     => '/etc/init.d/hostname start',
        refreshonly => true,
    }
}

define domo::user($keyfile="authorized_keys2") {
    user { $name:
        ensure => present,
        shell => "/bin/zsh",
        managehome => true;
    }

    zsh::zshrc { $name:
        homedir => "/home/$name",
        username => $name;
    }

    ssh::authorized_key { $name:
        user => $name,
        home => "/home/$name",
        keyfile => $keyfile;
    }
}

define domo::swap($size=1024) {
    Exec["swapfile create"] ->
        File["/swapfile"] ->
        Exec["swapfile mkswap"] ->
        Exec["swapfile fstab"] ->
        Exec["swapfile proc-swappiness"] ->
        Exec["swapfile sysctl-swappiness"]

    exec {
        "swapfile create":
            command => "dd if=/dev/zero of=/swapfile bs=1024k count=$size",
            creates => "/swapfile";
        "swapfile mkswap":
            command => "mkswap /swapfile && swapon -a",
            unless => "file /swapfile |grep 'swap file'";
        "swapfile fstab":
            command => 'echo "/swapfile       none    swap    sw      0       0" >> /etc/fstab',
            unless => "grep 'swapfile' /etc/fstab";
        "swapfile proc-swappiness":
            command => 'echo 10 > /proc/sys/vm/swappiness',
            unless => "test `cat /proc/sys/vm/swappiness` -eq 10";
        "swapfile sysctl-swappiness":
            command => 'echo "vm.swappiness = 10" >> /etc/sysctl.conf',
            unless => 'grep "vm.swappiness = 10" /etc/sysctl.conf';
    }

    file {
        "/swapfile":
            mode => "0600",
            ensure => file;
    }
}
