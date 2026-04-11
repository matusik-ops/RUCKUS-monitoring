## 1. Extend Unleashed Exporter

- [x] 1.1 Add `get_ap_stats()` method to UnleashedClient that POSTs `<ap LEVEL='1'/>` to _cmdstat.jsp and parses per-AP, per-radio XML elements
- [x] 1.2 Define new Prometheus metrics: `unleashed_radio_airtime_total`, `unleashed_radio_airtime_busy`, `unleashed_radio_airtime_rx`, `unleashed_radio_airtime_tx`, `unleashed_radio_num_sta`, `unleashed_radio_avg_rssi`, `unleashed_radio_tx_bytes_total`, `unleashed_radio_rx_bytes_total`, `unleashed_radio_tx_fail_total`, `unleashed_radio_retries_total`, `unleashed_radio_auth_fail`, `unleashed_radio_auth_success`, `unleashed_radio_assoc_fail`, `unleashed_radio_assoc_success`, `unleashed_radio_channel`, `unleashed_radio_tx_power`, `unleashed_radio_channelization` — labeled by ap_name, radio_band, channel
- [x] 1.3 Add `update_radio_metrics()` function that processes the AP stats XML and sets all per-radio gauges; exclude disconnected APs (state!=1); clean up stale metrics for APs that disappear
- [x] 1.4 Call both `get_stations()` and `get_ap_stats()` in the main poll loop
- [x] 1.5 Rebuild exporter container and verify new metrics appear on /metrics endpoint with real AP data

## 2. Update Alerting Rules

- [x] 2.1 Add HighAirtimeBusy alert rule: `unleashed_radio_airtime_busy / unleashed_radio_airtime_total > 0.5` for 5m
- [x] 2.2 Add RadioAuthFailureSpike alert rule: `increase(unleashed_radio_auth_fail[5m]) > 100`
- [x] 2.3 Validate alert rules with promtool (if available) or manual review

## 3. Update Grafana Dashboards

- [x] 3.1 Update radio health dashboard: replace aggregate Tx panels with per-radio airtime utilization (busy/total), per-radio client count, per-radio avg RSSI, per-radio Tx retries/failures, per-radio auth/assoc failures — with AP and radio band template variables
- [x] 3.2 Update fleet overview dashboard: add per-radio airtime-busy columns to the AP status table
- [x] 3.3 Verify dashboards render with real data in Grafana

## 4. Update Tests

- [x] 4.1 Add mock AP stats XML fixture based on real response from live AP
- [x] 4.2 Write tests for `get_ap_stats()` and `update_radio_metrics()`: correct metric values, stale AP cleanup, disconnected AP exclusion
- [x] 4.3 Run mock tests and verify all pass

## 5. Update Documentation and Specs

- [x] 5.1 Update METRICS.md with new per-radio metrics table
- [x] 5.2 Update README.md available metrics section
- [x] 5.3 Update ruckus-r720-monitoring-dashboard specs (snmp-collection, radio-health) to remove "not available" statements for per-radio data, noting it's available via web API
