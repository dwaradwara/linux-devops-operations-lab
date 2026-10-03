# Investigation

## Deployment Failure

The v2 release was deployed using Ansible.

Post-deployment health validation failed after three retries.

## Checks

The following were inspected:

- docker ps
- docker inspect
- docker logs
- curl against the external health endpoint

The container itself was running.

The release label confirmed:

devops-demo-api:v2-broken

Docker logs showed:

Uvicorn running on http://0.0.0.0:9000

However, the deployment and Nginx path expected the application on port 8000.

## Customer Symptom

The public health endpoint returned:

HTTP/1.1 502 Bad Gateway

## Monitoring

Zabbix generated:

- Severity: High
- Problem: DevOps demo application unavailable
