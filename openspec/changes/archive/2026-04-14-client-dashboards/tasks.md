## 1. Extend Exporter

- [x] 1.1 Add new numeric metrics: `unleashed_client_retries_total`, `unleashed_client_retry_bytes_total`, `unleashed_client_rx_pkts_total`, `unleashed_client_tx_pkts_total`, `unleashed_client_min_rssi_dbm`, `unleashed_client_max_rssi_dbm`
- [x] 1.2 Add `unleashed_client_info` gauge with labels: client_mac, hostname, ip, vlan, ap_name, ssid, radio_band, auth_method, encryption, dvctype, model_os
- [x] 1.3 Update `update_metrics()` to populate new metrics from existing XML response fields (`ip`, `vlan`, `dvctype`, `model`, `encryption`, `auth-method`, `total-retries`, `total-retry-bytes`, `total-rx-pkts`, `total-tx-pkts`, `min-received-signal-strength`, `max-received-signal-strength`)
- [x] 1.4 Stale-client cleanup: remove metric samples from new gauges when clients disconnect

## 2. Tests

- [x] 2.1 Update `tests/mock/fixtures/api_responses.py` to include the new XML fields in sample clients
- [x] 2.2 Update `tests/mock/test_unleashed_exporter.py` with tests for: retry metric, info gauge with labels, min/max RSSI, stale cleanup for new metrics
- [x] 2.3 Run full test suite and verify all pass

## 3. Clients Overview Dashboard

- [x] 3.1 Create `grafana/dashboards/clients-overview.json` with uid `ruckus-clients-overview`
- [x] 3.2 Add template variables: $ap_name, $ssid, $radio_band
- [x] 3.3 Build main client table with all columns (Hostname, MAC, OS, IP, VLAN, AP, SSID, Band, Channel, Encryption, Auth, RSSI, SNR, Noise, Link Speed, Rx/Tx Mbps current, Total Rx/Tx bytes, Retries, Connected Since, Duration), using joinByField on client_mac to merge info + numeric queries
- [x] 3.4 Add color-coded thresholds for RSSI, SNR, Retries
- [x] 3.5 Add KPI row: Total Clients, Clients per Band pie, Clients per SSID pie

## 4. Client Health Dashboard (replace existing)

- [x] 4.1 Rewrite `grafana/dashboards/client-health.json` keeping uid `ruckus-client-health`
- [x] 4.2 Add fleet KPI row: Total Clients, Good Signal %, Avg RSSI, Weak Signal Count, High Retry Count, Low Link Rate Count
- [x] 4.3 Add retry rate computation panel: `rate(retries[5m]) / clamp_min(rate(tx_pkts[5m]), 1) * 100` per client, thresholds green<2, yellow<10, red>10
- [x] 4.4 Add problem-client tables: Weak Signal (RSSI<-70), High Retry (>10%), Low Link Rate (<30 Mbps)
- [x] 4.5 Add per-client time-series with template variables: RSSI, SNR, Link Speed, Retry Rate, Throughput
- [x] 4.6 Add documentation text panel explaining retry rate as packet-loss proxy and noting latency/jitter require probes

## 5. Verify Against Live AP

- [x] 5.1 Rebuild unleashed-exporter, verify new metrics appear on /metrics endpoint
- [x] 5.2 Confirm Prometheus scrapes new metrics
- [x] 5.3 Load both dashboards, verify all panels show data with real clients
- [ ] 5.4 Test sorting, filtering, template variables

## 6. Documentation

- [x] 6.1 Update METRICS.md with new per-client metrics section
- [x] 6.2 Update README.md dashboards list (add Clients Overview)
