# INC004 - Excessive Log Growth and Disk Pressure

## Summary

Abnormal application log growth increased disk consumption on `devops-app-01`.

Investigation identified `/var/log/devops-demo` as the primary custom log consumer, with approximately 513 MB of log data.

A logrotate policy was deployed through Ansible to control log retention and growth.

## Environment

- Host: devops-app-01
- OS: Ubuntu Linux
- Configuration management: Ansible
- Log directory: /var/log/devops-demo
- Filesystem size: 15 GB

## Impact

Uncontrolled log growth can eventually exhaust filesystem capacity and affect application or operating-system services.

The incident was reproduced in a controlled lab environment without filling the filesystem.
