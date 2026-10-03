# Investigation

## Alert

Zabbix reported:

DevOps demo application unavailable

Severity: High

## Verification

The health endpoint was tested:

curl -i http://192.168.122.221/health

The request failed because Nginx could not reach the application upstream.

## Investigation Commands

docker ps -a

docker logs devops-demo-api

systemctl status nginx

curl -i http://127.0.0.1:8000/health

curl -i http://192.168.122.221/health

## Finding

The `devops-demo-api` Docker container was stopped.

Nginx itself remained operational, isolating the failure to the application layer.
