# Root Cause

The variable `nginx_listen_port` was set to the invalid value `invalid_port`.

Ansible rendered this value into the Nginx configuration.

The configuration file was syntactically invalid for the Nginx listen directive.

The validation handler correctly detected the problem before service reload.
