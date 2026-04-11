## Context

The existing Unleashed exporter queries `_cmdstat.jsp` for per-client data using `<client INTERVAL-STATS='yes'/>`. During e2e testing, we discovered that `<ap LEVEL='1'/>` returns rich per-AP, per-radio data including airtime — previously believed to require SSH. This change extends the exporter to collect both client and AP/radio stats in the same poll cycle.

Verified fields from the live AP (10.91.1.109, firmware 200.15.6.212):

Per radio: `airtime-total`, `airtime-busy`, `airtime-rx`, `airtime-tx`, `num-sta`, `avg-rssi`, `channel`, `channelization`, `tx-power`, `radio-total-tx-bytes`, `radio-total-rx-bytes`, `radio-total-tx-pkts`, `radio-total-rx-pkts`, `radio-total-tx-fail`, `radio-total-retries`, `radio-total-rx-decrypt-error`, `total-fcs-err`, `mgmt-auth-req`, `mgmt-auth-success`, `mgmt-auth-fail`, `mgmt-assoc-req`, `mgmt-assoc-success`, `mgmt-assoc-fail`, `mgmt-disassoc-leave`, `mgmt-disassoc-abnormal`

## Goals / Non-Goals

**Goals:**
- Expose per-radio airtime metrics (total, busy, rx, tx) per AP
- Expose per-radio client count, avg RSSI, traffic, Tx quality, and auth/assoc counters
- Update radio health dashboard with real airtime and per-radio panels
- Add per-radio alerting rules

**Non-Goals:**
- Changing the SNMP collection (per-radio data still not available via SNMP)
- Adding new containers or services (reuse existing exporter)
- Per-VAP (per-SSID-per-radio) stats (available in the API but out of scope for this change)

## Decisions

### 1. Extend existing exporter rather than add a new service

**Rationale**: The AP stats query uses the same `_cmdstat.jsp` endpoint and authentication session as the client stats query. Adding a second query in the same poll loop is trivial and avoids another container/service to manage.

### 2. Two queries per poll cycle

The exporter will make two `_cmdstat.jsp` POST requests per poll:
1. `<client INTERVAL-STATS='yes'/>` — per-client metrics (existing)
2. `<ap LEVEL='1'/>` — per-AP, per-radio metrics (new)

Both use the same session cookie and CSRF token.

### 3. Airtime as percentage

The raw airtime values appear to be relative counters or permille values (not absolute percentages). We'll expose them as-is and document the unit. The dashboard can compute `airtime-busy / airtime-total * 100` for a utilization percentage.

## Risks / Trade-offs

- **Double API load** → Two queries instead of one per poll cycle. Mitigation: Both are lightweight XML responses; the AP stats response is ~80KB but compresses well.
- **Airtime value interpretation** → The exact unit of airtime-total/busy/rx/tx is not documented. Values observed range from 0-169. Mitigation: Expose raw values; compute ratios in Grafana.
