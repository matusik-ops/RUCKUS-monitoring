## Context

The exporter currently makes two `_cmdstat.jsp` queries per poll cycle: per-client and per-AP/per-radio. We need to add a third: rogue AP detection. This is required for the planned 5-tab Network Health dashboard (RF Environment tab and Rogue Devices tab).

Verified against live AP at 10.91.1.109: rogue query returns rich data including detected APs with their SSID, BSSID (MAC), channel, radio band, encryption status, and a list of which of our APs detected each rogue (with per-detector RSSI values).

Sample rogue entry observed:
```xml
<rogue mac="d0:21:f9:5d:48:3a" rogue-type="malicious AP (Same-Network)"
       ssid="Photoneo-Playhouse" channel="11" radio-band="2.4g"
       num-detection="1" last-seen="1776063948">
  <detection ap="ec:58:ea:10:b4:f0" sys-name="AP02" rssi="49" last-seen="..."/>
</rogue>
```

## Goals / Non-Goals

**Goals:**
- Expose per-rogue-AP metrics with both rogue and detecting AP labels
- Distinguish malicious rogues (same-network masquerade) from regular foreign APs
- Provide aggregations: total rogue count, by band, by channel
- Handle stale rogues — remove from metrics if not seen in N polls

**Non-Goals:**
- Active rogue containment / blocking (read-only monitoring)
- Historical rogue tracking beyond Prometheus retention
- Event log integration if API format proves complex (defer to follow-up)

## Decisions

### 1. Rogue metrics use both rogue and detector labels

Each `<detection>` element creates a separate metric sample with labels:
- `rogue_mac`, `rogue_ssid`, `rogue_channel`, `rogue_band`, `rogue_type` (rogue AP attributes)
- `detector_ap` (which of our APs saw it)

This lets us answer: "Which of my APs sees this rogue?" and "What rogues are on channel 11 in 2.4GHz?"

### 2. Boolean rogue type label, not free-text

Map `rogue-type` to a simpler label. Two values observed:
- `"AP"` → label `is_malicious=false`
- `"malicious AP (Same-Network)"` → label `is_malicious=true`

Keep the original `rogue_type` label as well for full info, plus add boolean for easy alerting.

### 3. Metrics are gauges, not counters

Rogues come and go — they're not cumulative. Use gauges. Reset all rogue metrics each poll, then populate from current XML response. Stale rogues simply won't be set, so old samples will become stale in Prometheus.

### 4. Defer event log integration

The `<event/>` query format wasn't immediately working. Rather than block on it, ship rogue detection now and revisit events in a follow-up change.

## Risks / Trade-offs

- **High cardinality** → 20 rogues × 7 detector APs = 140 series potential. Per Prometheus standards that's fine, but if rogues balloon to 100+ this could grow. Mitigation: monitor cardinality.
- **API load** → Third query per poll. Mitigation: same poll session, lightweight XML, AP isn't stressed.
- **No event data** → Connect/disconnect history needs event log API which is deferred. Mitigation: dashboard tabs for "Overview" history will use what we have (Prometheus rate of `unleashed_client_count` change).
