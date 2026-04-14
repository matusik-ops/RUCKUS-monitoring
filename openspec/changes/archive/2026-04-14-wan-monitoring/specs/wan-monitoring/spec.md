## ADDED Requirements

### Requirement: blackbox_exporter container for active probing
The system SHALL include a `blackbox_exporter` container in Docker Compose configured with ICMP and DNS probe modules.

#### Scenario: Container starts
- **WHEN** `docker compose up` is run
- **THEN** blackbox_exporter starts on port 9115 and responds to probe requests

### Requirement: ICMP probes to gateway and internet targets
The system SHALL configure Prometheus to probe via ICMP ping every 15 seconds: gateway (configurable, default 10.91.1.254), 8.8.8.8, 1.1.1.1.

#### Scenario: Internet is up
- **WHEN** all ICMP probes succeed
- **THEN** `probe_success=1` and `probe_duration_seconds` shows RTT for each target

#### Scenario: Internet is down but gateway is up
- **WHEN** gateway probe succeeds but 8.8.8.8 and 1.1.1.1 fail
- **THEN** dashboard shows gateway UP, internet DOWN — ISP problem

#### Scenario: Everything down
- **WHEN** all probes fail
- **THEN** dashboard shows all DOWN — local network or monitoring host issue

### Requirement: DNS resolution probe
The system SHALL configure a DNS probe that resolves `google.com` every 30 seconds.

#### Scenario: DNS working
- **WHEN** DNS resolution succeeds
- **THEN** `probe_success=1` and `probe_dns_lookup_time_seconds` shows resolution time

### Requirement: WAN panels in Network Health dashboard
The system SHALL replace the WAN placeholder text panel in SSIDs & Network Events with real panels: Internet UP/DOWN stat, Gateway latency time-series, Internet latency time-series, DNS response time stat.

#### Scenario: Operator checks WAN health
- **WHEN** viewing Network Health → SSIDs & Network Events
- **THEN** WAN panels show current status, latency, and DNS health

### Requirement: WAN indicator in Network Overview
The system SHALL add an "Internet" UP/DOWN stat panel to the Network Overview status bar.

#### Scenario: Internet is up
- **WHEN** both 8.8.8.8 and 1.1.1.1 respond to ping
- **THEN** Network Overview shows "Internet: UP" in green

#### Scenario: Internet is down
- **WHEN** neither 8.8.8.8 nor 1.1.1.1 responds
- **THEN** Network Overview shows "Internet: DOWN" in red
