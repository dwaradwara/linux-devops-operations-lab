# Linux DevOps Operations & Incident Response Lab

Production-style Linux/DevOps lab built to demonstrate hands-on configuration management, containerized application deployment, monitoring, incident response, access administration, log management, and rollback workflows.

> All failures and incidents in this repository were deliberately reproduced in an isolated lab. They are not production incidents or customer data.

## 30-second overview

- **2 Ubuntu VMs** on KVM/libvirt: application and monitoring nodes
- **Ansible** roles for baseline configuration, application deployment, developer access, Zabbix agent configuration, monitoring stack, and log rotation
- **Docker + Nginx + FastAPI** application path
- **Zabbix + Grafana + PostgreSQL** monitoring stack
- **5 documented incidents** with investigation, root cause, resolution, and evidence
- **Deployment health validation + rollback** using immutable image tags
- **GitHub Actions** syntax validation for the Ansible playbooks

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
```

Virtual machines are hosted with **KVM/libvirt**. The control node connects over SSH and applies the desired state with Ansible.

## Technology stack

| Area | Technologies |
|---|---|
| Linux / virtualization | Ubuntu, KVM, libvirt, cloud-init |
| Configuration management | Ansible roles, variables, handlers |
| Application | FastAPI, Python |
| Runtime / proxy | Docker, Nginx |
| Monitoring | Zabbix Server, Zabbix Agent, Grafana |
| Data | PostgreSQL |
| Operations | SSH, systemd, logrotate, journalctl |
| Delivery validation | Ansible post-deployment health checks, GitHub Actions |

## Incident portfolio

| Incident | Scenario | Detection / evidence | Recovery |
|---|---|---|---|
| [INC001](incidents/INC001-application-outage/) | Application container outage | Zabbix HIGH alert and failed health check | Restarted container; HTTP 200 and Zabbix recovery |
| [INC002](incidents/INC002-ansible-nginx-deployment-failure/) | Invalid Nginx deployment | Ansible handler failed on `nginx -t` | Restored valid configuration without reloading the bad one |
| [INC003](incidents/INC003-developer-ssh-access-failure/) | Developer SSH access failure | `Permission denied (publickey)` and missing `authorized_keys` | Reapplied Ansible access role and validated SSH login |
| [INC004](incidents/INC004-log-growth-disk-pressure/) | Excessive log growth / disk pressure | `df`, `du`, and file-size investigation | Added Ansible-managed logrotate policy and validated rotation |
| [INC005](incidents/INC005-production-deployment-regression/) | Broken application release | Failed deployment health check, HTTP 502, Zabbix HIGH alert | Rolled back to known-good `v1`; HTTP 200 and automatic alert recovery |

## Strongest scenario: deployment regression and rollback

INC005 models a production-style release regression.

A known-good image was preserved as:

```text
devops-demo-api:v1
```

A deliberately broken release was then deployed:

```text
devops-demo-api:v2-broken
```

The container started, but the application listened on **port 9000** while the Docker/Nginx path expected **port 8000**.

Observed behavior:

```text
container running
      |
      +--> Uvicorn listening on :9000
      |
Nginx / deployment path expects :8000
      |
      +--> HTTP 502
      |
      +--> Zabbix HIGH alert
```

Investigation used:

```bash
docker ps
docker inspect
docker logs
curl
```

The release was rolled back with the Ansible deployment playbook to `devops-demo-api:v1`. The health endpoint returned **HTTP 200** and Zabbix automatically recorded recovery within **2 minutes**.

## Ansible roles

### `common`
Provides the Linux baseline across managed hosts:

- common administration packages
- operations group and user membership
- lab directories
- environment identification

### `app_server`
Configures the application node:

- Docker and Nginx installation
- FastAPI source deployment and image build
- application container lifecycle
- Nginx reverse proxy configuration
- `nginx -t` validation before reload
- application health validation

### `developer_access`
Automates developer access:

- Linux account provisioning
- SSH directory and authorized key management
- access revocation
- termination of active user sessions/processes
- home-directory cleanup

### `monitoring_stack`
Deploys:

- PostgreSQL
- Zabbix Server
- Zabbix Web
- Grafana

The database password is supplied with the `ZABBIX_DB_PASSWORD` environment variable and is not committed to the repository.

### `zabbix_agent`
Configures application-host monitoring:

- Zabbix agent installation
- server and active-server settings
- runtime/log directories
- service management and restart handler

### `log_management`
Controls application log growth:

- 50 MB rotation threshold
- five retained rotations
- compression
- delayed compression
- `copytruncate`

## Application and monitoring flow

```text
Client
  |
  v
Nginx :80
  |
  v
Docker container :8000
  |
  v
FastAPI /health
  |
  v
Zabbix web scenario
  |
  +--> problem event
  +--> recovery event
```

Linux host metrics are collected separately through the Zabbix agent.

## Repository structure

```text
linux-devops-operations-lab/
├── .github/
│   └── workflows/
│       └── ansible-validation.yml
├── ansible/
│   ├── roles/
│   │   ├── common/
│   │   ├── app_server/
│   │   ├── developer_access/
│   │   ├── monitoring_stack/
│   │   ├── zabbix_agent/
│   │   └── log_management/
│   ├── inventory.example.ini
│   ├── site.yml
│   ├── developer-access.yml
│   └── deploy-release.yml
├── app/
├── cloud-init/
├── incidents/
│   ├── INC001-application-outage/
│   ├── INC002-ansible-nginx-deployment-failure/
│   ├── INC003-developer-ssh-access-failure/
│   ├── INC004-log-growth-disk-pressure/
│   └── INC005-production-deployment-regression/
├── .env.example
├── .gitignore
└── README.md
```

## Setup

### Prerequisites

The lab assumes:

- Linux/WSL2 control node
- Ansible
- KVM/libvirt
- two reachable Ubuntu VMs
- SSH key-based access
- Docker-capable guest systems

Copy the example inventory:

```bash
cp ansible/inventory.example.ini ansible/inventory.ini
```

Update the VM IP addresses and SSH key path for your environment.

Set the monitoring database password locally:

```bash
export ZABBIX_DB_PASSWORD='replace-with-your-local-password'
```

Do not commit the real password.

### Validate and apply configuration

```bash
cd ansible

ansible-playbook -i inventory.ini site.yml --syntax-check
ansible-playbook -i inventory.ini site.yml
```

Verify connectivity:

```bash
ansible all -i inventory.ini -m ping
```

Validate the application:

```bash
curl http://192.168.122.221/health
```

Expected:

```json
{"status":"ok"}
```

## Release deployment and rollback

Deploy a known-good release:

```bash
cd ansible

ansible-playbook -i inventory.ini deploy-release.yml \
  -e release_image=devops-demo-api:v1
```

The playbook performs a post-deployment health check and fails the deployment workflow if the application does not return HTTP 200.

Rollback uses the same playbook with the previous known-good image tag.

## Developer access workflow

Provision developer access:

```bash
ansible-playbook -i inventory.ini developer-access.yml
```

Revoke access:

```bash
ansible-playbook -i inventory.ini developer-access.yml \
  -e developer_access_state=absent
```

The public-key path used by this playbook is local to the operator and is intentionally not committed.

## CI validation

GitHub Actions runs Ansible syntax validation on pushes and pull requests.

The CI job does **not** attempt to reproduce the KVM/libvirt environment or execute destructive incident scenarios. Its purpose is to catch playbook/YAML regressions before changes are merged.

## Security

The public repository intentionally excludes:

- private SSH keys
- local Ansible inventory
- `.env` files
- API keys
- production credentials
- hard-coded database passwords

Example files use placeholders only.

## What this project demonstrates

- Linux system administration
- Ansible roles, variables, handlers, and idempotent configuration
- Docker application deployment
- Nginx reverse-proxy administration
- Zabbix monitoring and alerting
- Grafana deployment
- KVM/libvirt virtualization
- Linux user and SSH access management
- application health checks
- log and disk troubleshooting
- incident investigation and root-cause analysis
- release rollback and recovery validation

## Portfolio scope

This repository is a **controlled technical lab** built to demonstrate hands-on Linux and DevOps operations. It does not claim production ownership, customer incidents, or high-availability production experience.
