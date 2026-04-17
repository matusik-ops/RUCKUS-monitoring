## 1. API Spike — Discover Event Log Format

- [ ] 1.1 Query the live AP with `<ajax-request action='getstat' comp='system'><syslog/></ajax-request>` and document the raw XML response schema (fields, event structure, timestamp format)
- [ ] 1.2 If syslog query doesn't work, try alternative payloads: `<event/>`, `<log/>`, `comp='stamgr'` with `<event/>`, or explore the AP web UI's event page network requests to find the correct query
- [ ] 1.3 Collect sample events for each target category (connect, disconnect, auth-fail, DFS radar, roam) by triggering them on the live AP, and save as test fixtures

## 2. Event Parsing and Classification

- [ ] 2.1 Add `get_events()` method to `UnleashedClient` class that queries the event log API and returns a list of event dicts
- [ ] 2.2 Implement event classifier function with regex patterns for: connect, disconnect, auth-fail, dfs-radar, roam, unclassified
- [ ] 2.3 Add timestamp-based deduplication: track last-seen event timestamp, only process newer events on each poll
- [ ] 2.4 Write mock tests for event parsing with the sample XML fixtures from task 1.3

## 3. Prometheus Metrics

- [ ] 3.1 Define counter metrics: `unleashed_event_total`, `unleashed_client_connect_total`, `unleashed_client_disconnect_total`, `unleashed_auth_fail_total`, `unleashed_dfs_radar_total`, `unleashed_roam_total`
- [ ] 3.2 Implement `update_event_metrics()` function that classifies events and increments appropriate counters
- [ ] 3.3 Integrate event collection into the main poll loop (call `get_events()` + `update_event_metrics()` each cycle)
- [ ] 3.4 Write mock tests verifying counter increments for each event type

## 4. Grafana Dashboard Panels

- [ ] 4.1 Add "Events" row to Network Health dashboard with event rate timeline panel (`rate(unleashed_event_total[5m])` by event_type)
- [ ] 4.2 Add auth failure breakdown table to Network Health (client MAC, AP, SSID, failure count)
- [ ] 4.3 Add DFS radar log panel to Network Health (AP name, channel, timestamp)
- [ ] 4.4 Add roaming event count panel to Network Health (from_ap → to_ap pairs)
- [ ] 4.5 Add auth failure count column to Client Health per-client table

## 5. Validation

- [ ] 5.1 Verify event metrics appear in Prometheus after exporter restart with live AP
- [ ] 5.2 Verify Grafana event panels populate with real data
- [ ] 5.3 Trigger a known event (e.g., disconnect/reconnect a client) and confirm it shows in the dashboard within one poll interval
