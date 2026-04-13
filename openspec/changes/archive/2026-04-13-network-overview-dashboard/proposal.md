## Why

The existing dashboards (Fleet Overview, AP Detail, Radio Health, Client Health) are useful for drill-down investigation, but there's no single view that tells an operator "everything is fine" or "something is wrong — here's what." A NOC-style overview dashboard is needed so that anyone glancing at the screen immediately knows the network status without clicking through multiple pages.

## What Changes

- Formalize and refine the draft `network-overview.json` dashboard into a production-quality single-pane NOC view
- Organize panels into clear zones: status bar (health at a glance), problem indicators (what's wrong now), trends (is it getting worse), and distribution (load balance)
- Add drill-down links from problem indicators to the relevant detail dashboards
- Set this as the Grafana home dashboard

## Capabilities

### New Capabilities
- `noc-dashboard`: A single Grafana dashboard designed for wall-mounted or always-on display that answers: How many APs are up? How many clients? Is any AP congested? Are any clients struggling? Are auth failures spiking? What's the traffic trend?

### Modified Capabilities

## Impact

- **Dashboards**: New `network-overview.json` replaces the draft; becomes the default landing page
- **Grafana config**: Set as home dashboard in provisioning
- **No code changes**: All metrics already collected; this is purely a dashboard/visualization change
