# dashboard-views Specification

## Purpose
TBD - created by archiving change ruckus-r720-monitoring-dashboard. Update Purpose after archive.
## Requirements
### Requirement: Fleet overview dashboard
The system SHALL provide a Grafana dashboard showing a summary of all monitored Unleashed APs with key health indicators at a glance: AP up/down status, total client count, CPU utilization, memory utilization, and aggregate Tx error rate.

#### Scenario: All APs healthy
- **WHEN** all monitored APs are responding and within normal thresholds
- **THEN** the overview dashboard shows all APs in a healthy/green state with summary metrics (total APs, total clients, overall traffic)

#### Scenario: One AP is down
- **WHEN** one AP is not responding to SNMP polling
- **THEN** the overview dashboard highlights that AP in a warning/red state

### Requirement: Per-AP detail dashboard
The system SHALL provide a drill-down view for each AP showing: total client count, CPU and memory utilization, uptime, aggregate WLAN traffic rates, and Ethernet interface status. Template variable for AP selection with drill-down links from the fleet overview.

#### Scenario: Navigating to AP detail
- **WHEN** a user clicks on an AP in the fleet overview
- **THEN** the system navigates to the per-AP detail dashboard filtered to that specific AP

#### Scenario: Viewing AP metrics
- **WHEN** a user views the per-AP detail dashboard
- **THEN** the dashboard displays time-series graphs for client count, aggregate traffic, CPU, memory, uptime, and Ethernet interface status

### Requirement: Wireless health dashboard
The system SHALL provide a wireless health view showing: aggregate Tx retries/failures/drops rates, Rx error rates, CPU/memory utilization, and aggregate WLAN throughput. Since per-radio SNMP metrics are not available on firmware 200.15, this dashboard shows system-level aggregates.

#### Scenario: Investigating wireless issues
- **WHEN** a user navigates to the wireless health view
- **THEN** the dashboard displays time-series graphs for Tx retry rate, Tx failure rate, Rx errors, CPU, and memory

### Requirement: Client health dashboard
The system SHALL provide a client health drill-down view showing: a sortable table of all connected clients with their RSSI (dBm), SNR, noise floor, Tx data rate, Rx/Tx bytes, association time, channel, SSID, radio band, hostname, and AP name. Time-series panels SHALL show per-client RSSI, SNR, and data rate history. A pie chart SHALL show client distribution per SSID.

#### Scenario: Viewing all clients on an AP
- **WHEN** a user navigates to the client health view filtered by AP
- **THEN** the dashboard displays a sortable table of all connected clients on that AP with signal quality, data rate, traffic, and association time

#### Scenario: Investigating a specific client
- **WHEN** a user selects a specific client MAC from the client filter variable
- **THEN** all panels filter to show only that client's RSSI, SNR, data rate, and traffic history over time

#### Scenario: Identifying poor-signal clients
- **WHEN** viewing the client table
- **THEN** clients with RSSI below -75 dBm are highlighted in amber/red

### Requirement: Per-metric historical view
The system SHALL allow users to drill down into individual metrics with adjustable time ranges for historical analysis.

#### Scenario: Reviewing historical traffic
- **WHEN** a user selects a traffic metric and sets the time range to the last 7 days
- **THEN** the dashboard displays a time-series graph of that metric over the 7-day period

#### Scenario: Zooming into an incident window
- **WHEN** a user selects a specific time range on a graph (drag-to-zoom)
- **THEN** all panels on the dashboard update to reflect the selected time range

### Requirement: Dashboards are provisioned from version-controlled files
The system SHALL load Grafana dashboards from provisioned JSON files (unwrapped format, not nested under a "dashboard" key) stored in the project repository.

#### Scenario: Fresh deployment
- **WHEN** the Grafana container starts for the first time
- **THEN** all dashboards are automatically loaded from the provisioned JSON files without manual import

#### Scenario: Dashboard update
- **WHEN** a provisioned dashboard JSON file is updated and the container is restarted
- **THEN** the updated dashboard is reflected in Grafana

### Requirement: Dashboard supports variable-based filtering
The system SHALL use Grafana template variables to allow filtering by AP name/IP, SSID, and client MAC across dashboard panels.

#### Scenario: Filtering by AP
- **WHEN** a user selects a specific AP from the variable dropdown
- **THEN** all panels on the dashboard update to show data for only that AP

