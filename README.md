# Linux DevOps Operations & Observability Lab

Production-style Linux operations lab focused on configuration management, application delivery, infrastructure monitoring, incident response, access administration, log management, rollback, and observability.

> All failures and incidents in this repository were deliberately reproduced in an isolated lab. They are not production incidents or customer data.

## 30-second overview

- **3 Ubuntu VMs** on KVM/libvirt: application, monitoring, and isolated SNMP target nodes
- **Ansible** roles for Linux baseline configuration, application deployment, monitoring, developer access, log rotation, and SNMP
- **Docker + Nginx + FastAPI** application path
- **Zabbix + Grafana + PostgreSQL** monitoring stack
- **Custom Zabbix low-level discovery (LLD)** with filesystem item and trigger prototypes
- **SNMPv2 monitoring** with a dedicated Linux target, availability alerting, and network discovery
- **Grafana operations dashboard** backed by the Zabbix API
- **5 documented application/operations incidents** plus observability failure-and-recovery drills
- **Deployment health validation + rollback** using immutable image tags
- **GitHub Actions** validation for Ansible and exported Zabbix templates

## Architecture

```text
                         WSL2 Ubuntu
                      Ansible Control Node
                              |
                              | SSH
              +---------------+----------------+
              |                                |
              v                                v
      devops-app-01                    devops-monitor-01
      Ubuntu 22.04                     Ubuntu 22.04
              |                                |
              |                                +-- PostgreSQL
              |                                +-- Zabbix Server
              |                                +-- Zabbix Web
              |                                +-- Grafana
              |
              +-- Nginx :80
              +-- Docker
              +-- FastAPI
              +-- Zabbix Agent
              +-- logrotate

                              |
                              | SNMPv2 / UDP 161
                              v
                       devops-snmp-01
                       Ubuntu 22.04
                       snmpd target
```

Virtual machines are hosted with **KVM/libvirt**. Ansible manages the desired state over SSH. Zabbix monitors the application node with an agent and the dedicated SNMP node over UDP/161.

## Technology stack

| Area | Technologies |
|---|---|
| Linux / virtualization | Ubuntu, KVM, libvirt, cloud-init |
| Configuration management | Ansible roles, variables, handlers |
| Application | FastAPI, Python |
| Runtime / proxy | Docker, Nginx |
| Monitoring | Zabbix Server, Zabbix Agent, SNMPv2, Grafana |
| Observability | Zabbix LLD, item prototypes, trigger prototypes, discovery actions, Grafana dashboards |
| Data | PostgreSQL |
| Operations | SSH, systemd, logrotate, journalctl, SNMP CLI |
| Delivery validation | Ansible post-deployment health checks, GitHub Actions |

## Observability expansion

The monitoring environment was extended beyond basic host availability to demonstrate reusable monitoring design and alert-quality work.

### Custom filesystem capacity template

The repository includes an exportable Zabbix 7.0 template:

[`monitoring/zabbix/templates/template-linux-filesystem-capacity.yaml`](monitoring/zabbix/templates/template-linux-filesystem-capacity.yaml)

It contains:

- filesystem low-level discovery using `vfs.fs.discovery`
- a `vfs.fs.size[{#FSNAME},pused]` item prototype
- a reusable `{$FS.PUSED.WARN}` threshold macro
- a sustained 10-minute trigger prototype to reduce short-spike noise
- component, mount, and capacity tags

### SNMP monitoring

A third VM, `devops-snmp-01`, is configured through the `snmp_target` Ansible role.

The SNMP template collects:

- system name
- system uptime
- interface count
- no-data detection for lost SNMP telemetry

The community string is supplied through the `SNMP_COMMUNITY` environment variable and is not stored in the repository.

### Network discovery and onboarding

Zabbix network discovery was configured for the lab subnet to locate the SNMP target. A discovery action then associates the discovered device with the `Linux servers` host group and the custom SNMP template.

### Grafana + Zabbix

Grafana reads operational data through the Zabbix API using a dedicated API token rather than a stored administrator password.

The dashboard combines:

- root filesystem utilization
- SNMP system uptime
- SNMP interface count
- recent infrastructure problems

![Linux Infrastructure Operations Grafana dashboard](docs/evidence/observability/07-grafana-infrastructure-dashboard.png)

Full implementation notes and evidence: [Observability expansion](docs/observability-expansion.md).

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

Investigation used `docker ps`, `docker inspect`, `docker logs`, and `curl`.

The release was rolled back with the Ansible deployment playbook to `devops-demo-api:v1`. The health endpoint returned HTTP 200 and Zabbix recorded recovery.

## Ansible roles

### `common`
Provides the Linux baseline across managed hosts: administration packages, operations group membership, lab directories, and environment identification.

### `app_server`
Configures Docker, Nginx, FastAPI deployment, Nginx validation, container lifecycle, and application health checks.

### `developer_access`
Automates account provisioning, SSH authorized keys, access revocation, process termination, and home-directory cleanup.

### `monitoring_stack`
Deploys PostgreSQL, Zabbix Server, Zabbix Web, and Grafana.

The database password is supplied with the `ZABBIX_DB_PASSWORD` environment variable and is not committed.

### `zabbix_agent`
Configures agent-based monitoring on the application host.

### `snmp_target`
Configures the isolated SNMP target with `snmpd`, restricted read-only access, service management, and UDP/161 verification.

### `log_management`
Controls application log growth with size-based rotation, retention, compression, and `copytruncate`.

## Monitoring flows

```text
Application path
Client -> Nginx :80 -> Docker :8000 -> FastAPI /health
                                      |
                                      +-> Zabbix web scenario
                                      +-> problem / recovery events

Host metrics
devops-app-01 -> Zabbix Agent -> Zabbix Server

SNMP telemetry
devops-snmp-01 :161/udp -> Zabbix Server -> Grafana
```

## Evidence

The observability extension includes recruiter-facing evidence for:

- filesystem discovery and prototypes
- filesystem alert and recovery
- live SNMP data
- SNMP outage detection
- SNMP recovery
- network discovery
- final Grafana infrastructure dashboard

See [`docs/evidence/observability/`](docs/evidence/observability/).

## Repository structure

```text
linux-devops-operations-lab/
├── .github/workflows/
│   └── ansible-validation.yml
├── ansible/
│   ├── roles/
│   │   ├── common/
│   │   ├── app_server/
│   │   ├── developer_access/
│   │   ├── monitoring_stack/
│   │   ├── zabbix_agent/
│   │   ├── snmp_target/
│   │   └── log_management/
│   ├── inventory.example.ini
│   ├── site.yml
│   ├── developer-access.yml
│   └── deploy-release.yml
├── app/
├── cloud-init/
├── docs/
│   ├── observability-expansion.md
│   └── evidence/observability/
├── incidents/
│   ├── INC001-application-outage/
│   ├── INC002-ansible-nginx-deployment-failure/
│   ├── INC003-developer-ssh-access-failure/
│   ├── INC004-log-growth-disk-pressure/
│   └── INC005-production-deployment-regression/
├── monitoring/zabbix/templates/
│   ├── template-linux-filesystem-capacity.yaml
│   └── template-snmp-linux-lab.yaml
├── .env.example
├── .gitignore
└── README.md
```

## Setup

### Prerequisites

- Linux/WSL2 control node
- Ansible
- KVM/libvirt
- three reachable Ubuntu VMs
- SSH key-based access
- Docker-capable monitoring/application guests

Copy the example inventory:

```bash
cp ansible/inventory.example.ini ansible/inventory.ini
```

Update the VM IP addresses and SSH key path for your environment.

Set secrets locally:

```bash
export ZABBIX_DB_PASSWORD='replace-with-your-local-password'
export SNMP_COMMUNITY='replace-with-a-non-default-lab-value'
```

Do not commit the real values.

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
curl http://<APP_VM_IP>/health
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

## CI validation

GitHub Actions validates:

- the main Ansible playbook
- the release deployment playbook
- the exported Zabbix 7.0 template YAML files

The CI workflow does not attempt to reproduce KVM/libvirt or destructive incident scenarios.

## Security

The public repository intentionally excludes private SSH keys, local inventory, `.env` files, API tokens, SNMP community secrets, and database passwords. Example files contain placeholders only.

## What this project demonstrates

- Linux administration and troubleshooting
- KVM/libvirt virtualization
- Ansible configuration management
- Docker and Nginx operations
- Zabbix agent monitoring
- custom Zabbix templates
- low-level discovery and prototypes
- alert-threshold tuning
- SNMP monitoring and service-loss detection
- Zabbix network discovery and discovery actions
- Grafana dashboarding through the Zabbix API
- incident investigation and recovery validation
- Linux user and SSH access management
- log and disk troubleshooting
- deployment health checks and rollback

## Portfolio scope

This repository is a **controlled technical lab** built to demonstrate hands-on Linux, monitoring, and DevOps operations. It does not claim production ownership, customer incidents, or high-availability production experience.
