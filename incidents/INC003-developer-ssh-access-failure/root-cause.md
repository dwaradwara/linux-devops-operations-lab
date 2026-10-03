# Root Cause

The developer's `authorized_keys` file was unavailable.

Without the authorized public key on the server, SSH could not authenticate the `appdev` account and returned:

Permission denied (publickey).
