## ADDED Requirements

### Requirement: Prometheus retains historical metric data
The system SHALL configure Prometheus with a data retention period sufficient for incident review, defaulting to 30 days.

#### Scenario: Default retention
- **WHEN** no custom retention is specified
- **THEN** Prometheus retains metric data for 30 days

#### Scenario: Custom retention
- **WHEN** an operator sets retention to 90 days in configuration
- **THEN** Prometheus retains metric data for 90 days and automatically expires data older than 90 days

### Requirement: Prometheus data is persisted across container restarts
The system SHALL store Prometheus TSDB data on a persistent Docker volume so that data survives container restarts and upgrades.

#### Scenario: Container restart
- **WHEN** the Prometheus container is stopped and restarted
- **THEN** all previously collected metric data is still available

#### Scenario: Container recreation
- **WHEN** the Prometheus container is removed and recreated via Docker Compose
- **THEN** metric data persists because it is stored on a named Docker volume

### Requirement: Grafana configuration is persisted
The system SHALL persist Grafana data (datasource config, user preferences) on a Docker volume.

#### Scenario: Grafana restart
- **WHEN** the Grafana container restarts
- **THEN** datasource configurations and user preferences are preserved

### Requirement: Retention period is configurable
The system SHALL allow the retention period to be configured via an environment variable or configuration file.

#### Scenario: Configuring retention via environment variable
- **WHEN** an operator sets the PROMETHEUS_RETENTION environment variable to "15d"
- **THEN** Prometheus uses a 15-day retention period
