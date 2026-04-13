## Why

We have rich monitoring data (per-AP, per-radio, per-client, rogue APs) but currently distributed across multiple drill-down dashboards. We need a single comprehensive "Network Health" dashboard organized into thematic sections that operators can navigate top-to-bottom: overall health → RF environment → historical trends → security. The existing Network Overview is concise; this is its deeper companion focused on root-cause investigation rather than at-a-glance status.

## What Changes

- Build a new "Network Health" dashboard with 5 collapsible row sections acting as tabs:
  1. **Overview** — composite network health score (%), peak-hour metrics, signal stats, current alerts, AP fleet summary
  2. **RF Environment** — channel utilization, 2.4GHz/5GHz congestion, per-AP/per-radio RF table (airtime busy/rx/tx, retries, FCS errors, noise via per-client average), rogue AP density per channel
  3. **Airtime History** — time-series of airtime busy/rx/tx per AP per band, daily peaks
  4. **Channel History** — channel changes per AP over time (DFS events, ChannelFly), Tx power history
  5. **Rogue Devices** — rogue AP table, malicious-rogue alert panel, rogues by channel, top detected rogues by signal
- Use Grafana row-collapse pattern so each section can be expanded/collapsed independently
- Place at top of Grafana home (alongside Network Overview)

## Capabilities

### New Capabilities
- `health-dashboard`: 5-section comprehensive dashboard for deep network health investigation. Composite health % score, RF environment analysis, airtime/channel history, rogue AP overview.

### Modified Capabilities
<!-- None - this is a new dashboard, doesn't modify existing capabilities -->

## Impact

- **Dashboards**: New `grafana/dashboards/network-health.json` (~1500 lines)
- **Provisioning**: No changes — auto-loaded from existing dashboards directory
- **No code changes**: All required metrics already collected (per-AP, per-radio, per-client, rogue)
- **No new infrastructure**
