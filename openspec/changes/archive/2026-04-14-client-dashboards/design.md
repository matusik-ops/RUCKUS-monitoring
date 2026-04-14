## Context

The existing `Client Health` dashboard is a single view mixing client table (MAC, SSID, signal, data rate, bytes, association time) with time-series for RSSI/SNR/data rate. It works but is cramped and doesn't expose several useful fields the Ruckus API already returns (IP, VLAN, OS, encryption, retries).

The `_cmdstat.jsp <client INTERVAL-STATS='yes'/>` XML response includes per-client:
- Identity: `mac`, `hostname`, `ip`, `vlan`, `dvctype`, `model`, `dvcinfo`
- Connection: `ap-name`, `ssid`, `radio-band`, `channel`, `first-assoc`, `auth-method`, `encryption`
- Signal: `received-signal-strength` (dBm), `rssi` (AP scaled), `noise-floor`, `channel`
- Performance: `tx-rate` (Kbps), `total-rx-bytes`, `total-tx-bytes`, `total-rx-pkts`, `total-tx-pkts`
- Quality: `total-retries`, `total-retry-bytes`, `total-rx-crc-errs`, `tx-drop-data`, `tx-drop-mgmt`

## Goals / Non-Goals

**Goals:**
- Two focused dashboards replacing the current Client Health
- Expose all useful client fields from the API
- Make problem clients obvious via color-coded thresholds
- Per-client drill-down via template variables

**Non-Goals:**
- End-to-end latency/jitter/ICMP packet loss (requires external probing, deferred to future WAN/probe change)
- Historical client records beyond Prometheus retention
- Per-client per-application traffic breakdown (DPI)

## Decisions

### 1. Split into two dashboards

- **Clients Overview** — large wide table with many columns, all clients visible, sortable. Designed for "find client X" / "show me all clients" use cases. Minimal graphs.
- **Client Health** — focused on problem identification: single big gauge for fleet quality, time-series per metric with AP/band/client template variables, problem-client highlight tables.

### 2. Identity data via info gauge pattern

To avoid high-cardinality label explosion on every numeric metric (Prometheus best practice):
- Create `unleashed_client_info` gauge with labels: mac, hostname, ip, vlan, ap_name, ssid, radio_band, auth_method, encryption, dvctype, model_os
- Existing numeric metrics keep their current label set (mac, ap, ssid, band, hostname)
- Dashboards use `joinByField` on mac to merge info + numeric data

### 3. Retry Rate as packet-loss proxy

The "Client Health" dashboard uses retry rate = `rate(total_retries[5m]) / rate(total_tx_pkts[5m])` as the WiFi packet-loss indicator. This is a standard industry approach:
- 0-2% retries = excellent link
- 2-10% = acceptable
- 10-20% = poor
- >20% = severely degraded (clients will experience slow speeds)

This replaces the ICMP-style packet loss the user asked for, which isn't available via the API. Documented clearly in the dashboard.

### 4. RSSI min/max from interval-stats

The interval-stats block has `min-received-signal-strength`, `max-received-signal-strength`, `first-rssi`, `last-rssi`. Instead of exposing all four as metrics (too many), expose `min` and `max` only — they bracket the signal variation over the 5-minute window and indicate movement/fading.

## Risks / Trade-offs

- **Cardinality** → Adding VLAN/IP/OS labels could create label cardinality if clients are very mobile (new client_info series per MAC+IP combination). Mitigation: the info gauge is rate-limited by MAC uniqueness; IPs don't change often for a given client session.
- **Backward compatibility** → Current Client Health dashboard will be replaced. Users navigating to old URL will need updating. Mitigation: keep old UID `ruckus-client-health` for the new Client Health dashboard (same purpose); new Clients Overview gets a new UID.
- **Deprecation** → The existing dashboard had panels for "Client Data Rate Over Time", "Client RSSI Over Time" etc — these will exist in new Client Health dashboard so no feature loss.
