## ADDED Requirements

### Requirement: System-level wireless health dashboard shows Tx quality metrics
The system SHALL display aggregate Tx retries (ruckusUnleashedSystemStatsWLANTotalTxRetry), Tx failures (TotalTxFail), Tx dropped packets (TotalTxDroppedPkt), and Rx error frames (TotalRxErrFrm) as rate-of-change time-series to indicate overall wireless transmission quality. Note: per-radio breakdowns are NOT available via SNMP on firmware 200.15 — these are system-level aggregates.

#### Scenario: High retry rate
- **WHEN** the Tx retry rate increases significantly
- **THEN** the dashboard shows the trend, indicating potential RF interference or distance issues

#### Scenario: Normal Tx quality
- **WHEN** Tx retry and failure rates are low
- **THEN** the dashboard shows stable, low-rate graphs

### Requirement: AP resource utilization panel shows CPU and memory
The system SHALL display AP CPU utilization (ruckusUnleashedSystemStatsCPUUtil) and memory utilization (ruckusUnleashedSystemStatsMemoryUtil) as time-series graphs and current gauges.

#### Scenario: High CPU usage
- **WHEN** AP CPU utilization exceeds 80%
- **THEN** the dashboard panel visually indicates high CPU load (color threshold)

#### Scenario: Normal resource usage
- **WHEN** CPU and memory are within normal ranges
- **THEN** the dashboard shows healthy/green indicators

### Requirement: Per-client signal distribution provides radio health proxy
Since per-radio metrics (channel utilization, airtime, auth/assoc failure rates) are NOT available via SNMP on firmware 200.15, the system SHALL use per-client RSSI distribution from the web API exporter as a proxy for radio health — showing signal quality distribution across clients per AP and per radio band.

#### Scenario: Most clients have good signal
- **WHEN** the majority of clients have RSSI above -60 dBm
- **THEN** the dashboard shows a healthy signal distribution

#### Scenario: Clients with poor signal on specific AP
- **WHEN** multiple clients on one AP have RSSI below -75 dBm
- **THEN** the dashboard highlights that AP as having signal quality issues

### Requirement: Aggregate wireless traffic is displayed
The system SHALL display aggregate WLAN Rx/Tx bytes and packets as rate-of-change time-series from SNMP system stats.

#### Scenario: Traffic overview
- **WHEN** the AP is passing wireless traffic
- **THEN** the dashboard shows aggregate Rx/Tx throughput trends over time
