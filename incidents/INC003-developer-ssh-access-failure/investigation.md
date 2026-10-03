# Investigation

## Checks Performed

Account verification:

id appdev

SSH directory inspection:

ls -ld /home/appdev /home/appdev/.ssh
ls -la /home/appdev/.ssh

SSH authentication logs:

journalctl -u ssh -n 40 --no-pager

## Findings

- Developer account existed
- SSH service remained available
- Developer private key was valid
- `/home/appdev/.ssh/authorized_keys` was missing
- Public-key authentication therefore failed

The failure was isolated to the developer account's SSH authorization configuration.
