## Context

The monitoring stack currently runs as a single Docker Compose deployment on one machine, scraping one Ruckus Unleashed master AP (10.91.1.109). The company operates multiple warehouse sites ("sklad"), each with its own Ruckus Unleashed cluster. We need a single Grafana dashboard that can view any site or compare across sites.

Current stack per site: unleashed-exporter + snmp-exporter + blackbox-exporter + Prometheus + Grafana — all in one `docker-compose.yml`, consuming ~540 MB RAM and ~1.5 GB disk.

## Goals / Non-Goals

**Goals:**
- Monitor N warehouse sites from a single Grafana instance
- Each site runs independently — if one site goes down, others are unaffected
- Reuse existing dashboards with minimal changes (add `$site` filter)
- Keep per-site deployment simple (clone repo, set env vars, `docker compose up`)

**Non-Goals:**
- High availability or clustering for Prometheus (single master is sufficient for now)
- Long-term storage (Thanos/Cortex/Mimir) — federation with local retention is enough
- Alerting federation (alerts stay local per site for now)
- Auto-discovery of new sites (sites are added manually to master config)

## Decisions

### 1. Prometheus Federation over multi-datasource Grafana

**Decision:** Use Prometheus federation (master scrapes `/federate` from members) rather than adding each site's Prometheus as a separate Grafana datasource.

**Rationale:** Federation gives us a single datasource in Grafana, so cross-site queries (e.g., "total clients across all sites") work natively. Multi-datasource requires mixed datasource panels which are fragile and don't support cross-site aggregation.

**Alternative considered:** Grafana multi-datasource with a `$datasource` variable. Simpler to set up but cannot aggregate across sites and requires dashboard variable switching rather than label-based filtering.

### 2. Site label via external_labels

**Decision:** Each site's Prometheus adds `external_labels: { site: "<site-name>" }` in its `prometheus.yml`. The master Prometheus preserves this label through federation.

**Rationale:** This is the standard Prometheus approach. The label is automatically attached to all federated metrics — no relabeling or exporter changes needed.

**Alternative considered:** Adding a `site` label at the exporter level. Rejected because it would require modifying every exporter and duplicates what `external_labels` does natively.

### 3. Per-site stack stays self-contained

**Decision:** Each site runs the full stack (exporters + member Prometheus) via the existing `docker-compose.yml`, with site-specific values in a `.env` file. Grafana is removed from site-level deployments (runs only on central server).

**Rationale:** Self-contained sites are easy to deploy, debug locally, and operate independently. A `.env` file per site keeps the compose file generic.

### 4. Central server runs Master Prometheus + Grafana

**Decision:** A separate `docker-compose.central.yml` runs Master Prometheus (federation) and Grafana. It scrapes `/federate` from each site's Prometheus.

**Rationale:** Clean separation — sites produce metrics, central server consumes them. The central compose file is independent of the site count (just add targets).

### 5. Federation match filter

**Decision:** Federate all `unleashed_*`, `snmp_*`, `probe_*` metrics — essentially everything the exporters produce. Use `match[]` params on the `/federate` endpoint to select these.

**Rationale:** The metric volume per site is small (~500-2000 time series). No need for selective federation — bandwidth and storage are negligible.

## Risks / Trade-offs

- **Network dependency** → If central server loses connectivity to a site, federation gaps appear. Mitigation: each site still has local Prometheus with full data; gaps are only in the central view. Set `honor_labels: true` and reasonable scrape intervals.
- **Metric staleness** → Federation adds one scrape interval of latency (30-60s). Mitigation: acceptable for warehouse monitoring — not real-time alerting.
- **Single point of failure** → Central Grafana/Prometheus is a SPOF for cross-site visibility. Mitigation: sites operate independently; central is convenience, not critical path.
- **Scaling limit** → Prometheus federation works well up to ~20-50 sites with small metric volumes. Beyond that, consider Thanos/Mimir. Mitigation: current scope is <10 sites.

## Migration Plan

1. Add `external_labels` to existing site's `prometheus.yml` — non-breaking, just adds metadata
2. Create `.env.example` with site-specific variables (site name, AP IP, credentials)
3. Create `docker-compose.central.yml` with Master Prometheus + Grafana
4. Create `prometheus/prometheus.central.yml` with federation scrape config
5. Add `$site` variable to all dashboards, update queries with `site=~"$site"` filter
6. Deploy central server, add first site as federation target, verify
7. Deploy second site (R850 project), add to federation targets

**Rollback:** Remove `external_labels` from site Prometheus config. Central server is independent and can be stopped without affecting sites.

## Open Questions

- What are the site names/identifiers for labeling? (e.g., "sklad-01", "sklad-02")
- Network topology: are site Prometheus instances reachable from central server on `:9090` directly, or is VPN/tunneling needed?
- Should the central Grafana use the same dashboard JSONs or maintain separate copies?
