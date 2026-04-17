## ADDED Requirements

### Requirement: Master Prometheus federates metrics from site members
The Master Prometheus SHALL scrape the `/federate` endpoint of each site-level Prometheus member, collecting all `unleashed_*`, `snmp_*`, `probe_*`, and `up` metrics.

#### Scenario: Normal federation scrape
- **WHEN** Master Prometheus performs a federation scrape against a member
- **THEN** all matching metrics are ingested with the member's `site` label preserved via `honor_labels: true`

#### Scenario: Member unreachable
- **WHEN** a site-level Prometheus is unreachable during a federation scrape
- **THEN** Master Prometheus logs a scrape error and the `up` metric for that federation target reads `0`; other sites are unaffected

### Requirement: Federation scrape interval matches member scrape interval
The Master Prometheus SHALL scrape federation targets at the same interval as site-level Prometheus scrapes exporters (30s), to avoid aliasing or missed samples.

#### Scenario: Scrape timing alignment
- **WHEN** Master Prometheus federates a member
- **THEN** the federation scrape interval is 30s, matching the member's `scrape_interval`

### Requirement: Site-level Prometheus exposes external_labels
Each site-level Prometheus SHALL include `external_labels` with a unique `site` key (e.g., `site: "sklad-01"`) in its `prometheus.yml` global config.

#### Scenario: External labels on federated metrics
- **WHEN** metrics are federated from a site
- **THEN** every metric carries the `site` label identifying its origin site

### Requirement: Federation match filter covers all monitoring metrics
The federation `match[]` parameters SHALL include patterns for all exported metric families: `{__name__=~"unleashed_.*"}`, `{__name__=~"snmp_.*"}`, `{__name__=~"probe_.*"}`, and `{__name__="up"}`.

#### Scenario: All metric families federated
- **WHEN** a site exports unleashed, SNMP, blackbox, and up metrics
- **THEN** all of them appear in the Master Prometheus with the correct `site` label
