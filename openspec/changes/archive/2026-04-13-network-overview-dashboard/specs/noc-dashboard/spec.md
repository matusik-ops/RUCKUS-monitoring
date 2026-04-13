## ADDED Requirements

### Requirement: Dashboard shows network health at a glance
The system SHALL provide a single Grafana dashboard ("Ruckus Network Overview") that displays overall network health without requiring any user interaction. All panels SHALL auto-refresh every 30 seconds.

#### Scenario: Everything healthy
- **WHEN** all APs are online, airtime is low, no clients have weak signal, and no auth failures are spiking
- **THEN** all status indicators are green and problem tables are empty

#### Scenario: AP is down
- **WHEN** the number of online APs drops below the expected count
- **THEN** the "APs Online" stat turns yellow or red depending on how many are missing

#### Scenario: Radio congested
- **WHEN** any AP's airtime-busy exceeds 40% of airtime-total on either band
- **THEN** that AP's airtime bar gauge turns red, immediately identifying the congested AP and band

#### Scenario: Client with poor signal
- **WHEN** any client has RSSI below -70 dBm
- **THEN** that client appears in the "Weak Signal" table with hostname, AP, SSID, band, and RSSI color-coded

### Requirement: Status bar shows big-number health indicators
The system SHALL display a top row of stat/gauge panels: APs Online, Total Clients, Master CPU, Master Memory, SNMP Target (UP/DOWN), Exporter (UP/DOWN). These SHALL be large enough to read from 3 meters on a wall-mounted display.

#### Scenario: Data source goes down
- **WHEN** the SNMP target or Unleashed exporter is unreachable
- **THEN** the corresponding status panel shows "DOWN" in red

### Requirement: Per-AP health section identifies problem APs
The system SHALL display horizontal bar gauges showing per-AP: total clients, airtime busy % for 2.4GHz, airtime busy % for 5GHz, and auth failures per radio. Color thresholds SHALL highlight APs with issues.

#### Scenario: Uneven client distribution
- **WHEN** one AP has significantly more clients than others
- **THEN** its bar stands out visually in the clients-per-AP gauge

#### Scenario: Auth failure spike on one AP
- **WHEN** one AP's radio has >200 auth failures
- **THEN** that entry turns red in the auth failures gauge

### Requirement: Problem client tables show who needs attention
The system SHALL display two tables: "Clients with Weak Signal (RSSI < -70 dBm)" and "Lowest Data Rates". Tables SHALL show client MAC, hostname, AP, SSID, band, and the metric value with color coding. If no clients have problems, tables SHALL be empty (no noise).

#### Scenario: No problem clients
- **WHEN** all clients have RSSI above -70 dBm and reasonable data rates
- **THEN** both tables are empty — clear indication of a healthy network

#### Scenario: Multiple weak clients
- **WHEN** 3 clients have RSSI below -70 dBm
- **THEN** all 3 appear in the weak signal table sorted by RSSI (worst first)

### Requirement: Trend section shows historical context
The system SHALL display time-series panels for: total client count over time, aggregate Tx retries/failures rate, and aggregate wireless throughput (Rx/Tx bps). These provide context for whether the current state is normal or degrading.

#### Scenario: Client count spike
- **WHEN** client count increases significantly over the last hour
- **THEN** the trend graph shows the increase, helping correlate with other issues

### Requirement: Distribution section shows load balance
The system SHALL display pie charts for: clients per SSID, clients per AP, and clients per radio band. These help identify load imbalance across the network.

#### Scenario: Most clients on one AP
- **WHEN** 60% of clients are on a single AP
- **THEN** the per-AP pie chart makes the imbalance immediately visible

### Requirement: Drill-down links to detail dashboards
Panels in the per-AP health section SHALL include links to the AP Detail and Radio Health dashboards, filtered by the selected AP.

#### Scenario: Investigating a congested AP
- **WHEN** an operator sees AP06 has high airtime in the overview
- **THEN** they can click to navigate directly to the Radio Health dashboard filtered to AP06

### Requirement: Dashboard is set as Grafana home
The system SHALL configure Grafana provisioning so the Network Overview dashboard loads as the default home page when opening Grafana.

#### Scenario: Opening Grafana
- **WHEN** a user navigates to http://localhost:3000
- **THEN** the Network Overview dashboard is displayed by default
