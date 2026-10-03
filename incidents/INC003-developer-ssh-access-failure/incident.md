# INC003 - Developer SSH Access Failure

## Summary

A developer account on `devops-app-01` lost SSH access after its `authorized_keys` file became unavailable.

The issue was reproduced as a public-key authentication failure, investigated through account and SSH configuration checks, and repaired by reapplying the Ansible developer-access role.

## Environment

- Host: devops-app-01
- Developer account: appdev
- Authentication: SSH public key
- Configuration management: Ansible

## Impact

The developer could not access the application server through SSH.

## Symptom

SSH returned:

Permission denied (publickey).
