## Context

We have a draft `network-overview.json` deployed in Grafana with 5 sections: status bar, per-AP health, worst clients, trends, and distribution. It works but needs refinement — better thresholds, drill-down links, and organization for a wall-mounted NOC display.

All metrics are already collected (SNMP system stats, per-radio via web API, per-client via web API). This change is purely dashboard design — no exporter or code changes.

## Goals / Non-Goals

**Goals:**
- One screen that answers: "Is the network healthy right now?"
- Problems are immediately visible (red/yellow) without clicking anything
- Drill-down links to detailed dashboards for investigation
- Works on a wall-mounted TV (readable from distance, auto-refresh)

**Non-Goals:**
- Adding new metrics or data sources
- Replacing the existing detail dashboards (they remain for investigation)
- Real-time alerting integration (alerts are in Prometheus, not the dashboard)

## Decisions

### 1. Dashboard layout: 5 zones top-to-bottom

1. **Status bar** (top) — Big numbers: APs online, total clients, CPU, memory, data source health. Green = OK, red = act now. Readable from 3 meters.
2. **Per-AP health** (middle-top) — Horizontal bar gauges: clients per AP, airtime busy per band, auth failures. Shows which AP has a problem.
3. **Problem clients** (middle) — Tables: clients with weak signal, clients with lowest data rates. If empty = no problems.
4. **Trends** (middle-bottom) — Time-series: client count, Tx retries/failures, throughput. Shows if things are getting worse.
5. **Distribution** (bottom) — Pie charts: clients per SSID, per AP, per band. Shows load balance.

### 2. Color thresholds based on observed real data

From our 7-AP network with ~30 clients:
- APs online: green ≥7, yellow ≥5, red <5
- Airtime busy: green <20%, yellow <40%, red ≥40%
- Client RSSI: green >-60, yellow >-75, red ≤-75
- Auth failures: green <50, yellow <200, red ≥200
- Tx rate: green >70Mbps, yellow >30Mbps, red ≤30Mbps

### 3. Set as Grafana home dashboard

Configure Grafana provisioning so this dashboard loads by default when opening Grafana.

## Risks / Trade-offs

- **Information density** — A single dashboard showing everything risks clutter. Mitigation: 5 clear zones with section headers; empty problem tables = no noise.
- **Threshold tuning** — Initial thresholds are based on current network size. Mitigation: Document thresholds; easy to adjust in dashboard JSON.
