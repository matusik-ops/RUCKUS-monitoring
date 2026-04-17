## ADDED Requirements

### Requirement: All dashboards include a site template variable
Every Grafana dashboard SHALL include a `$site` template variable that queries available `site` label values from Prometheus.

#### Scenario: Site variable populated
- **WHEN** a user opens any dashboard
- **THEN** the `$site` dropdown shows all sites currently reporting metrics, plus an "All" option

### Requirement: All dashboard queries filter by site label
Every PromQL query in every dashboard panel SHALL include a `site=~"$site"` filter so that panels respect the selected site.

#### Scenario: Filtering to a single site
- **WHEN** a user selects "sklad-01" in the `$site` dropdown
- **THEN** all panels show only data from sklad-01

#### Scenario: Viewing all sites
- **WHEN** a user selects "All" in the `$site` dropdown
- **THEN** panels show aggregated data from all sites, with per-site series distinguished by legend labels

### Requirement: Existing dashboard variables remain functional
The addition of `$site` SHALL NOT break existing template variables (`$ap_name`, `$ssid`, `$radio_band`, `$client`). These variables SHALL be chained to filter within the selected site.

#### Scenario: Chained variable filtering
- **WHEN** a user selects site "sklad-01" and then opens the `$ap_name` dropdown
- **THEN** only AP names from sklad-01 are listed
