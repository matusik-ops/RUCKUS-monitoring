## Why

Currently the single Client Health dashboard mixes inventory data with signal/quality data and doesn't expose many client attributes the Ruckus API provides (IP, VLAN, OS, encryption, retries). Operators need two focused views: one comprehensive "who is connected and how" (inventory + traffic) and one "is this client experiencing problems" (health/quality) — especially to quickly identify clients with poor WiFi experience.

## What Changes

- Extend the Unleashed exporter to collect additional per-client fields from the `_cmdstat.jsp` XML already returned: `ip`, `vlan`, `dvctype`, `model` (OS), `encryption`, `auth-method`, `total-retries`, `total-retry-bytes`, `total-rx-pkts`, `total-tx-pkts`, `received-signal-strength` history (min/max/avg from interval-stats).
- Replace the existing Client Health dashboard with two new dashboards:
  1. **Clients Overview** — comprehensive inventory + live traffic view (MAC, hostname, OS, IP, VLAN, AP, SSID, band, encryption, RSSI, SNR, noise, channel, link speed, current Rx/Tx Mbps, total bytes since connect, retries, connected since, association duration).
  2. **Client Health** — signal/quality view focused on identifying problem clients (RSSI, SNR, noise floor, retry rate as WiFi packet-loss proxy, link speed, current throughput, per-client trends over time).
- Archive the existing `Client Health` dashboard.

## Capabilities

### New Capabilities
- `client-dashboards`: Two Grafana dashboards — clients-overview (inventory + traffic) and client-health (signal + quality indicators). Plus new per-client metrics for IP/VLAN/OS/encryption/retries exposed from the web API.

### Modified Capabilities
- `client-health` (existing): Expanded set of per-client metrics. Old dashboard replaced by two new ones.

## Impact

- **Exporter**: Add ~7 new per-client metrics and labels to existing metrics (device type, OS, IP, VLAN, encryption stored as labels on a new `unleashed_client_info` gauge for cardinality control)
- **Dashboards**: New `clients-overview.json` + `client-health.json`, old `client-health.json` replaced
- **No new data sources**: All fields are already in the XML response we receive — just not currently exposed
- **Known limitations** (documented): end-to-end latency, jitter, and ICMP packet loss are NOT available from the Ruckus API. Retry rate at the MAC layer serves as a WiFi-native proxy for packet loss quality.
