## ADDED Requirements

### Requirement: Per-site deployment uses environment variables for configuration
Each site deployment SHALL read site-specific values (site name, AP IP, SNMP targets, credentials) from a `.env` file, keeping `docker-compose.yml` generic across sites.

#### Scenario: Deploying a new site
- **WHEN** an operator clones the repo and creates a `.env` file with site-specific values
- **THEN** `docker compose up` starts the full site-level stack (exporters + member Prometheus) configured for that site

#### Scenario: Missing .env file
- **WHEN** `docker compose up` is run without a `.env` file
- **THEN** the stack either fails with a clear error or uses documented defaults

### Requirement: Central server runs Master Prometheus and Grafana
A `docker-compose.central.yml` SHALL define the central server stack: Master Prometheus (federation) and Grafana, with Grafana pre-configured to use Master Prometheus as its datasource.

#### Scenario: Starting the central server
- **WHEN** an operator runs `docker compose -f docker-compose.central.yml up`
- **THEN** Master Prometheus starts federating from configured member targets, and Grafana is accessible on `:3000` with dashboards loaded

### Requirement: Site-level stack excludes Grafana
The per-site `docker-compose.yml` SHALL NOT include a Grafana service, since Grafana runs only on the central server.

#### Scenario: Site stack services
- **WHEN** the site-level stack is started
- **THEN** it runs unleashed-exporter, snmp-exporter, blackbox-exporter, and member Prometheus — no Grafana

### Requirement: Adding a new site requires only config changes
Adding a new site to the federation SHALL require only: (1) deploying the site-level stack with a new `.env`, and (2) adding the site's Prometheus address to the central `prometheus.central.yml` federation targets.

#### Scenario: Onboarding a new warehouse site
- **WHEN** a new site is deployed and its Prometheus address is added to the central federation config
- **THEN** the new site's metrics appear in Grafana under its `site` label within one scrape interval
