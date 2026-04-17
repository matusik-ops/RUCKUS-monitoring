## Context

The unleashed-exporter polls the Ruckus Unleashed `_cmdstat.jsp` API every 60 seconds for real-time metrics (clients, radios, rogues). The API also supports event/syslog queries that return discrete events: client joins/leaves, auth failures, DFS radar, roaming. Currently none of these events are captured — troubleshooting relies on manually SSH-ing into the AP or checking the web UI.

The exporter already has a working `UnleashedClient` class with authentication, CSRF handling, and XML parsing. The event log integration extends this with a new query type.

## Goals / Non-Goals

**Goals:**
- Retrieve event log entries from the Unleashed API on each poll cycle
- Parse and classify events into categories: connect, disconnect, auth-fail, DFS radar, roam
- Expose event data as Prometheus metrics (counters for rates, info gauges for recent events)
- Add Grafana panels to visualize event patterns over time

**Non-Goals:**
- Real-time event streaming (WebSocket/push) — polling every 60s is sufficient
- Long-term event storage outside Prometheus retention — Prometheus is the only store
- Alerting rules based on events — can be added later as a separate change
- Parsing every possible Unleashed event type — focus on the 5 most useful categories

## Decisions

### 1. Event log API query format

**Decision:** Use `<ajax-request action='getstat' comp='system'><syslog/></ajax-request>` to query the event log via `_cmdstat.jsp`.

**Rationale:** The Unleashed web UI uses this same endpoint to display the event log. The `comp='system'` component with `<syslog/>` returns recent syslog/event entries as XML. This is the same pattern used for `<client/>`, `<ap/>`, and `<rogue/>` queries.

**Risk:** The exact XML format needs to be verified against the live AP. A spike task should confirm the query works and document the response schema before full implementation.

**Alternative considered:** SNMP traps. Rejected because: requires trap receiver infrastructure, Unleashed has limited trap support, and the existing HTTP API approach is consistent with the rest of the exporter.

### 2. Event classification via message pattern matching

**Decision:** Parse the syslog message text using regex patterns to classify events into categories (connect, disconnect, auth-fail, dfs-radar, roam).

**Rationale:** Ruckus syslog messages follow consistent patterns (e.g., "STA[xx:xx:xx:xx:xx:xx] joined", "Auth failure for STA[...]", "Radar detected on channel X"). Pattern matching is simple, testable, and extensible.

**Alternative considered:** Structured event types from the API. The API may return event type codes — if so, use those instead. The spike task should determine this.

### 3. Prometheus metric design: counters + info gauge

**Decision:** Use counters for event rates and an info gauge for recent event details:

- `unleashed_event_total` — Counter, labels: `event_type`, `ap_name`, `site`. Incremented for each event.
- `unleashed_client_connect_total` — Counter, labels: `client_mac`, `ap_name`, `ssid`, `site`.
- `unleashed_client_disconnect_total` — Counter, labels: `client_mac`, `ap_name`, `ssid`, `site`.
- `unleashed_auth_fail_total` — Counter, labels: `client_mac`, `ap_name`, `ssid`, `site`.
- `unleashed_dfs_radar_total` — Counter, labels: `ap_name`, `channel`, `site`.
- `unleashed_roam_total` — Counter, labels: `client_mac`, `from_ap`, `to_ap`, `site`.

**Rationale:** Counters enable `rate()` and `increase()` in Grafana for event-rate graphs. Per-event-type counters with relevant labels allow targeted queries (e.g., "auth failures per client").

**Alternative considered:** Gauge with event timestamp. Rejected because gauges don't compose well for event counting; counters are the Prometheus convention for events.

### 4. Deduplication via timestamp tracking

**Decision:** Track the most recent event timestamp seen per poll. On each poll, only process events newer than the last seen timestamp.

**Rationale:** The syslog API may return overlapping events between polls (e.g., last 100 events). Without dedup, counters would be incremented multiple times for the same event.

### 5. Dashboard placement

**Decision:** Add an "Events" row to the Network Health dashboard with: event rate timeline, auth failure breakdown table, DFS radar log, and roaming event count. Add auth-fail count to Client Health per-client view.

**Rationale:** Events are a health/diagnostic concern — Network Health is the natural home. Per-client auth failure count belongs in Client Health.

**Alternative considered:** Dedicated Events dashboard. May be warranted later, but start by embedding in existing dashboards to avoid dashboard sprawl.

## Risks / Trade-offs

- **Unknown API format** → The syslog query format is not documented. Mitigation: first task is a spike to query the live AP and document the response. If the syslog endpoint doesn't exist, fall back to parsing the web UI's event page.
- **Event volume** → Busy networks may generate thousands of events per minute. Mitigation: only process events since last poll (dedup), and keep counter cardinality bounded by using top-level labels only.
- **Counter resets on exporter restart** → Prometheus handles counter resets natively via `rate()`/`increase()`. No special handling needed.
- **Message format changes across firmware** → Regex patterns may break on firmware updates. Mitigation: log unclassified events and expose `unleashed_event_unclassified_total` counter to detect pattern mismatches.
