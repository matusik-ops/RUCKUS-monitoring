## ADDED Requirements

### Requirement: Single dashboard with 5 collapsible sections
The system SHALL provide a Grafana dashboard ("Ruckus Network Health") organized as 5 row sections that can be expanded/collapsed independently: Overview, RF Environment, Airtime History, Channel History, Rogue Devices.

#### Scenario: Collapsing a section
- **WHEN** an operator clicks a section row title
- **THEN** that section collapses, hiding its panels and skipping their queries

#### Scenario: Default state
- **WHEN** the dashboard loads
- **THEN** the Overview section is expanded; the other 4 sections are collapsed (operator expands as needed)

### Requirement: Overview section shows composite health score
The Overview section SHALL display a composite "Network Health %" score computed as:
- Start at 100
- Subtract 10 per AP that is down (SNMP not responding)
- Subtract 5 per client with RSSI < -75 dBm
- Subtract 10 per radio with airtime busy ratio > 50%
- Subtract 15 per AP with auth fail rate > 50%
- Subtract 20 per malicious rogue AP
- Clamp to a minimum of 0

The score SHALL be color-coded: green ≥80%, yellow ≥50%, red <50%.

#### Scenario: Healthy network
- **WHEN** all APs are up, no clients have weak signal, no congested radios, no auth issues, no malicious rogues
- **THEN** health score shows 100% in green

#### Scenario: Multiple issues
- **WHEN** there are 2 weak clients, 1 congested radio, and 1 malicious rogue
- **THEN** health score shows 60% in yellow (100 - 10 - 10 - 20 = 60)

### Requirement: Overview section shows fleet summary stats
The Overview section SHALL display:
- Total APs / Online APs
- Total clients (current and peak in time range)
- Average client RSSI across all clients
- Maximum client count over the selected time range
- Active alerts count (sum of weak clients + congested radios + high-auth-fail APs + malicious rogues)
- Peak hour identification (when client count was highest in the time range)

#### Scenario: Operator views overview
- **WHEN** opening the Network Health dashboard
- **THEN** all KPIs are visible without scrolling

### Requirement: RF Environment section shows per-AP RF table
The RF Environment section SHALL display a sortable table with one row per (AP, radio_band) pair, columns:
- AP, Band, Channel, Channel Width
- Connected Clients, Avg RSSI
- Airtime Busy %, Rx %, Tx %
- Tx Retries (rate over 5m), Tx Failures (rate over 5m), FCS Errors (rate over 5m)
- Auth Fail % (over 5m)

Numeric columns SHALL have color thresholds matching the alerting rules.

#### Scenario: Identifying worst radio
- **WHEN** an operator sorts by Auth Fail %
- **THEN** the worst-performing radios appear at the top, color-coded red

### Requirement: RF Environment section shows channel utilization
The RF Environment section SHALL display:
- Bar chart: 2.4GHz channel congestion (rogues per channel + our radios per channel)
- Bar chart: 5GHz channel congestion (rogues per channel + our radios per channel)

These help the operator identify which channels are oversubscribed.

#### Scenario: Channel 1 is crowded
- **WHEN** channel 1 has 5 detected rogues and 2 of our APs are on it
- **THEN** the 2.4GHz bar chart shows channel 1 with the highest combined value

### Requirement: Airtime History section shows time-series
The Airtime History section SHALL display per-AP, per-band time-series of airtime busy %, Rx %, and Tx % using rate windows of 5 minutes. Template variables `$ap_name` and `$radio_band` SHALL allow filtering.

#### Scenario: Investigating a busy period
- **WHEN** an operator selects time range "last 24 hours" and filters by `$radio_band=2.4g`
- **THEN** time-series shows when each AP's 2.4GHz airtime spiked

### Requirement: Channel History section shows channel changes
The Channel History section SHALL display per-AP, per-band time-series of channel number and Tx power, allowing operators to see when channels changed (DFS events, manual changes, ChannelFly).

#### Scenario: Channel jumped on AP05
- **WHEN** AP05 5GHz changed from channel 56 to channel 149 at 14:23
- **THEN** the time-series shows the step change at that timestamp

### Requirement: Rogue Devices section shows comprehensive rogue overview
The Rogue Devices section SHALL display:
- KPIs: Total rogues, Malicious rogues (highlighted red), Strongest rogue signal (worst case)
- Bar chart: Rogues per channel (split by 2.4GHz / 5GHz)
- Sortable table of all rogues with: SSID, MAC, Channel, Band, Type, Detector AP, RSSI (color-coded)

#### Scenario: Multiple malicious rogues detected
- **WHEN** 2 malicious rogues are detected
- **THEN** the Malicious KPI shows 2 in red, and the rogue table sorts them to the top with malicious type highlighted

### Requirement: Dashboard auto-refreshes and supports time range
The dashboard SHALL auto-refresh every 30 seconds and provide a time range picker defaulting to last 6 hours (suitable for History sections).

#### Scenario: Looking at historical data
- **WHEN** an operator changes time range to "last 7 days"
- **THEN** all time-series panels in History sections update to show 7 days of data
