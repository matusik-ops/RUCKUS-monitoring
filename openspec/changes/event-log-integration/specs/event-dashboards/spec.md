## ADDED Requirements

### Requirement: Network Health dashboard includes event rate timeline
The Network Health dashboard SHALL include a time-series panel showing event rates over time, with separate series for connect, disconnect, auth-fail, dfs-radar, and roam event types. The panel SHALL include `site=~"$site"` filter.

#### Scenario: Viewing event rates
- **WHEN** a user views the Network Health dashboard
- **THEN** the Events row displays a graph of `rate(unleashed_event_total[5m])` broken down by event_type

### Requirement: Network Health dashboard includes auth failure breakdown
The Network Health dashboard SHALL include a table panel showing auth failures grouped by client MAC and AP, ordered by failure count descending. This enables identification of specific devices causing repeated auth failures.

#### Scenario: Identifying problem devices
- **WHEN** a user views the auth failure breakdown table
- **THEN** the table shows client MAC, AP name, SSID, and failure count, sorted by highest failure count

### Requirement: Network Health dashboard includes DFS radar log
The Network Health dashboard SHALL include a table or stat panel showing recent DFS radar detections with AP name, channel, and time.

#### Scenario: DFS event occurred
- **WHEN** a DFS radar event was detected in the last 24 hours
- **THEN** the panel shows the AP name, affected channel, and timestamp

### Requirement: Network Health dashboard includes roaming event count
The Network Health dashboard SHALL include a panel showing client roaming events per AP pair, enabling visibility into roaming hotspots.

#### Scenario: Active roaming
- **WHEN** clients are roaming between APs
- **THEN** the panel shows roam counts per from_ap/to_ap pair
