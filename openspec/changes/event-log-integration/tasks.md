## 1. API Spike — Discover Event Log Format

- [x] 1.1 Query the live AP with `<ajax-request action='getstat' comp='system'><syslog/></ajax-request>` and document the raw XML response schema — DONE: `comp='system'` returned empty; discovered `comp='eventd'` by reverse-engineering AP's JavaScript
- [x] 1.2 Try alternative payloads and discover correct query — DONE: `<alarm/>` and `<xevent/>` under `comp='eventd'` return structured XML with event types: AP join, radio on/off, rogue detected, warm reboot, firmware upgrade
- [x] 1.3 Collect sample events — DONE: documented available event types. Client connect/disconnect NOT available as discrete events (must derive from client list diffs)

## 2. Event Parsing and Classification

- [x] 2.1 Add `get_alarms()` and `get_xevents()` methods to `UnleashedClient` class that query `comp='eventd'` and return lists of event dicts
- [x] 2.2 Implement event classification in `update_alarm_metrics()` and `update_xevent_metrics()` — classifies by alarm `name` field (AP Radio Off, AP Radio On, AP Has Joined, Rogue) and xevent `msg` field (MSG_AP_warm_reboot)
- [x] 2.3 Add timestamp-based deduplication via `_last_alarm_time` and `_last_xevent_time` globals
- [x] 2.4 Write mock tests for event parsing with sample XML fixtures

## 3. Prometheus Metrics

- [x] 3.1 Define counter metrics: `unleashed_ap_radio_off_total`, `unleashed_ap_radio_on_total`, `unleashed_ap_join_event_total`, `unleashed_ap_reboot_event_total`, `unleashed_rogue_detected_event_total`
- [x] 3.2 Implement `update_alarm_metrics()` and `update_xevent_metrics()` functions that classify events and increment counters
- [x] 3.3 Integrate event collection into the main poll loop
- [x] 3.4 Write mock tests verifying counter increments for each event type

## 4. Grafana Dashboard Panels

- [x] 4.1 Add "Radio Off/On Events (DFS)" panel to Network Overview dashboard
- [ ] 4.2 Add auth failure breakdown table to Network Health (client MAC, AP, SSID, failure count)
- [ ] 4.3 Add DFS radar log panel to Network Health (AP name, channel, timestamp)
- [ ] 4.4 Add roaming event count panel to Network Health (from_ap → to_ap pairs) — BLOCKED: roaming events not available in API
- [ ] 4.5 Add auth failure count column to Client Health per-client table

## 5. Validation

- [ ] 5.1 Verify event metrics appear in Prometheus after exporter restart with live AP
- [ ] 5.2 Verify Grafana event panels populate with real data
- [ ] 5.3 Trigger a known event (e.g., disconnect/reconnect a client) and confirm it shows in the dashboard within one poll interval
