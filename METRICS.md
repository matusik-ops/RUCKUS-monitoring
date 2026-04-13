# Collected Metrics Reference

This file documents **every measurement value** collected from the Ruckus Unleashed AP via two data sources:

1. **SNMP** — from the master AP at OID base `1.3.6.1.4.1.25053.1.15`
2. **Web API** — from `_cmdstat.jsp` XML interface (per-client, per-AP/radio, per-rogue)

All metrics are stored in Prometheus and queryable via PromQL in Grafana. Both sources are polled every 60 seconds.

---

## SOURCE 1: SNMP (RUCKUS-UNLEASHED-SYSTEM-MIB + standard MIBs)

Polled directly from the master AP at 10.91.1.109 via SNMP v2c.
OID base: `1.3.6.1.4.1.25053.1.15` (RUCKUS-UNLEASHED-SYSTEM-MIB, firmware 200.15+)
Labels: `instance` (AP IP)

### System Info (from RUCKUS-UNLEASHED-SYSTEM-MIB)

| Prometheus Metric | OID Suffix | Type | Description |
|---|---|---|---|
| `sysUpTime` | 1.3.6.1.2.1.1.3 | gauge | System uptime (1/100s) |
| `ruckusUnleashedSystemStatsNumAP` | .15.1 | gauge | Number of APs in network |
| `ruckusUnleashedSystemStatsNumRegisteredAP` | .15.15 | gauge | Number of registered APs |

### Client Counts

| Prometheus Metric | OID Suffix | Type | Description |
|---|---|---|---|
| `ruckusUnleashedSystemStatsNumSta` | .15.2 | gauge | Authenticated clients |
| `ruckusUnleashedSystemStatsAllNumSta` | .15.30 | gauge | All clients incl. unauthorized |

### System Resources

| Prometheus Metric | OID Suffix | Type | Description |
|---|---|---|---|
| `ruckusUnleashedSystemStatsCPUUtil` | .15.13 | gauge | CPU utilization (%) |
| `ruckusUnleashedSystemStatsMemoryUtil` | .15.14 | gauge | Memory utilization (%) |

### Aggregate WLAN Traffic Counters

| Prometheus Metric | OID Suffix | Type | Description |
|---|---|---|---|
| `ruckusUnleashedSystemStatsWLANTotalRxPkts` | .15.5 | counter | Total wireless Rx packets |
| `ruckusUnleashedSystemStatsWLANTotalRxBytes` | .15.6 | counter | Total wireless Rx bytes |
| `ruckusUnleashedSystemStatsWLANTotalTxPkts` | .15.8 | counter | Total wireless Tx packets |
| `ruckusUnleashedSystemStatsWLANTotalTxBytes` | .15.9 | counter | Total wireless Tx bytes |
| `ruckusUnleashedSystemStatsWLANTotalRxMulticast` | .15.7 | counter | Total Rx multicast |
| `ruckusUnleashedSystemStatsWLANTotalTxMulticast` | .15.10 | counter | Total Tx multicast |
| `ruckusUnleashedSystemStatsWLANTotalTxFail` | .15.11 | counter | Total Tx failures |
| `ruckusUnleashedSystemStatsWLANTotalTxRetry` | .15.12 | counter | Total Tx retries |
| `ruckusUnleashedSystemStatsWLANTotalAssocFail` | .15.16 | counter | Total assoc failures |
| `ruckusUnleashedSystemStatsWLANTotalRxErrFrm` | .15.17 | counter | Total Rx error frames |
| `ruckusUnleashedSystemStatsWLANTotalTxDroppedPkt` | .15.19 | counter | Total Tx dropped packets |
| `ruckusUnleashedSystemStatsWLANTotalTxErrFrm` | .15.20 | counter | Total Tx error frames |
| `ruckusUnleashedSystemStatsWLANTotalTxDroppedFrm` | .15.21 | counter | Total Tx dropped frames |

### Ethernet Interface Counters (from IF-MIB)

Labels: `ifDescr` (interface name like `eth0`, `wifi0`, `wlan0`, `br0`)

| Prometheus Metric | OID | Type | Description |
|---|---|---|---|
| `ifInOctets` | 1.3.6.1.2.1.2.2.1.10 | counter | Bytes received on interface |
| `ifOutOctets` | 1.3.6.1.2.1.2.2.1.16 | counter | Bytes transmitted on interface |
| `ifInErrors` | 1.3.6.1.2.1.2.2.1.14 | counter | Inbound errors |
| `ifOutErrors` | 1.3.6.1.2.1.2.2.1.20 | counter | Outbound errors |
| `ifOperStatus` | 1.3.6.1.2.1.2.2.1.8 | gauge | Interface up (1) / down (2) |

---

## SOURCE 2: Web API — Per-Client (`_cmdstat.jsp <client INTERVAL-STATS='yes'/>`)

Polled per AP via XML POST. Each client appears once per poll.
Labels: `client_mac`, `ap_name`, `ssid`, `radio_band` (2.4g/5g), `hostname`

### Signal & Channel Info

| Prometheus Metric | XML Field | Type | Description |
|---|---|---|---|
| `unleashed_client_rssi_dbm` | `received-signal-strength` | gauge | Received signal strength (dBm) |
| `unleashed_client_snr_db` | `rssi` | gauge | SNR (AP-reported scaled value) |
| `unleashed_client_noise_floor_dbm` | `noise-floor` | gauge | Noise floor (dBm), typically -96 |
| `unleashed_client_channel` | `channel` | gauge | Channel the client is on |

### Performance

| Prometheus Metric | XML Field | Type | Description |
|---|---|---|---|
| `unleashed_client_tx_rate_kbps` | `tx-rate` (interval-stats) | gauge | Negotiated PHY rate (Kbps) |
| `unleashed_client_rx_bytes_total` | `total-rx-bytes` | gauge | Cumulative bytes received |
| `unleashed_client_tx_bytes_total` | `total-tx-bytes` | gauge | Cumulative bytes transmitted |

### Session

| Prometheus Metric | XML Field | Type | Description |
|---|---|---|---|
| `unleashed_client_assoc_time_seconds` | `first-assoc` | gauge | Association start time (unix ts) |

### Derived Aggregates (no extra label, computed from client list)

| Prometheus Metric | Computed From | Type | Description |
|---|---|---|---|
| `unleashed_client_count` | count of clients | gauge | Total connected clients |
| `unleashed_clients_per_ssid{ssid}` | count by SSID | gauge | Clients per SSID |
| `unleashed_clients_per_ap{ap_name}` | count by AP | gauge | Clients per AP |

---

## SOURCE 3: Web API — Per-AP / Per-Radio (`_cmdstat.jsp <ap LEVEL='1'/>`)

Polled per AP. Each AP has 2 radios (2.4GHz, 5GHz).
Labels: `ap_name`, `radio_band` (2.4g/5g), `channel`

### Airtime Counters (cumulative since AP boot/reset)

These four are related: `total = busy + rx + tx`

| Prometheus Metric | XML Field | Type | Description |
|---|---|---|---|
| `unleashed_radio_airtime_total` | `airtime-total` | gauge | Total observed airtime (=busy+rx+tx) |
| `unleashed_radio_airtime_busy` | `airtime-busy` | gauge | Time busy from interference / other-BSS traffic |
| `unleashed_radio_airtime_rx` | `airtime-rx` | gauge | Time spent receiving |
| `unleashed_radio_airtime_tx` | `airtime-tx` | gauge | Time spent transmitting |

### Client Activity

| Prometheus Metric | XML Field | Type | Description |
|---|---|---|---|
| `unleashed_radio_num_sta` | `num-sta` | gauge | Clients connected to this radio |
| `unleashed_radio_avg_rssi` | `avg-rssi` | gauge | Average client RSSI on this radio |

### Traffic Counters

| Prometheus Metric | XML Field | Type | Description |
|---|---|---|---|
| `unleashed_radio_tx_bytes_total` | `radio-total-tx-bytes` | gauge | Total Tx bytes |
| `unleashed_radio_rx_bytes_total` | `radio-total-rx-bytes` | gauge | Total Rx bytes |
| `unleashed_radio_tx_pkts_total` | `radio-total-tx-pkts` | gauge | Total Tx packets |
| `unleashed_radio_rx_pkts_total` | `radio-total-rx-pkts` | gauge | Total Rx packets |

### Errors & Quality

| Prometheus Metric | XML Field | Type | Description |
|---|---|---|---|
| `unleashed_radio_tx_fail_total` | `radio-total-tx-fail` | gauge | Tx failures (frames not delivered) |
| `unleashed_radio_retries_total` | `radio-total-retries` | gauge | Tx retries |
| `unleashed_radio_fcs_error_total` | `total-fcs-err` | gauge | Frame checksum errors (corrupted Rx) |

### Auth/Assoc Counters

| Prometheus Metric | XML Field | Type | Description |
|---|---|---|---|
| `unleashed_radio_auth_fail` | `mgmt-auth-fail` | gauge | Failed auth attempts |
| `unleashed_radio_auth_success` | `mgmt-auth-success` | gauge | Successful auth |
| `unleashed_radio_assoc_fail` | `mgmt-assoc-fail` | gauge | Failed assoc |
| `unleashed_radio_assoc_success` | `mgmt-assoc-success` | gauge | Successful assoc |

### Radio Configuration

| Prometheus Metric | XML Field | Type | Description |
|---|---|---|---|
| `unleashed_radio_channel` | `channel` | gauge | Current channel number |
| `unleashed_radio_tx_power` | `tx-power` | gauge | Transmit power setting |
| `unleashed_radio_channelization` | `channelization` | gauge | Channel width in MHz (20/40/80) |

---

## SOURCE 4: Web API — Rogue Detection (`_cmdstat.jsp <rogue/>`)

Polled per AP. Returns rogue APs detected by our APs.
Labels on `unleashed_rogue_rssi_dbm`: `rogue_mac`, `rogue_ssid`, `rogue_channel`, `rogue_band`, `rogue_type`, `is_malicious`, `detector_ap`

| Prometheus Metric | XML Source | Type | Description |
|---|---|---|---|
| `unleashed_rogue_rssi_dbm` | per `<detection>` element | gauge | Signal strength of rogue as seen by our AP |
| `unleashed_rogue_count` | count of unique rogue MACs | gauge | Total unique rogue APs |
| `unleashed_rogue_malicious_count` | count of "malicious AP (Same-Network)" | gauge | **Security risk** — rogues impersonating our SSID |
| `unleashed_rogue_count_by_band{radio_band}` | grouped by band | gauge | Rogues per band |
| `unleashed_rogue_count_by_channel{channel, radio_band}` | grouped by channel | gauge | Rogues per channel |

---

## Exporter Health (operational metrics, not from AP)

| Prometheus Metric | Type | Description |
|---|---|---|
| `unleashed_exporter_polls_total` | counter | Successful polls of the API |
| `unleashed_exporter_errors_total{type}` | counter | Errors by type: auth_failure, connection_error, api_error, parse_error, csrf_failure |
| `up{job="snmp"}` | gauge | SNMP target reachable (1/0) |
| `up{job="unleashed"}` | gauge | Web API exporter reachable (1/0) |

---

## NOT Available

These are commonly desired but not exposed by either source on firmware 200.15:

| Metric | Why | Workaround |
|---|---|---|
| Channel utilization vs idle time | API only gives busy+rx+tx breakdown that always sums to total | Use per-component values (busy %, rx %, tx %) or AP CLI `get airtime` (requires SSH) |
| Temperature | Not exposed by any Ruckus interface | None |
| Per-client Rx data rate | Only Tx rate available in interval-stats | Use `unleashed_client_tx_rate_kbps` |
| Per-client retries | Not in the client XML (only in AP-level counters) | Use `unleashed_radio_retries_total` for AP-wide view |
| Connect/disconnect events | Event log API format unknown / not implemented | Track via Prometheus rate of `unleashed_client_count` change |
| DFS radar events | Would require event log | None |
