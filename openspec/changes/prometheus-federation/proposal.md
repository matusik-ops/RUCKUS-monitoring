## Why

The monitoring stack currently runs as a single deployment scraping one Ruckus Unleashed master AP. We need to monitor multiple warehouse sites (each with its own Ruckus Unleashed cluster) from a single Grafana instance. Prometheus Federation is the standard approach — each site runs a local Prometheus, and a central Master Prometheus federates metrics from all of them.

## What Changes

- Each site deployment gets `external_labels` (e.g., `site: "sklad-01"`) added to its Prometheus config so metrics are tagged by origin
- A new **Master Prometheus** instance is introduced on a central server, configured to scrape `/federate` endpoints from all site-level Prometheus members
- A single **Grafana** instance on the central server connects to Master Prometheus as its datasource
- All dashboards gain a `$site` template variable so users can filter or compare across sites
- The existing per-site `docker-compose.yml` is refactored into a reusable site-level stack (exporter + SNMP exporter + blackbox exporter + member Prometheus)
- A new central-server `docker-compose.yml` is created (Master Prometheus + Grafana)

## Capabilities

### New Capabilities
- `federation`: Prometheus federation config — Master Prometheus scraping `/federate` from member instances, metric relabeling, and retention policies
- `multi-site-deployment`: Per-site and central-server docker-compose definitions, external_labels configuration, and deployment instructions
- `site-filtering`: Dashboard `$site` variable across all dashboards, enabling per-site and cross-site views

### Modified Capabilities
- `dashboard-views`: All dashboards need `$site` variable added to template variables and queries filtered by `site` label

## Impact

- **Config files**: `prometheus/prometheus.yml` gains `external_labels`; new central `prometheus.yml` with federation scrape config
- **Docker Compose**: Existing `docker-compose.yml` becomes the per-site template; new `docker-compose.central.yml` for the central server
- **Dashboards**: All 4 Grafana dashboards (`network-overview`, `network-health`, `clients-overview`, `client-health`) need `$site` variable and query updates
- **Network**: Site-level Prometheus `:9090` must be reachable from central server (VPN/LAN)
- **Resources**: Central server needs ~200-400 MB RAM (Master Prometheus + Grafana), each site ~170 MB (member Prometheus + exporters)
