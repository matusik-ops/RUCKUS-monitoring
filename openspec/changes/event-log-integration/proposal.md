## Why

The monitoring stack currently shows real-time metrics (client count, signal, traffic) but has no visibility into discrete events: when clients connect/disconnect, when authentication fails (and which device caused it), when DFS radar forces a channel change, or when clients roam between APs. These events are critical for troubleshooting intermittent issues and understanding network behavior over time.

## What Changes

- Research and implement the `_cmdstat.jsp` event/syslog query format to retrieve event log entries from the Unleashed master AP
- Parse event log entries and expose them as Prometheus metrics (counters and info gauges) in the unleashed-exporter
- Track connect/disconnect events with client MAC + AP + timestamp
- Track authentication failure events with client MAC to identify which specific devices cause auth failures (e.g., on AP06/AP08)
- Track DFS radar detection events (when 5GHz channels change due to radar)
- Track roaming events (client moved from one AP to another)
- Add event-focused panels to Grafana dashboards: event timeline, auth failure breakdown, roaming history, DFS event log

## Capabilities

### New Capabilities
- `event-collection`: Event log retrieval from Unleashed API, parsing of event types (connect, disconnect, auth-fail, DFS radar, roam), and exposure as Prometheus metrics
- `event-dashboards`: Grafana panels for event visualization — event timeline, auth failure breakdown by device, roaming paths, DFS radar history

### Modified Capabilities
- `client-health`: Add auth failure count per client and last-disconnect reason to client health views

## Impact

- **unleashed-exporter/exporter.py**: New API query method for event log, new metric definitions (counters + info gauges), new parsing logic in the poll loop
- **Grafana dashboards**: New panels in Network Health and Client Health dashboards, potentially a new dedicated Events dashboard
- **Prometheus**: Additional time series for event counters (~5-10 new metric families)
- **API dependency**: Requires research into the exact `_cmdstat.jsp` XML payload for event/syslog queries — this is the main unknown
