# Resolution and Validation

## Resolution

The Ansible developer-access playbook was reapplied.

Ansible restored:

- the developer account
- the `.ssh` directory
- the managed `authorized_keys` file
- correct file ownership and permissions

## Validation

The restored file was verified with:

ls -l /home/appdev/.ssh/authorized_keys

SSH login was then tested again using the developer key.

Result:

devops-app-01

The developer's access was successfully restored.

## Prevention

- Manage SSH access declaratively through Ansible
- Avoid unmanaged changes to authorized_keys
- Validate file ownership and permissions
- Maintain documented onboarding and offboarding procedures
