## 1. Per-Site Prometheus Configuration

- [x] 1.1 ~Add `external_labels` to site prometheus~ SKIPPED — existing stack stays untouched; site label added via federation-targets.yml labels
- [x] 1.2 ~Create `.env.example`~ SKIPPED — existing stack unchanged
- [x] 1.3 ~Update `docker-compose.yml`~ SKIPPED — existing stack unchanged
- [x] 1.4 ~Remove Grafana from per-site compose~ SKIPPED — existing stack keeps its own Grafana on :3000

## 2. Central Server Stack

- [x] 2.1 Create `prometheus/prometheus.central.yml` with federation scrape job: scrape `/federate` from member Prometheus targets with `match[]` for `unleashed_*`, `snmp_*`, `probe_*`, `up`; set `honor_labels: true` and 30s scrape interval
- [x] 2.2 Create `docker-compose.central.yml` with Master Prometheus (:9190) and Grafana (:3100) services, mounting central prometheus config and existing dashboard provisioning
- [x] 2.3 Create `prometheus/federation-targets.yml` with initial site targets (placeholder IPs), referenced by `file_sd_configs` in the central prometheus config for easy site addition

## 3. Dashboard Site Variable

- [x] 3.1 Add `$site` template variable to `network-overview.json` — query: `label_values(unleashed_ap_num_sta, site)`, include "All" option, place as first variable
- [x] 3.2 Add `$site` template variable to `network-health.json` with same config
- [x] 3.3 Add `$site` template variable to `clients-overview.json` with same config
- [x] 3.4 Add `$site` template variable to `client-health.json` with same config

## 4. Dashboard Query Updates

- [x] 4.1 Update all PromQL queries in `network-overview.json` to include `site=~"$site"` filter (38 exprs)
- [x] 4.2 Update all PromQL queries in `network-health.json` to include `site=~"$site"` filter (102 exprs)
- [x] 4.3 Update all PromQL queries in `clients-overview.json` to include `site=~"$site"` filter (27 exprs)
- [x] 4.4 Update all PromQL queries in `client-health.json` to include `site=~"$site"` filter (15 exprs)
- [x] 4.5 Chain existing variables (`$ap_name`, `$ssid`, `$radio_band`) to filter within selected `$site`

## 5. Validation

- [x] 5.1 Verify central stack starts and Master Prometheus federates from existing Prometheus on :9090 — confirmed: 47 clients federated with site="sklad-01"
- [ ] 5.2 Verify Grafana on :3100 `$site` dropdown populates correctly and all panels filter by site
- [ ] 5.3 Verify selecting "All" shows data from all federated sites
- [ ] 5.4 Verify existing variables (`$ap_name`, `$ssid`, `$radio_band`) chain correctly within selected site
