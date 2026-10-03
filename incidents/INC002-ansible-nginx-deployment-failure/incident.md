# INC002 - Ansible Nginx Deployment Failure

## Summary

An invalid Nginx listen-port value was introduced through Ansible configuration.

The Ansible template deployment succeeded, but the Nginx validation handler detected the invalid configuration and prevented Nginx from reloading.

## Impact

The deployment failed, but the existing running Nginx process continued serving the application.

Application health remained HTTP 200.

## Detection

The Ansible handler executed:

nginx -t

and returned:

host not found in "invalid_port" of the "listen" directive

The playbook stopped with failed=1.
