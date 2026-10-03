# Linux DevOps Operations Lab

Hands-on DevOps and Linux operations lab demonstrating configuration management, containerized application deployment, monitoring, incident response, access management, log management, and rollback workflows.

This project was built as a controlled technical lab to practice production-style Linux/DevOps operations.

## Architecture

```text
                    WSL2 Ubuntu
                 Ansible Control Node
                         |
                         | SSH
              +----------+-----------+
              |                      |
              v                      v
      devops-app-01          devops-monitor-01
      Ubuntu 22.04           Ubuntu 22.04
      192.168.122.221        192.168.122.215
              |                      |
              |                      +-- Zabbix Server
              |                      +-- Zabbix Web
              |                      +-- PostgreSQL
              |                      +-- Grafana
              |
              +-- Nginx :80
              +-- Docker
              +-- FastAPI
              +-- Zabbix Agent
              +-- logrotate
