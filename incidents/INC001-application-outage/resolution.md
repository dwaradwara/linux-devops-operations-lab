# Resolution and Validation

## Resolution

The application container was restarted:

ansible app -i inventory.ini -b -m command -a "docker start devops-demo-api"

## Validation

Application health was verified:

curl -i http://192.168.122.221/health

Result:

HTTP/1.1 200 OK

{"status":"ok"}

Zabbix subsequently cleared the High-severity problem automatically.

## Prevention

- Monitor application-level health endpoints instead of only TCP ports.
- Configure container restart policies.
- Maintain Zabbix alerts for application health failures.
- Validate application recovery after operational changes.
