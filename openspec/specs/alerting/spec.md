# alerting Specification

## Purpose
TBD - created by archiving change ruckus-r720-monitoring-dashboard. Update Purpose after archive.
## Requirements
### Requirement: Alert when AP is unreachable
The system SHALL raise an alert when an Unleashed AP fails to respond to SNMP polling for a configured duration.

#### Scenario: AP goes down
- **WHEN** an AP does not respond to SNMP polling for 5 minutes (default threshold)
- **THEN** Grafana fires an alert indicating the AP is unreachable

#### Scenario: AP recovers
- **WHEN** an AP that was previously unreachable begins responding again
- **THEN** the alert resolves automatically

### Requirement: Alert on high client count
The system SHALL raise an alert when the total client count (ruckusUnleashedSystemStatsAllNumSta) exceeds a configurable threshold.

#### Scenario: Client count exceeds threshold
- **WHEN** the total connected client count exceeds the configured maximum (default: 50)
- **THEN** Grafana fires a high-client-count alert

### Requirement: Alert on excessive Tx retries
The system SHALL raise an alert when the rate of aggregate Tx retries (ruckusUnleashedSystemStatsWLANTotalTxRetry) exceeds a configurable threshold, indicating RF quality issues.

#### Scenario: Tx retry rate too high
- **WHEN** the Tx retry rate exceeds the configured threshold over a 5-minute window
- **THEN** Grafana fires a tx-retry alert

### Requirement: Alert on high AP CPU usage
The system SHALL raise an alert when AP CPU utilization (ruckusUnleashedSystemStatsCPUUtil) exceeds a configurable threshold.

#### Scenario: CPU overloaded
- **WHEN** AP CPU utilization exceeds 90% for 5 minutes (default)
- **THEN** Grafana fires a high-cpu alert

### Requirement: Alert on poor client signal
The system SHALL raise an alert when any connected client's RSSI (unleashed_client_rssi_dbm from the web API exporter) falls below a configurable threshold.

#### Scenario: Client with weak signal
- **WHEN** a client's RSSI drops below -75 dBm (default) for 5 minutes
- **THEN** Grafana fires a poor-client-signal alert identifying the client MAC, AP, and SSID

### Requirement: Alert thresholds are configurable
The system SHALL allow all alert thresholds to be configured via Grafana alert rule configuration without modifying dashboard JSON directly.

#### Scenario: Adjusting a threshold
- **WHEN** an operator changes an alert threshold in the Grafana alert rule UI
- **THEN** the alert uses the updated threshold

### Requirement: Alert notification channel
The system SHALL support configuring at least one notification channel (e.g., email, webhook) for alert delivery.

#### Scenario: Alert fires with notification configured
- **WHEN** an alert condition is met and a notification channel is configured
- **THEN** the system sends a notification to the configured channel

#### Scenario: No notification channel configured
- **WHEN** an alert condition is met but no notification channel is configured
- **THEN** the alert is visible in the Grafana alerting UI but no external notification is sent

