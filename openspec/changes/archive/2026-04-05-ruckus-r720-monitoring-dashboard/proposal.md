## Why

We need visibility into the health, performance, and status of our Ruckus R720 access points. Currently there is no centralized way to monitor AP metrics, review historical data for incident analysis, or drill down into specific problem areas. A monitoring dashboard will enable proactive detection of issues and faster incident resolution.

## What Changes

- Deploy a monitoring stack using well-known open-source tools (Grafana + Prometheus + SNMP Exporter) to collect and visualize Ruckus Unleashed metrics
- Create an organized drill-down dashboard: summary overview → per-AP detail → per-metric deep dive
- Store historical metrics data for post-incident review and trend analysis
- Deploy a custom Prometheus exporter that polls the Unleashed _cmdstat.jsp XML web API for per-client metrics (RSSI, noise floor, SNR, channel, hostname)
- Design the architecture to be extensible so future data sources (syslog, etc.) can be integrated without rearchitecting

## Capabilities

### New Capabilities
- `snmp-collection`: SNMP-based metric collection from Ruckus Unleashed APs (firmware 200.15+) using Prometheus SNMP Exporter. Covers system-level stats (CPU, memory, AP count, aggregate client counts, aggregate WLAN traffic/error counters), per-AP status/model/uptime, and Ethernet interface counters. Uses RUCKUS-UNLEASHED-SYSTEM-MIB (OID base 1.3.6.1.4.1.25053.1.15.1), RUCKUS-UNLEASHED-WLAN-MIB (1.3.6.1.4.1.25053.1.15.2), SNMPv2-MIB, and IF-MIB. Note: RUCKUS-RADIO-MIB per-radio stats are NOT available on firmware 200.15.
- `radio-health`: System-level wireless health metrics — aggregate Tx retries/failures/drops, Rx errors, CPU/memory utilization, plus per-client RSSI distribution as a proxy for radio health (since per-radio metrics are not available via SNMP).
- `client-health`: Per-client metrics via Unleashed _cmdstat.jsp XML web API with INTERVAL-STATS — individual RSSI (dBm), noise floor (dBm), SNR, Tx data rate (Kbps), Rx/Tx bytes, association time, channel, radio band, SSID, hostname, AP name. Collected by a custom Python Prometheus exporter using login.jsp + CSRF token authentication.
- `dashboard-views`: Grafana dashboard with drill-down hierarchy — fleet overview, per-AP detail panels, wireless health, client health, and per-metric historical views
- `data-retention`: Prometheus data retention configuration and storage setup for historical metric review
- `alerting`: Grafana alerting rules for critical conditions (AP down, high client count, excessive Tx retries, high CPU, poor client signal)
- `testing`: Two-phase test suite — mock-based tests (SNMP config and web API exporter with simulated responses) for CI/offline validation, and end-to-end tests against the live Ruckus AP (https://10.91.1.109/) to verify real data collection and dashboard rendering

### Modified Capabilities
<!-- No existing capabilities to modify — this is a greenfield project -->

## Impact

- **Infrastructure**: New containerized services (Grafana, Prometheus, SNMP Exporter, custom web API exporter) to deploy and maintain
- **Network**: SNMP v2c polling traffic to Unleashed master AP; HTTPS requests to _cmdstat.jsp web API; firewall rules may need updating
- **Dependencies**: Docker/Docker Compose for container orchestration; Python with prometheus_client for web API exporter
- **Storage**: Persistent volume for Prometheus TSDB and Grafana configuration/dashboards
- **Limitations**: Per-radio metrics (channel utilization, airtime, per-radio client counts) are NOT available via SNMP on firmware 200.15. Temperature is not available anywhere. Noise floor IS available per-client via the web API.
