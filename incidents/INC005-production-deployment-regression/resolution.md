# Resolution and Validation

## Resolution

The broken v2 release was rolled back to the previous known-good image:

devops-demo-api:v1

The rollback was performed using the Ansible deployment playbook.

## Validation

After rollback:

- deployment health validation succeeded
- running release label returned devops-demo-api:v1
- HTTP health endpoint returned 200
- response body returned {"status":"ok"}
- Zabbix automatically marked the incident as resolved

## Monitoring Evidence

- Detection: 09:10:31
- Recovery: 09:12:31
- Duration: 2 minutes
- Severity: High

## Prevention

- Run automated post-deployment health checks
- Keep previous known-good releases available for rollback
- Validate application listening ports before deployment
- Monitor application health rather than container state alone
- Use immutable release tags instead of relying only on latest
- Stop rollout when health validation fails
