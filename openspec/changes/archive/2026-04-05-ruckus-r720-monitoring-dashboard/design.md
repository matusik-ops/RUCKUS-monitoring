## Context

We have Ruckus R720 access points running Unleashed firmware 200.15.6.212 with no centralized monitoring. When issues arise (AP down, poor signal, high client load), they are discovered reactively. We need a monitoring stack that collects metrics via SNMP and the Unleashed web API, stores them historically, and presents them in a drill-down dashboard.

The project is greenfield — there is no existing monitoring infrastructure to integrate with. The Unleashed network has 7 APs with ~13 clients across 2 SSIDs.

## Goals / Non-Goals

**Goals:**
- Deploy a containerized monitoring stack using Docker Compose
- Collect system-level metrics via SNMP (AP status, CPU/memory, aggregate client counts, WLAN traffic counters, Tx error rates)
- Collect per-client metrics via Unleashed _cmdstat.jsp web API (RSSI, noise floor, SNR, channel, hostname, radio band)
- Provide Grafana dashboards with drill-down navigation (fleet → AP → wireless health → client health)
- Retain historical data for incident review
- Design for extensibility — adding new data sources (logs, APIs) should not require rearchitecting

**Non-Goals:**
- Per-radio SNMP metrics (channel utilization, airtime, per-radio client counts) — NOT available on firmware 200.15
- Log aggregation (future phase — Loki can be added to the same Grafana instance)
- Ruckus controller/SmartZone integration (SNMP direct to APs for now)
- High availability or clustering of the monitoring stack
- Automated remediation or self-healing

## Decisions

### 1. Grafana + Prometheus + SNMP Exporter stack

**Choice**: Use Prometheus as the metrics store, SNMP Exporter for collection, and Grafana for visualization.

**Alternatives considered**:
- **Zabbix**: Full-featured but heavyweight, less flexible dashboarding, steeper learning curve
- **LibreNMS**: Good for network monitoring but less extensible for non-SNMP sources
- **Telegraf + InfluxDB + Grafana (TIG)**: Viable, but Prometheus has stronger ecosystem for alerting and service discovery

**Rationale**: The Prometheus + Grafana ecosystem is the most widely adopted open-source monitoring stack. It has excellent community support, native alerting, and Grafana supports many data source plugins — making it straightforward to add logs (Loki), traces, or other sources later without changing the visualization layer.

### 2. Docker Compose for deployment

**Choice**: Package all services in a single Docker Compose file.

**Rationale**: Simple to deploy, version-control, and reproduce. Appropriate for a single-site monitoring deployment. Kubernetes would be overkill here.

### 3. SNMP v2c for system metrics, Unleashed _cmdstat.jsp XML API for client metrics

**Choice**: Use SNMP v2c for system-level metrics (CPU, memory, client counts, WLAN traffic counters, per-AP status) and the Unleashed _cmdstat.jsp XML/AJAX web interface for per-client metrics (RSSI, noise floor, Tx data rate, Rx/Tx bytes, association time, channel, hostname). The XML query uses `INTERVAL-STATS='yes'` to get additional per-client fields (tx-rate, total-rx-bytes, total-tx-bytes) that are not available in the base client list. A custom Python exporter authenticates via login.jsp + CSRF token, posts XML requests to _cmdstat.jsp, parses XML responses including interval-stats child elements, and exposes Prometheus metrics.

**Alternatives considered**:
- **SNMP only**: Simpler, but per-client metrics and per-radio metrics are not available via SNMP on firmware 200.15
- **Web API only**: Could replace SNMP entirely, but SNMP is more reliable for counter-based system metrics and doesn't require session management
- **aioruckus library**: Python library that wraps the Unleashed web API. Could be used as dependency, but adds an external dependency for what is a simple XML POST.

**Rationale**: The two protocols complement each other. SNMP provides reliable counter-based system/interface metrics at low overhead. The _cmdstat.jsp API provides per-client detail (RSSI, noise floor, radio band, hostname) that SNMP cannot expose. The custom exporter is ~250 lines Python and follows the standard Prometheus exporter pattern.

### 4. Provisioned dashboards via JSON files

**Choice**: Store Grafana dashboards as provisioned JSON files in the repo rather than configuring them manually in the UI.

**Rationale**: Version-controlled, reproducible, and can be updated via code changes. Dashboards survive container restarts without needing a persistent Grafana database.

### 5. Prometheus local storage for retention

**Choice**: Use Prometheus's built-in TSDB with configurable retention period.

**Alternatives considered**:
- **Thanos/Cortex**: Long-term storage solutions, but overkill for this scale
- **InfluxDB**: Would add another component to maintain

**Rationale**: Prometheus TSDB is sufficient for weeks/months of retention at our scale. If long-term archival is needed later, Thanos can be layered on without changing the collection pipeline.

### 6. Two-phase testing strategy

**Choice**: Mock-based tests for CI/offline development, plus end-to-end tests against the live AP at 10.91.1.109.

**Alternatives considered**:
- **Only mock tests**: Safer for CI but misses real-world SNMP/API response quirks (e.g., discovering that OID trees differ from documentation)
- **Only e2e tests**: Catches real issues but requires AP availability, slow, not suitable for CI

**Rationale**: Mock tests validate logic (exporter parsing, alert rule correctness, metric naming) and run fast in CI without network dependencies. E2e tests validate the full pipeline against real hardware — critical given that SNMP OIDs and API formats differ significantly from documentation. Both are needed; they serve different purposes.

## Risks / Trade-offs

- **SNMP OID discrepancies** → Firmware 200.15 uses OID base 1.3.6.1.4.1.25053.1.15 (ruckusUnleashed), not the 1.3.6.1.4.1.25053.1.1.13 documented in many community sources. Mitigation: Verified via live SNMP walk; OIDs in snmp.yml match reality. Always test against live hardware.
- **No per-radio SNMP metrics** → RUCKUS-RADIO-MIB OIDs do not exist on firmware 200.15. No channel utilization, airtime, or per-radio client counts via SNMP. Mitigation: Per-client RSSI distribution from web API serves as a proxy for radio health.
- **Undocumented web API** → The _cmdstat.jsp XML interface is not officially documented by Ruckus. It may change between firmware versions. Mitigation: Recorded actual XML responses as test fixtures; e2e tests catch format changes.
- **Web API session management** → The Unleashed web API uses -ejs-session- cookies + CSRF tokens. Sessions expire. Mitigation: The exporter re-authenticates on session expiry (redirect to login.jsp); credentials stored in .env (not committed).
- **Web API rate limiting** → Polling the API too frequently could impact AP performance. Mitigation: Default poll interval of 60s; configurable.
- **SNMP v2c security** → Community strings are sent in plaintext. Mitigation: Restrict SNMP access via firewall rules to monitoring host only; upgrade to v3 if needed.
- **Single point of failure** → All monitoring runs on one host. Mitigation: Acceptable for initial deployment; document backup/restore procedure for Prometheus data and Grafana config.
