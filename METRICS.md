# Collected Metrics Reference

All metrics are stored in Prometheus and queryable via PromQL in Grafana.

## SNMP Metrics (via Prometheus SNMP Exporter)

Collected from the Unleashed master AP via SNMP v2c. OID base: `1.3.6.1.4.1.25053.1.15` (RUCKUS-UNLEASHED-SYSTEM-MIB, firmware 200.15+).

Scraped every 60s (configurable). Labels: `instance` (AP IP address).

| Prometheus Metric | Type | Description | What it tells you | Example PromQL |
|---|---|---|---|---|
| `sysUpTime` | gauge | System uptime in hundredths of a second | How long the AP has been running; drops indicate reboots | `sysUpTime / 100 / 86400` (uptime in days) |
| `ruckusUnleashedSystemStatsNumAP` | gauge | Number of APs in the Unleashed network | Fleet size; drop means an AP disconnected | `ruckusUnleashedSystemStatsNumAP` |
| `ruckusUnleashedSystemStatsNumRegisteredAP` | gauge | Number of registered/approved APs | Should match NumAP; mismatch means pending APs | `ruckusUnleashedSystemStatsNumRegisteredAP` |
| `ruckusUnleashedSystemStatsNumSta` | gauge | Number of authorized (authenticated) clients | Active users on the network | `ruckusUnleashedSystemStatsNumSta` |
| `ruckusUnleashedSystemStatsAllNumSta` | gauge | Number of all clients (including unauthorized) | Total wireless associations; gap with NumSta = auth issues | `ruckusUnleashedSystemStatsAllNumSta` |
| `ruckusUnleashedSystemStatsCPUUtil` | gauge | CPU utilization (%) | AP processing load; sustained >80% = overloaded | `ruckusUnleashedSystemStatsCPUUtil` |
| `ruckusUnleashedSystemStatsMemoryUtil` | gauge | Memory utilization (%) | RAM pressure; high values may cause instability | `ruckusUnleashedSystemStatsMemoryUtil` |
| `ruckusUnleashedSystemStatsWLANTotalRxPkts` | counter | Total wireless packets received | Wireless inbound volume | `rate(ruckusUnleashedSystemStatsWLANTotalRxPkts[5m])` |
| `ruckusUnleashedSystemStatsWLANTotalRxBytes` | counter | Total wireless bytes received | Wireless inbound throughput | `rate(ruckusUnleashedSystemStatsWLANTotalRxBytes[5m]) * 8` (bps) |
| `ruckusUnleashedSystemStatsWLANTotalTxPkts` | counter | Total wireless packets transmitted | Wireless outbound volume | `rate(ruckusUnleashedSystemStatsWLANTotalTxPkts[5m])` |
| `ruckusUnleashedSystemStatsWLANTotalTxBytes` | counter | Total wireless bytes transmitted | Wireless outbound throughput | `rate(ruckusUnleashedSystemStatsWLANTotalTxBytes[5m]) * 8` (bps) |
| `ruckusUnleashedSystemStatsWLANTotalTxFail` | counter | Total wireless transmit failures | Frames that could not be delivered; sustained increase = RF issues | `rate(ruckusUnleashedSystemStatsWLANTotalTxFail[5m])` |
| `ruckusUnleashedSystemStatsWLANTotalTxRetry` | counter | Total wireless transmit retries | Frames re-sent due to no ACK; high rate = interference or distance | `rate(ruckusUnleashedSystemStatsWLANTotalTxRetry[5m])` |
| `ruckusUnleashedSystemStatsWLANTotalRxMulticast` | counter | Total wireless Rx multicast frames | Multicast traffic volume | `rate(ruckusUnleashedSystemStatsWLANTotalRxMulticast[5m])` |
| `ruckusUnleashedSystemStatsWLANTotalTxMulticast` | counter | Total wireless Tx multicast frames | Multicast traffic volume | `rate(ruckusUnleashedSystemStatsWLANTotalTxMulticast[5m])` |
| `ruckusUnleashedSystemStatsWLANTotalAssocFail` | counter | Total wireless association failures | Clients failing to connect; spike = capacity or config issue | `rate(ruckusUnleashedSystemStatsWLANTotalAssocFail[5m])` |
| `ruckusUnleashedSystemStatsWLANTotalRxErrFrm` | counter | Total wireless Rx error frames | Corrupted inbound frames; high rate = interference | `rate(ruckusUnleashedSystemStatsWLANTotalRxErrFrm[5m])` |
| `ruckusUnleashedSystemStatsWLANTotalTxDroppedPkt` | counter | Total wireless Tx dropped packets | Frames dropped before transmission | `rate(ruckusUnleashedSystemStatsWLANTotalTxDroppedPkt[5m])` |
| `ruckusUnleashedSystemStatsWLANTotalTxErrFrm` | counter | Total wireless Tx error frames | Transmission errors | `rate(ruckusUnleashedSystemStatsWLANTotalTxErrFrm[5m])` |
| `ruckusUnleashedSystemStatsWLANTotalTxDroppedFrm` | counter | Total wireless Tx dropped frames | Frames dropped (queue full, etc.) | `rate(ruckusUnleashedSystemStatsWLANTotalTxDroppedFrm[5m])` |
| `ifInOctets` | counter | Ethernet interface bytes received | Wired ingress throughput per interface | `rate(ifInOctets{ifDescr="eth0"}[5m]) * 8` (bps) |
| `ifOutOctets` | counter | Ethernet interface bytes transmitted | Wired egress throughput per interface | `rate(ifOutOctets{ifDescr="eth0"}[5m]) * 8` (bps) |
| `ifInErrors` | counter | Ethernet interface inbound errors | Wired Rx errors; non-zero = cable or switch issue | `rate(ifInErrors{ifDescr="eth0"}[5m])` |
| `ifOutErrors` | counter | Ethernet interface outbound errors | Wired Tx errors | `rate(ifOutErrors{ifDescr="eth0"}[5m])` |
| `ifOperStatus` | gauge | Ethernet interface operational status (1=up, 2=down) | Whether each Ethernet port is linked | `ifOperStatus{ifDescr="eth0"}` |

## Web API Metrics (via Unleashed Exporter)

Collected from the Unleashed _cmdstat.jsp XML interface with `INTERVAL-STATS='yes'`. Polled every 60s (configurable).

Labels: `client_mac`, `ap_name`, `ssid`, `radio_band` (2.4g/5g), `hostname`.

| Prometheus Metric | Type | Description | What it tells you | Example PromQL |
|---|---|---|---|---|
| `unleashed_client_rssi_dbm` | gauge | Client received signal strength (dBm) | Signal quality; below -75 = poor, below -80 = very poor | `unleashed_client_rssi_dbm{ap_name="AP01"}` |
| `unleashed_client_snr_db` | gauge | Client SNR (AP-reported RSSI value) | Signal-to-noise ratio; higher is better | `unleashed_client_snr_db` |
| `unleashed_client_noise_floor_dbm` | gauge | Client noise floor (dBm) | RF environment noise; typically -96; higher = more interference | `unleashed_client_noise_floor_dbm` |
| `unleashed_client_tx_rate_kbps` | gauge | Client Tx data rate (Kbps) | Negotiated PHY rate; e.g., 135000 = 135 Mbps. Low rate = poor signal or old client | `unleashed_client_tx_rate_kbps / 1000` (Mbps) |
| `unleashed_client_rx_bytes_total` | gauge | Client total received bytes | Cumulative download traffic per client | `unleashed_client_rx_bytes_total{client_mac="aa:bb:cc:dd:ee:01"}` |
| `unleashed_client_tx_bytes_total` | gauge | Client total transmitted bytes | Cumulative upload traffic per client | `unleashed_client_tx_bytes_total` |
| `unleashed_client_assoc_time_seconds` | gauge | Client association start time (unix timestamp) | When client connected; `time() - metric` = session duration | `time() - unleashed_client_assoc_time_seconds` (duration) |
| `unleashed_client_channel` | gauge | Wireless channel the client is on | Which channel/radio the client uses; helps identify band distribution | `count by (channel) (unleashed_client_channel)` |
| `unleashed_client_count` | gauge | Total number of connected clients | Quick client count without label cardinality | `unleashed_client_count` |
| `unleashed_clients_per_ssid` | gauge | Client count per SSID | Load distribution across SSIDs | `unleashed_clients_per_ssid` |
| `unleashed_clients_per_ap` | gauge | Client count per AP | Load distribution across APs; imbalance = sticky clients or coverage gap | `unleashed_clients_per_ap` |

## Exporter Health Metrics

| Prometheus Metric | Type | Description | Example PromQL |
|---|---|---|---|
| `unleashed_exporter_polls_total` | counter | Total successful polls | `rate(unleashed_exporter_polls_total[5m])` |
| `unleashed_exporter_errors_total` | counter | Total poll errors (labeled by type: auth_failure, connection_error, api_error, parse_error, csrf_failure) | `unleashed_exporter_errors_total` |
| `up{job="snmp"}` | gauge | SNMP target reachability (1=up, 0=down) | `up{job="snmp"}` |
| `up{job="unleashed"}` | gauge | Unleashed exporter reachability | `up{job="unleashed"}` |

## Not Available (firmware 200.15 limitations)

| Metric | Why | Workaround |
|---|---|---|
| Per-radio channel utilization | RUCKUS-RADIO-MIB OIDs not present on firmware 200.15 | Use per-client RSSI distribution as proxy |
| Per-radio airtime | Same — not in SNMP tree | None via SNMP; may be available via CLI `get airtime` |
| Per-radio client counts | Same — only aggregate counts via SNMP | Use `unleashed_clients_per_ap` from web API |
| Per-radio auth/assoc failure rates | Same — only aggregate counters via SNMP | Monitor `ruckusUnleashedSystemStatsWLANTotalAssocFail` rate |
| Temperature | Not exposed by any Ruckus interface | None |
| Per-client data rate (Rx) | Only Tx rate available in interval-stats | Use `unleashed_client_tx_rate_kbps` |
