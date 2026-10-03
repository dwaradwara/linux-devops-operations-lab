# Resolution and Prevention

## Resolution

An Ansible-managed logrotate policy was deployed for:

/var/log/devops-demo/*.log

The policy included:

- 50 MB rotation threshold
- five retained rotations
- compression
- delayed compression
- missing-file handling
- empty-log handling
- copytruncate

The configuration was validated and forced rotation was tested.

## Validation

Rotation produced separate generations of the application log and compressed older log generations.

Synthetic incident data was then removed.

Final filesystem usage was approximately:

- Filesystem size: 15 GB
- Used: 2.8 GB
- Available: 12 GB
- Usage: 20%

## Prevention

- Manage application logs with logrotate
- Monitor filesystem consumption
- Investigate unexpected `/var/log` growth
- Use retention and compression policies
- Alert before disk usage reaches critical thresholds
