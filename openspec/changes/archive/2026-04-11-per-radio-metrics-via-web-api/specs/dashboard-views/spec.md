## MODIFIED Requirements

### Requirement: Fleet overview includes per-radio airtime indicators
The fleet overview dashboard SHALL show airtime-busy per radio for each AP, color-coded by utilization level.

#### Scenario: Viewing fleet with airtime
- **WHEN** a user views the fleet overview
- **THEN** each AP row shows 2.4GHz and 5GHz airtime-busy values with color thresholds

### Requirement: Radio health dashboard shows real per-radio data
The radio health dashboard SHALL replace system-level aggregate panels with real per-radio panels: airtime utilization, client count, avg RSSI, Tx retries, auth/assoc failures, traffic — all per AP, per radio band.

#### Scenario: Drilling into radio health
- **WHEN** a user views the radio health dashboard for a specific AP
- **THEN** the dashboard shows side-by-side 2.4GHz and 5GHz panels for all radio metrics
