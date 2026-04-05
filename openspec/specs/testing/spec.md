# testing Specification

## Purpose
TBD - created by archiving change ruckus-r720-monitoring-dashboard. Update Purpose after archive.
## Requirements
### Requirement: Mock-based tests for the Unleashed web API exporter
The system SHALL include unit/integration tests for the custom Python exporter using mock HTTP responses that simulate the Unleashed _cmdstat.jsp XML interface (login.jsp authentication, _csrfTokenVar.jsp CSRF token, _cmdstat.jsp XML responses). Tests SHALL run without network access to a real AP.

#### Scenario: Successful authentication and client data collection
- **WHEN** the mock API returns a valid session cookie, CSRF token, and an XML client list with multiple clients
- **THEN** the exporter produces Prometheus metrics for all clients with correct RSSI, SNR, noise floor, and labels

#### Scenario: Authentication failure handling
- **WHEN** the mock login.jsp does not set a session cookie
- **THEN** the exporter logs an error, exposes an error counter metric, and does not crash

#### Scenario: API error handling
- **WHEN** the mock _cmdstat.jsp returns empty content or connection timeout
- **THEN** the exporter logs an error, exposes an error counter metric, and retains previous metrics until next successful poll

#### Scenario: Client disconnection cleanup
- **WHEN** a client present in the first poll is absent in the second poll
- **THEN** the exporter removes that client's metrics from the /metrics output

#### Scenario: Session re-authentication
- **WHEN** _cmdstat.jsp redirects to login.jsp (session expired)
- **THEN** the exporter re-authenticates, re-fetches CSRF token, and retries the request

### Requirement: Mock-based tests for SNMP configuration
The system SHALL include tests that verify the snmp.yml configuration is well-formed, contains expected metric names with correct OID base (1.3.6.1.4.1.25053.1.15), and validates against a recorded SNMP walk from the live AP.

#### Scenario: Valid SNMP config structure
- **WHEN** snmp.yml is parsed
- **THEN** it contains the ruckus_r720 module with walk OIDs and metric definitions for CPU, memory, client counts, and traffic counters

#### Scenario: Recorded walk contains expected OIDs
- **WHEN** the test loads the recorded SNMP walk from the live R720
- **THEN** the walk contains sysUpTime, CPU utilization, and system stats OIDs

### Requirement: Mock-based tests for Prometheus alerting rules
The system SHALL include tests that verify Prometheus alerting rules fire correctly using promtool with mock time-series data.

#### Scenario: AP-down alert fires
- **WHEN** mock data shows an AP with no successful SNMP scrapes for 5 minutes
- **THEN** the AP-unreachable alert rule evaluates to firing

#### Scenario: Poor client signal alert fires
- **WHEN** mock data shows a client RSSI at -80 dBm for 5 minutes
- **THEN** the poor-client-signal alert rule evaluates to firing

#### Scenario: High CPU alert fires
- **WHEN** mock data shows CPU utilization at 95% for 5 minutes
- **THEN** the high-CPU alert rule evaluates to firing

### Requirement: End-to-end tests against live Ruckus AP
The system SHALL include end-to-end tests that run the full stack (Docker Compose) against the live Ruckus AP at https://10.91.1.109/ and verify real data flows from AP through to Grafana.

#### Scenario: SNMP exporter collects real metrics
- **WHEN** the stack is started with the live AP target (10.91.1.109)
- **THEN** Prometheus contains non-zero values for sysUpTime, CPU utilization, and client count within 2 scrape intervals

#### Scenario: Web API exporter collects real client data
- **WHEN** the stack is started with Unleashed credentials for 10.91.1.109
- **THEN** the unleashed-exporter /metrics endpoint returns per-client RSSI metrics without errors

#### Scenario: Grafana dashboards render with real data
- **WHEN** the stack has been running for at least 2 minutes against the live AP
- **THEN** the Grafana API (GET /api/search) returns all 4 provisioned dashboards

#### Scenario: Prometheus receives data from both exporters
- **WHEN** the stack is running against the live AP
- **THEN** a Prometheus API query (GET /api/v1/targets) shows both SNMP and unleashed-exporter targets as "up"

### Requirement: End-to-end tests are separately invocable
The system SHALL allow mock tests and end-to-end tests to be run independently. Mock tests SHALL be runnable via `make test-mock`. End-to-end tests SHALL be runnable via `make test-e2e` and SHALL require the live AP to be reachable.

#### Scenario: Running mock tests only
- **WHEN** an operator runs make test-mock
- **THEN** all mock tests execute without requiring network access to any AP

#### Scenario: Running end-to-end tests only
- **WHEN** an operator runs make test-e2e with the live AP reachable
- **THEN** the full stack starts, tests run against real data, and the stack is torn down

#### Scenario: End-to-end tests skip gracefully when AP unreachable
- **WHEN** an operator runs make test-e2e but the AP at 10.91.1.109 is unreachable
- **THEN** the tests are skipped with a clear message rather than failing with a timeout

