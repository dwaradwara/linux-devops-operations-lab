# INC001 - Application Outage Detected by Zabbix

## Summary

The DevOps demo application became unavailable after its Docker container was stopped.

Zabbix detected the failure through an HTTP web scenario monitoring the `/health` endpoint and generated a High-severity alert.

## Environment

- Application host: devops-app-01
- Application IP: 192.168.122.221
- Reverse proxy: Nginx
- Application runtime: Docker
- Application: FastAPI
- Monitoring: Zabbix
- Health endpoint: /health

## Detection

Zabbix generated:

- Severity: High
- Problem: DevOps demo application unavailable
- Detection time: 08:06:31
- Recovery time: 08:11:31
- Incident duration: 5 minutes

## Customer Impact

Requests to the application health endpoint failed while the application container was stopped.

Nginx remained available, but the upstream FastAPI service was unavailable.
