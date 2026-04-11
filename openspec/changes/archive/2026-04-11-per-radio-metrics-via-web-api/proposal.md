## Why

The current monitoring stack lacks per-radio metrics — airtime utilization, per-radio client counts, per-radio Tx retries/failures, and per-radio auth/assoc failure rates. These were previously assumed to require SSH CLI access, but testing against the live AP revealed that the `_cmdstat.jsp` web API's AP stats query (`<ap LEVEL='1'/>`) already returns per-radio data including `airtime-total`, `airtime-busy`, `airtime-rx`, `airtime-tx`, `num-sta`, `avg-rssi`, `radio-total-retries`, `radio-total-tx-fail`, `mgmt-auth-fail`, and `mgmt-assoc-fail` — per AP, per radio band.

## What Changes

- Extend the existing Unleashed exporter to also query AP-level stats (`<ap LEVEL='1'/>`) and expose per-radio metrics as Prometheus gauges/counters
- Add new Grafana dashboard panels for airtime utilization per radio, per-AP radio health comparison
- Update alerting rules to use real per-radio metrics (channel utilization via airtime, auth failure rates)
- Update existing specs and documentation to reflect that per-radio metrics ARE available (correcting the firmware 200.15 limitation documented earlier)

## Capabilities

### New Capabilities
- `per-radio-stats`: Per-AP, per-radio metrics from the _cmdstat.jsp AP stats query — airtime (total/busy/rx/tx), client counts, avg RSSI, traffic counters, Tx retries/failures, auth/assoc success/failure counters, channel, Tx power, channelization

### Modified Capabilities
- `radio-health`: Was based on system-level aggregates as a proxy. Now uses real per-radio airtime and failure rate data from the web API.
- `alerting`: Add per-radio alerts (high airtime-busy, auth failure spike per radio) now that the data is available.
- `dashboard-views`: Add airtime panels to the radio health dashboard.

## Impact

- **Code**: Extend `unleashed-exporter/exporter.py` with a second _cmdstat.jsp query for AP stats
- **Dashboards**: Update radio-health dashboard with real per-radio panels; update fleet overview with airtime indicators
- **Alerts**: Add HighAirtimeBusy and per-radio AuthFailureSpike rules
- **Specs**: Correct the "not available" statements in snmp-collection and radio-health specs
- **No new services or dependencies** — reuses the existing exporter and web API session
