## Why

The planned Network Health dashboard requires data sources we don't currently collect: rogue AP detection (for "Rogue Devices" tab and channel congestion analysis) and event-based history (connections, disconnections, signal drops). The Unleashed `_cmdstat.jsp` API exposes both via additional XML queries — verified against the live AP, the rogue query returns ~20 detected rogue APs including 2 marked as "malicious AP (Same-Network)" which represent real security concerns.

## What Changes

- Extend the Unleashed exporter to query `<rogue/>` per poll cycle and expose per-rogue-AP metrics (RSSI, channel, band, detection count, rogue type)
- Add per-detecting-AP labels so we can see which of our APs detected each rogue and where
- Expose summary metrics: total rogues, malicious rogues, rogues per band, rogues per channel
- Investigate and add event log query (`<event/>`) for connect/disconnect/signal-drop events as a stretch goal — needs format research

## Capabilities

### New Capabilities
- `rogue-detection`: Per-rogue-AP metrics from `_cmdstat.jsp <rogue/>` query — MAC, SSID, channel, radio band, signal strength as detected by each of our APs, rogue classification (regular AP vs malicious same-network)

### Modified Capabilities
- `client-health`: Will additionally query event log to detect client disconnect/reconnect events (if event API works)

## Impact

- **Code**: Extend `unleashed-exporter/exporter.py` with `get_rogues()` method and `update_rogue_metrics()`
- **Polling load**: Adds one more `_cmdstat.jsp` query per cycle (now 3 queries per 60s — client, AP, rogue). Rogue query returns moderate XML (~10 KB).
- **No new dependencies**: Reuses existing requests/XML stack
- **No infrastructure changes**: No new containers
