# Zabbix Monitoring Assets

This directory contains reusable Zabbix 7.0 template exports used by the lab.

## Templates

- `template-linux-filesystem-capacity.yaml` — filesystem LLD, item prototype, threshold macro, and sustained-capacity trigger prototype.
- `template-snmp-linux-lab.yaml` — SNMP system name, uptime, interface count, and no-data availability alert.

Import the YAML files through **Data collection → Templates → Import**.

Host-specific details such as interface IPs, SNMP community values, API tokens, and temporary test thresholds are intentionally not committed.

The lab also uses Zabbix network discovery and discovery actions configured through the UI. Their tested behavior and screenshots are documented in [`docs/observability-expansion.md`](../../../docs/observability-expansion.md).
