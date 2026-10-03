# Root Cause

The FastAPI application container `devops-demo-api` was stopped.

Nginx continued listening on port 80, but its upstream application on port 8000 was unavailable.

The incident demonstrated why TCP port availability alone is insufficient for application monitoring.

The Zabbix web scenario correctly monitored the application health endpoint rather than only checking whether port 80 was open.
