# snmp-collection Specification

## Purpose
TBD - created by archiving change ruckus-r720-monitoring-dashboard. Update Purpose after archive.
## Requirements
### Requirement: SNMP Exporter collects R720 metrics via RUCKUS-UNLEASHED-SYSTEM-MIB
The system SHALL use Prometheus SNMP Exporter to poll Ruckus Unleashed APs (firmware 200.15+) via SNMP v2c and expose metrics in Prometheus format. The SNMP Exporter configuration SHALL target: RUCKUS-UNLEASHED-SYSTEM-MIB (1.3.6.1.4.1.25053.1.15.1), RUCKUS-UNLEASHED-WLAN-MIB (1.3.6.1.4.1.25053.1.15.2), SNMPv2-MIB, and IF-MIB. Note: RUCKUS-RADIO-MIB OIDs (1.3.6.1.4.1.25053.1.1.12) are NOT available on firmware 200.15 — per-radio stats do not exist in this SNMP tree.

#### Scenario: Successful SNMP scrape
- **WHEN** Prometheus scrape interval elapses
- **THEN** SNMP Exporter polls each configured Unleashed target and returns metrics to Prometheus

#### Scenario: AP unreachable
- **WHEN** an AP does not respond to SNMP polling within the timeout
- **THEN** SNMP Exporter returns snmp_scrape_walk_errors incremented and Prometheus records the failed scrape

### Requirement: System-level client count metrics are collected
The system SHALL collect aggregate client counts from RUCKUS-UNLEASHED-SYSTEM-MIB: ruckusUnleashedSystemStatsNumSta (1.3.6.1.4.1.25053.1.15.1.1.1.15.2) for authorized clients and ruckusUnleashedSystemStatsAllNumSta (.15.30) for all clients. Per-radio client counts are NOT available via SNMP on this firmware.

#### Scenario: Clients connected
- **WHEN** the Unleashed network has active clients
- **THEN** metrics include aggregate authorized and total client count values

### Requirement: Aggregate wireless traffic metrics are collected
The system SHALL collect aggregate WLAN traffic counters from RUCKUS-UNLEASHED-SYSTEM-MIB: WLANTotalRxPkts (.15.5), WLANTotalRxBytes (.15.6), WLANTotalTxPkts (.15.8), WLANTotalTxBytes (.15.9), WLANTotalTxFail (.15.11), WLANTotalTxRetry (.15.12), WLANTotalAssocFail (.15.16), WLANTotalRxErrFrm (.15.17), WLANTotalTxDroppedPkt (.15.19), WLANTotalTxErrFrm (.15.20), WLANTotalTxDroppedFrm (.15.21).

#### Scenario: Normal traffic flow
- **WHEN** the AP is passing wireless traffic
- **THEN** metrics include aggregate Rx/Tx byte, packet, retry, failure, and error counters

### Requirement: AP system health metrics are collected
The system SHALL collect from RUCKUS-UNLEASHED-SYSTEM-MIB: ruckusUnleashedSystemStatsCPUUtil (.15.13) as CPU utilization percentage, ruckusUnleashedSystemStatsMemoryUtil (.15.14) as memory utilization percentage, and ruckusUnleashedSystemStatsNumAP (.15.1) for the number of APs.

#### Scenario: AP system health
- **WHEN** the AP is polled
- **THEN** metrics include CPU utilization %, memory utilization %, and AP count

### Requirement: AP identity info is collected
The system SHALL collect from RUCKUS-UNLEASHED-SYSTEM-MIB: system name (.1.1.1), IP address (.1.1.2), uptime (.1.1.8), model (.1.1.9), serial number (.1.1.15), and firmware version (.1.1.18). From SNMPv2-MIB: sysUpTime, sysDescr, sysName.

#### Scenario: AP identity available
- **WHEN** the AP is polled
- **THEN** metrics include system name, model, serial number, and firmware version

### Requirement: Per-AP status is collected via WLAN MIB
The system SHALL collect from RUCKUS-UNLEASHED-WLAN-MIB AP table (1.3.6.1.4.1.25053.1.15.2.1.1.2.1.1): AP status (.3), model (.4), and uptime (.6), indexed by AP MAC address.

#### Scenario: Multiple APs in the network
- **WHEN** the Unleashed network has multiple member APs
- **THEN** metrics include per-AP status (connected/disconnected), model, and uptime

### Requirement: Ethernet interface metrics are collected
The system SHALL collect standard IF-MIB counters: ifInOctets, ifOutOctets, ifInErrors, ifOutErrors, ifOperStatus for Ethernet interfaces.

#### Scenario: Ethernet traffic
- **WHEN** the AP Ethernet port is active
- **THEN** metrics include interface byte counters and operational status

### Requirement: Target APs are configurable
The system SHALL allow AP targets to be configured via a YAML file (file_sd_configs) without modifying application code.

#### Scenario: Adding a new AP to monitoring
- **WHEN** an operator adds an AP IP address to the target configuration file
- **THEN** Prometheus begins scraping the new AP on the next reload/restart

### Requirement: Scrape interval is configurable
The system SHALL allow the SNMP scrape interval to be configured, with a default of 60 seconds.

#### Scenario: Default scrape interval
- **WHEN** no custom scrape interval is specified
- **THEN** Prometheus scrapes SNMP targets every 60 seconds

### Requirement: Known SNMP limitations are documented
The system SHALL document that on firmware 200.15, RUCKUS-RADIO-MIB per-radio metrics (channel utilization, airtime, per-radio client counts, auth/assoc counters) are NOT available via SNMP. Per-client metrics require the Unleashed _cmdstat.jsp web API. Noise floor is available per-client via the web API but not via SNMP. Temperature is not available anywhere.

#### Scenario: Operator reviews documentation
- **WHEN** an operator reads the project documentation
- **THEN** the documentation clearly states which metrics are and are not available via SNMP vs the web API

