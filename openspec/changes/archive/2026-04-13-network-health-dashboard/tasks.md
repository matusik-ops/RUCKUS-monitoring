## 1. Dashboard Scaffolding

- [x] 1.1 Create `grafana/dashboards/network-health.json` with base dashboard structure: title "Ruckus Network Health", uid `ruckus-network-health`, 30s refresh, time range now-6h, template variables for `$ap_name` and `$radio_band`
- [x] 1.2 Add 5 collapsible row panels (Overview expanded, others collapsed by default): Overview, RF Environment, Airtime History, Channel History, Rogue Devices

## 2. Overview Section

- [x] 2.1 Add Network Health % stat panel with composite score formula and color thresholds (green ≥80, yellow ≥50, red <50)
- [x] 2.2 Add KPI row: APs Online / Total, Total Clients (current), Avg Client RSSI, Max Clients (in time range), Active Alerts count
- [x] 2.3 Add Peak Hour panel showing time of max client count in selected range
- [x] 2.4 Add Active Alerts breakdown: weak clients count, congested radios count, high-auth-fail APs count, malicious rogues count

## 3. RF Environment Section

- [x] 3.1 Add per-AP per-radio table panel with all required columns (AP, Band, Channel, Width, Clients, Avg RSSI, Airtime Busy/Rx/Tx %, Tx Retries, Tx Failures, FCS Errors, Auth Fail %); sortable; color thresholds on numeric columns
- [x] 3.2 Add 2.4GHz channel congestion bar chart combining `unleashed_rogue_count_by_channel{radio_band="2.4g"}` and our APs per channel
- [x] 3.3 Add 5GHz channel congestion bar chart (same approach for 5g)

## 4. Airtime History Section

- [x] 4.1 Add airtime busy % per AP per band time-series (with `$ap_name` and `$radio_band` variables)
- [x] 4.2 Add airtime Rx % time-series
- [x] 4.3 Add airtime Tx % time-series

## 5. Channel History Section

- [x] 5.1 Add channel-over-time per AP per band time-series (shows step changes when channels switch)
- [x] 5.2 Add Tx power-over-time per AP per band time-series

## 6. Rogue Devices Section

- [x] 6.1 Add 3 KPI stats: Total Rogues, Malicious Rogues (red threshold), Strongest Rogue Signal (closest dBm)
- [x] 6.2 Add rogues-per-channel bar chart split by band
- [x] 6.3 Add rogue table with: SSID, MAC, Channel, Band, Type, Detector AP, RSSI (color-coded), sorted by RSSI descending (closest first)

## 7. Verify

- [x] 7.1 Validate JSON, restart Grafana, confirm dashboard loads
- [x] 7.2 Verify all 5 sections render correctly with real data, no "No data" panels
- [x] 7.3 Test row collapse/expand behavior (manual UI test required)
- [x] 7.4 Test template variables (filter by AP, by band) (manual UI test required)
