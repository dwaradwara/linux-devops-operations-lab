# Investigation

## Failure

The application playbook failed during the Nginx validation handler.

## Error

nginx: [emerg] host not found in "invalid_port" of the "listen" directive

## Validation

Manual configuration validation:

nginx -t

also failed.

The application endpoint was tested separately:

curl http://192.168.122.221/health

Result:

HTTP 200

This confirmed that the existing Nginx process had not reloaded the invalid configuration.
