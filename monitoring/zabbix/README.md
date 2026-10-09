# Zabbix Observability Expansion

This directory extends the existing monitoring lab into a reusable observability exercise. The goal is to demonstrate monitoring design rather than to mirror a specific job description.

## What this extension adds

- reusable Zabbix 7.0 custom templates
- low-level filesystem discovery (LLD)
- item and trigger prototypes
- sustained-threshold alerting to reduce transient noise
- a separate Linux SNMP target
- SNMPv2 telemetry collection
- Zabbix network discovery / automatic host onboarding
- Grafana Zabbix data-source support
- an alert-to-investigation-to-recovery validation workflow

## Lab topology

```text
                         devops-monitor-01
                   Zabbix Server + Grafana
                     192.168.122.215
                       /           \
                      /             \
           Zabbix agent              SNMPv2
                    /                 \
                   v                   v
          devops-app-01          devops-snmp-01
          192.168.122.221        192.168.122.222
          filesystems / app      snmpd on UDP 161
```

The SNMP community is intentionally not committed. Set it locally with `SNMP_COMMUNITY`.

## 1. Prepare the third VM

Create an Ubuntu VM named `devops-snmp-01` using:

- `cloud-init/snmp-user-data.yml`
- `cloud-init/snmp-meta-data.yml`

The example inventory expects `192.168.122.222`. If DHCP assigns a different address, update your local `ansible/inventory.ini`.

## 2. Apply the Ansible configuration

```bash
export ZABBIX_DB_PASSWORD='replace-with-your-local-value'
export SNMP_COMMUNITY='replace-with-a-lab-only-community'

cd ansible
ansible-playbook -i inventory.ini site.yml --syntax-check
ansible-playbook -i inventory.ini site.yml
```

Validate SNMP from the monitoring server:

```bash
snmpget -v2c -c "$SNMP_COMMUNITY" 192.168.122.222 1.3.6.1.2.1.1.5.0
snmpget -v2c -c "$SNMP_COMMUNITY" 192.168.122.222 1.3.6.1.2.1.1.3.0
snmpwalk -v2c -c "$SNMP_COMMUNITY" 192.168.122.222 1.3.6.1.2.1.2
```

Expected result: `sysName`, `sysUpTime`, and interface data are returned. Do not continue to Zabbix until these commands work.

## 3. Import the custom templates

In Zabbix 7.0:

1. Open **Data collection → Templates**.
2. Choose **Import**.
3. Import `templates/template-linux-filesystem-capacity.yaml`.
4. Import `templates/template-snmp-linux-lab.yaml`.
5. Link **Linux Filesystem Capacity - Lab** to `devops-app-01`.

The filesystem template uses the built-in `vfs.fs.discovery` key. Each discovered filesystem creates an item from the item prototype:

```text
vfs.fs.size[{#FSNAME},pused]
```

The trigger prototype waits for usage to remain above the configured threshold for ten minutes:

```text
{$FS.PUSED.WARN} = 85
window = 10m
```

This is intentional: a short-lived spike should not immediately page an operator.

## 4. Create the SNMP host manually first

Before enabling automatic discovery, prove that SNMP monitoring works end-to-end.

Create a host:

```text
Host name: devops-snmp-01
Host group: Linux servers (or a lab group)
Interface: SNMP
IP: 192.168.122.222
Port: 161
Version: SNMPv2
Community: use your local SNMP_COMMUNITY value
Template: SNMP Linux Node - Lab
```

Confirm that these items receive data:

- SNMP: System name
- SNMP: System uptime
- SNMP: Interface count

Then stop `snmpd` on the target for longer than five minutes and verify the **SNMP telemetry unavailable for 5 minutes** problem. Restore `snmpd` and verify automatic recovery.

## 5. Add network discovery

After manual SNMP monitoring is proven, configure automatic device detection.

Create a Zabbix network discovery rule:

```text
Name: Lab SNMP subnet discovery
Discovery by: Server
IP range: 192.168.122.220-230
Update interval: 10m
Check: SNMPv2 agent
SNMP OID: 1.3.6.1.2.1.1.5.0
Port: 161
Device uniqueness: IP address
```

Use the local SNMP community in the SNMP discovery check.

Create a discovery action with conditions that limit it to the lab rule and **Discovery status = Up**. Operations:

1. Add host
2. Add to a lab/Linux host group
3. Link `SNMP Linux Node - Lab`

For the demonstration, remove the manually created SNMP host before testing automatic creation so there is no duplicate.

## 6. Grafana

The monitoring-stack Compose file preinstalls the Grafana Zabbix plugin.

In Grafana:

1. Enable the Zabbix plugin.
2. Add a Zabbix data source.
3. URL: `http://zabbix-web:8080/api_jsonrpc.php`
4. Authenticate with a dedicated local Zabbix API user.
5. Build one operations dashboard with:
   - application-host filesystem utilization
   - SNMP target uptime
   - SNMP target interface count
   - current problems / alert state

Do not commit real Zabbix credentials.

## 7. Evidence to capture after validation

Capture evidence only after the lab is running:

1. Zabbix template showing the filesystem LLD rule.
2. Discovered filesystem items.
3. Warning trigger firing after sustained capacity pressure.
4. SNMP Latest data with uptime and interface count.
5. Network discovery finding `devops-snmp-01`.
6. Grafana dashboard with both agent and SNMP telemetry.
7. Recovery event after the underlying problem is fixed.

The repository should contain real screenshots from your own lab run, not generated mockups.

## Alert-quality rationale

The lab deliberately separates **detection** from **paging**:

- data collection can be frequent;
- alerts should require a meaningful duration or loss of telemetry;
- recovery must be verified from monitoring, not assumed after a restart;
- each alert should identify an actionable failure domain.

That design is more useful than creating a large number of instant threshold alerts.
