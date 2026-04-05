## 1. Project Scaffolding

- [x] 1.1 Create project directory structure (docker-compose.yml, config dirs for prometheus, grafana, snmp-exporter, unleashed-exporter, tests/mock, tests/e2e)
- [x] 1.2 Create .env file with configurable parameters (SNMP community string, scrape interval, retention period, alert thresholds, Unleashed API URL/username/password, REST API poll interval)
- [x] 1.3 Create .env.test with test-specific config (live AP address 10.91.1.109, test credentials)
- [x] 1.4 Acquire Ruckus MIB files (RUCKUS-RADIO-MIB, RUCKUS-UNLEASHED-SYSTEM-MIB, RUCKUS-HWINFO-MIB) and document sourcing steps

## 2. SNMP Exporter Configuration

- [x] 2.1 Create SNMP Exporter snmp.yml module targeting Ruckus standalone MIBs: RUCKUS-RADIO-MIB (per-radio stats: client counts, Rx/Tx bytes/frames, resource utilization, busy airtime, auth/assoc counters), RUCKUS-UNLEASHED-SYSTEM-MIB (CPU, memory, total clients, aggregate Tx retries/failures/drops/errors), RUCKUS-HWINFO-MIB (model, serial), plus standard SNMPv2-MIB and IF-MIB
- [x] 2.2 Add SNMP Exporter service to Docker Compose with snmp.yml mounted

## 3. Unleashed REST API Exporter

- [x] 3.1 Create Python Prometheus exporter that authenticates to Unleashed REST API (POST /api/login) and polls per-client station data (GET /api/sta)
- [x] 3.2 Expose per-client metrics as Prometheus gauges: RSSI (dBm), SNR (dB), data rate (Mbps), association duration, Rx/Tx bytes, labeled by client MAC, AP name, SSID, radio band
- [x] 3.3 Expose derived metric: client count per SSID
- [x] 3.4 Handle session re-authentication on 401, API errors, and stale client removal (remove metrics for disconnected clients)
- [x] 3.5 Create Dockerfile for the exporter and add to Docker Compose with environment variables for credentials and poll interval

## 4. Prometheus Configuration

- [x] 4.1 Create prometheus.yml with SNMP scrape job (file_sd_configs, configurable scrape interval default 60s, relabeling for AP identity labels) and unleashed-exporter scrape job
- [x] 4.2 Create targets.yml file for AP target list (IP addresses, AP name labels)
- [x] 4.3 Create Prometheus alerting rules file with rules for: AP unreachable, high channel utilization, high client count, auth failure spike, excessive Tx retries, high CPU, poor client signal (RSSI < threshold)
- [x] 4.4 Add Prometheus service to Docker Compose with persistent volume, configurable retention (default 30d), and alert rules mounted

## 5. Grafana Configuration

- [x] 5.1 Create Grafana datasource provisioning YAML pointing to Prometheus
- [x] 5.2 Create Grafana dashboard provisioning YAML to auto-load dashboards from a directory
- [x] 5.3 Create Grafana alerting contact point configuration (webhook/email placeholder)
- [x] 5.4 Add Grafana service to Docker Compose with persistent volume, provisioning configs, and dashboard directory mounted

## 6. Grafana Dashboards

- [x] 6.1 Create fleet overview dashboard JSON: AP status table with up/down indicators, total client count per AP, per-radio channel utilization, CPU utilization, aggregate Tx error rate, color-coded health thresholds, drill-down links to per-AP detail
- [x] 6.2 Create per-AP detail dashboard JSON: per-radio client count, per-radio traffic in/out rates, channel utilization per radio, CPU and memory gauges, uptime, Ethernet interface status. Template variable for AP selection. Drill-down links from overview.
- [x] 6.3 Create radio health dashboard JSON: per-radio channel utilization, busy airtime rate, auth failure rate, assoc failure rate, Tx retry/failure/drop rates, Rx error rates. Template variables for AP and radio band (2.4GHz/5GHz/All).
- [x] 6.4 Create client health dashboard JSON: sortable client table (MAC, RSSI, SNR, data rate, SSID, radio band, association duration, Rx/Tx bytes), per-client RSSI and data rate time-series, RSSI threshold coloring. Template variables for AP, SSID, and client MAC.
- [x] 6.5 Create Grafana alert rules (AP unreachable, high channel util, high client count, auth failure spike, Tx retries, high CPU, poor client signal) with configurable thresholds

## 7. Mock Tests

- [x] 7.1 Create mock test fixtures: sample Unleashed REST API responses (/api/login success/failure, /api/sta with multiple clients, empty client list, 401 expired session, 500 error)
- [x] 7.2 Write pytest tests for the Unleashed exporter: successful collection, auth failure handling, API error handling, client disconnection cleanup, session re-auth on 401
- [x] 7.3 Record an SNMP walk from the live R720 (10.91.1.109) and create a mock SNMP agent fixture (snmprec/walk file) for offline testing
- [x] 7.4 Write tests verifying SNMP Exporter produces expected metric names and labels against the recorded walk (missing OIDs handled gracefully)
- [x] 7.5 Write promtool unit tests for alerting rules: AP-down, high channel utilization, poor client signal fire correctly with mock time-series data
- [x] 7.6 Create Makefile target `test-mock` (or pytest marker) to run all mock tests without network access

## 8. End-to-End Tests

- [x] 8.1 Create e2e test harness: start full Docker Compose stack with live AP target (10.91.1.109), wait for readiness, run assertions, tear down
- [x] 8.2 Write e2e test: SNMP exporter collects real metrics (sysUpTime, CPU, radio client count are non-zero in Prometheus within 2 scrape intervals)
- [x] 8.3 Write e2e test: REST API exporter collects real client data (unleashed-exporter /metrics returns per-client metrics or empty set without errors)
- [x] 8.4 Write e2e test: Prometheus targets health (GET /api/v1/targets shows both SNMP and unleashed-exporter targets as "up")
- [x] 8.5 Write e2e test: Grafana dashboards render (GET /api/search returns all provisioned dashboards, datasource query returns non-empty results)
- [x] 8.6 Add skip-if-unreachable logic: e2e tests skip gracefully with a clear message when 10.91.1.109 is not reachable
- [x] 8.7 Create Makefile target `test-e2e` to run end-to-end tests separately

## 9. Documentation and Validation

- [x] 9.1 Create README.md with: setup instructions, configuration guide (including Unleashed API credentials), architecture overview, available metrics reference, known limitations (no noise floor/temperature via SNMP), minimum firmware requirements for airtime OIDs, test instructions (mock and e2e)
- [x] 9.2 Validate full stack comes up with docker compose up, both SNMP and REST API exporters scrape successfully, and all dashboards load correctly
