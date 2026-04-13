## Context

We've built collection for: per-client metrics (RSSI, SNR, noise, channel, data rate, traffic, association time), per-AP/per-radio (airtime, num-sta, auth/assoc fail rates, traffic, retries, FCS errors, channel, tx-power), rogue APs (per-detector RSSI, malicious flag, by-band/channel counts), and SNMP system stats (CPU, memory, aggregate WLAN traffic).

The existing Network Overview dashboard is the at-a-glance NOC view. The new Network Health dashboard is a deeper investigation tool — when something is wrong on the overview, this is where you look.

## Goals / Non-Goals

**Goals:**
- One Grafana dashboard with 5 collapsible row sections functioning as tabs
- Health % score that aggregates multiple dimensions (AP up, congestion, weak clients, malicious rogues)
- Each section is independently useful — collapsed sections don't load data
- Re-uses metrics we already have; no exporter changes
- Loads in <2s, refreshes every 30s

**Non-Goals:**
- Replacing Network Overview (this is complementary)
- Per-client deep-dive (Client Health dashboard handles that)
- Real-time event log integration (deferred — needs separate exporter work)
- DFS radar event detection (would need event log)
- Wired/uplink monitoring

## Decisions

### 1. Single dashboard with collapsed rows acting as tabs

Standard Grafana row-collapse pattern. Each "tab" is a Grafana row with a title and collapsed=true by default for sections 2-5. Overview is expanded by default. Operators click row title to expand/collapse.

**Why not separate dashboards**: One bookmark, one URL, shared time picker, easier to share/screenshot, less file maintenance.

### 2. Composite health score formula

```
health_score = 100
  - (10 × down_APs)               # each down AP = -10%
  - (5  × weak_signal_clients)    # each client with RSSI < -75 = -5%
  - (10 × congested_radios)       # each radio with airtime busy > 50% = -10%
  - (15 × high_auth_fail_APs)     # each AP with >50% auth fail = -15%
  - (20 × malicious_rogues)       # each malicious rogue = -20%
clamp_min(health_score, 0)
```

Color thresholds: green ≥80, yellow ≥50, red <50. Tuned so a single down AP doesn't immediately go red, but multiple problems do.

### 3. RF Environment tab uses per-AP/per-radio table

A wide table panel showing all 14 radios (7 APs × 2 bands) with columns:
- AP, Band, Channel, Channel Width
- Clients, Avg RSSI
- Airtime Busy %, Rx %, Tx %
- Tx Retries (5m), Tx Failures (5m), FCS Errors (5m)
- Auth Fail Rate (5m)

Sortable by any column — operator can sort by Tx Retries to find worst RF radios.

### 4. History tabs use time-series with band/AP variables

Airtime History and Channel History tabs use template variables (`$ap_name`, `$radio_band`) so operator can drill down. Default = all APs.

### 5. Rogue Devices tab

Three panels:
- **Top KPIs**: Total rogues, Malicious rogues count, Strongest rogue signal
- **Rogues by Channel** (bar chart): Shows channel pollution from foreign APs
- **Rogue Table**: All detected rogues sorted by best (highest) RSSI; includes SSID, MAC, channel, band, type, which of our APs sees it

### 6. Reuse existing alert thresholds for consistency

Use the same thresholds across dashboards (RSSI -70/-75 for weak, airtime 40%/50% for congested, auth fail 5%/20%, etc.) so operators see consistent colors.

## Risks / Trade-offs

- **Dashboard size** → 5 sections × multiple panels = ~25-30 panels total. Mitigation: collapsed rows don't load data when collapsed — Grafana skips queries for collapsed sections.
- **Health score subjectivity** → Weights are opinionated. Mitigation: document the formula in the panel description so users understand and can adjust if needed.
- **Channel history requires history** → If exporter just started, channel history will be empty. Mitigation: dashboard time range default = 6h; users can change it.
- **No DFS event detection** → We can see channel changes via `unleashed_radio_channel`, but not the reason (DFS radar, manual change, ChannelFly). Mitigation: just show the change; operator interprets.
