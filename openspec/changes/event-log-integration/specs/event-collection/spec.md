## ADDED Requirements

### Requirement: Exporter retrieves event log entries from Unleashed API
The system SHALL query the Unleashed `_cmdstat.jsp` API for syslog/event log entries on each poll cycle, using the same authentication and CSRF handling as existing queries.

#### Scenario: Successful event log retrieval
- **WHEN** the exporter's poll interval elapses
- **THEN** the exporter posts an event log XML request to `_cmdstat.jsp`, parses the XML response, and processes each event entry

#### Scenario: Event log API unavailable
- **WHEN** the event log query returns an error or empty response
- **THEN** the exporter logs a warning and increments the poll error counter; other metrics collection continues unaffected

### Requirement: Events are classified into categories
The system SHALL classify each event log entry into one of the following categories based on message content: `connect`, `disconnect`, `auth-fail`, `dfs-radar`, `roam`, or `unclassified`.

#### Scenario: Client connect event
- **WHEN** the event log contains a message indicating a client joined (e.g., "STA[aa:bb:cc:dd:ee:ff] joined BSSID[...] on AP[AP01]")
- **THEN** the event is classified as `connect` with the client MAC, AP name, and SSID extracted

#### Scenario: Authentication failure event
- **WHEN** the event log contains a message indicating an auth failure
- **THEN** the event is classified as `auth-fail` with the client MAC and AP name extracted

#### Scenario: DFS radar event
- **WHEN** the event log contains a message indicating radar detection on a channel
- **THEN** the event is classified as `dfs-radar` with the AP name and channel extracted

#### Scenario: Roaming event
- **WHEN** the event log contains a message indicating a client roamed between APs
- **THEN** the event is classified as `roam` with the client MAC, source AP, and destination AP extracted

#### Scenario: Unrecognized event
- **WHEN** the event log contains a message that doesn't match any known pattern
- **THEN** the event is classified as `unclassified` and counted for monitoring pattern coverage

### Requirement: Event counters are exposed as Prometheus metrics
The system SHALL expose the following counter metrics, incremented for each new event since the last poll:

- `unleashed_event_total` labeled by `event_type`, `ap_name`
- `unleashed_client_connect_total` labeled by `client_mac`, `ap_name`, `ssid`
- `unleashed_client_disconnect_total` labeled by `client_mac`, `ap_name`, `ssid`
- `unleashed_auth_fail_total` labeled by `client_mac`, `ap_name`, `ssid`
- `unleashed_dfs_radar_total` labeled by `ap_name`, `channel`
- `unleashed_roam_total` labeled by `client_mac`, `from_ap`, `to_ap`

#### Scenario: Multiple events in one poll
- **WHEN** the event log contains 3 connect events and 1 auth failure since the last poll
- **THEN** the connect counter is incremented by 3 and the auth-fail counter by 1

#### Scenario: No new events
- **WHEN** the event log contains no events newer than the last poll timestamp
- **THEN** no counters are incremented

### Requirement: Events are deduplicated across polls
The system SHALL track the timestamp of the most recently processed event and only process events newer than that timestamp on subsequent polls.

#### Scenario: Overlapping event windows
- **WHEN** two consecutive polls return overlapping event entries
- **THEN** only events not previously processed are counted
