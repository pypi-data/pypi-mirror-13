Exec { path => "/usr/bin:/usr/sbin/:/bin:/sbin" }

include apt

import "functions.pp"
import "domo.pp"
import "nodes/*.pp"
