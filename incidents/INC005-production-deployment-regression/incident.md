# INC005 - Production Deployment Regression and Rollback

## Summary

A simulated application release introduced a port mismatch between the deployed container and the existing Nginx infrastructure.

The previous known-good release listened on port 8000. The new release started successfully but listened on port 9000 while the deployment configuration continued forwarding traffic to port 8000.

The deployment health check failed, the customer-facing endpoint returned HTTP 502, and Zabbix generated a High-severity alert.

The service was restored by rolling back to the known-good v1 image.

## Environment

- Host: devops-app-01
- Reverse proxy: Nginx
- Runtime: Docker
- Application: FastAPI
- Configuration/deployment: Ansible
- Monitoring: Zabbix

## Impact

The application became unavailable through Nginx and returned HTTP 502 Bad Gateway.

Zabbix detected the application health failure and generated a High-severity problem.
