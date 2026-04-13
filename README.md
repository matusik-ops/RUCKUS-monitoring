# Ruckus R720 Monitoring Dashboard

Monitoring stack for Ruckus R720 access points (standalone/Unleashed mode) using Grafana, Prometheus, SNMP Exporter, and a custom Unleashed REST API exporter.

## Architecture

```
┌─────────────┐    SNMP v2c    ┌──────────────────┐    scrape    ┌────────────┐    query    ┌─────────┐
│  Ruckus R720 │◄──────────────│  SNMP Exporter   │◄────────────│ Prometheus │◄───────────│ Grafana │
│  (AP)        │               │  :9116           │             │ :9090      │            │ :3000   │
│              │    REST API   ┌──────────────────┐│    scrape   │            │            │         │
│              │◄──────────────│ Unleashed        ││◄────────────│            │            │         │
│              │  /api/sta     │ Exporter :9191   ││             │            │            │         │
└─────────────┘               └──────────────────┘│             └────────────┘            └─────────┘
```

**Two data collection paths:**
- **SNMP Exporter**: AP/radio-level metrics (CPU, memory, client counts, channel utilization, airtime, traffic counters, auth/assoc stats)
- **Unleashed REST API Exporter**: Per-client metrics (RSSI, SNR, data rate, association time, Rx/Tx bytes per client)

## Quick Start

```bash
# 1. Configure
cp .env.example .env
# Edit .env with your AP address, SNMP community, and Unleashed API credentials

# 2. Start
docker compose up -d

# 3. Access Grafana
open http://localhost:3000  # admin/admin (default)
```

## Configuration

All configuration is in `.env`:

| Variable | Default | Description |
|---|---|---|
| `SNMP_COMMUNITY` | `public` | SNMP v2c community string |
| `SNMP_SCRAPE_INTERVAL` | `60s` | How often to poll SNMP |
| `PROMETHEUS_RETENTION` | `30d` | How long to keep metric data |
| `UNLEASHED_API_URL` | `https://10.91.1.109` | Unleashed AP REST API URL |
| `UNLEASHED_USERNAME` | `admin` | Unleashed web UI username |
| `UNLEASHED_PASSWORD` | - | Unleashed web UI password |
| `UNLEASHED_POLL_INTERVAL` | `60` | REST API poll interval (seconds) |
| `UNLEASHED_VERIFY_SSL` | `false` | Verify SSL cert (self-signed by default) |
| `GRAFANA_ADMIN_PASSWORD` | `admin` | Grafana admin password |

### Adding/Removing APs

Edit `prometheus/targets.yml`:

```yaml
- targets:
    - 10.91.1.109
  labels:
    ap_name: r720-main
- targets:
    - 10.91.1.110
  labels:
    ap_name: r720-floor2
```

Reload Prometheus: `curl -X POST http://localhost:9090/-/reload`

## Dashboards

| Dashboard | Description |
|---|---|
| **Fleet Overview** | All APs at a glance: status, client count, channel utilization, CPU, Tx errors |
| **AP Detail** | Per-AP drill-down: radio clients, traffic, channel util, CPU/memory, Ethernet status |
| **Radio Health** | Per-radio: channel utilization, airtime, auth/assoc failure rates, Tx retries, Rx errors |
| **Client Health** | Per-client: RSSI, SNR, data rate, association time, traffic (from REST API) |

## Available Metrics

### Via SNMP (RUCKUS-UNLEASHED-SYSTEM-MIB)

| Metric | Description |
|---|---|
| `ruckusUnleashedSystemStatsCPUUtil` | CPU utilization % |
| `ruckusUnleashedSystemStatsMemoryUtil` | Memory utilization % |
| `ruckusUnleashedSystemStatsNumSta` / `AllNumSta` | Authorized / total client count |
| `ruckusUnleashedSystemStatsNumAP` | Number of connected APs |
| `ruckusUnleashedSystemStatsWLANTotalTxRetry` | Aggregate Tx retries |
| `ruckusUnleashedSystemStatsWLANTotalTxFail` | Aggregate Tx failures |
| `ruckusUnleashedSystemStatsWLANTotalRx/TxBytes` | Aggregate wireless traffic |
| `ifInOctets` / `ifOutOctets` | Ethernet interface traffic |

### Via Unleashed Web API — Per-Radio

| Metric | Description |
|---|---|
| `unleashed_radio_airtime_total/busy/rx/tx` | Radio airtime breakdown |
| `unleashed_radio_num_sta` | Clients per radio |
| `unleashed_radio_avg_rssi` | Average client RSSI per radio |
| `unleashed_radio_retries_total` | Tx retries per radio |
| `unleashed_radio_tx_fail_total` | Tx failures per radio |
| `unleashed_radio_auth_fail/success` | Auth results per radio |
| `unleashed_radio_assoc_fail/success` | Assoc results per radio |
| `unleashed_radio_channel/tx_power/channelization` | Radio config |

### Via Unleashed Web API — Rogue Detection

| Metric | Description |
|---|---|
| `unleashed_rogue_rssi_dbm` | Rogue AP signal strength per detector |
| `unleashed_rogue_count` | Total unique rogues detected |
| `unleashed_rogue_malicious_count` | Same-network impersonator APs (security concern) |
| `unleashed_rogue_count_by_band/channel` | Rogue distribution |

### Via Unleashed REST API

| Metric | Description |
|---|---|
| `unleashed_client_rssi_dbm` | Client RSSI in dBm |
| `unleashed_client_snr_db` | Client signal-to-noise ratio |
| `unleashed_client_data_rate_mbps` | Client negotiated data rate |
| `unleashed_client_assoc_time_seconds` | Client association duration |
| `unleashed_client_rx_bytes` / `tx_bytes` | Client traffic |
| `unleashed_clients_per_ssid` | Client count per SSID |

## Alerting Rules

| Alert | Condition | Default Threshold |
|---|---|---|
| APUnreachable | SNMP scrape failing | 5 minutes |
| HighClientCount | Total clients > threshold | 50 |
| ExcessiveTxRetries | Tx retry rate > threshold | 1000/s |
| HighCPUUsage | CPU util > threshold | 90% |
| PoorClientSignal | Client RSSI < threshold | -75 dBm |
| HighAirtimeBusy | Radio airtime busy/total > threshold | 50% |
| RadioAuthFailureSpike | Per-radio auth failures in 5m > threshold | 100 |

## Testing

```bash
# Install test dependencies
pip install -r requirements-test.txt

# Run mock tests (no AP required)
make test-mock

# Run alert rule tests (requires promtool)
make test-alerts

# Run end-to-end tests (requires live AP at 10.91.1.109)
make test-e2e

# Run all tests
make test
```

## Known Limitations

- **SNMP is system-level only**: RUCKUS-RADIO-MIB per-radio OIDs don't exist on firmware 200.15. Per-radio data (airtime, client counts, auth/assoc) comes from the web API exporter instead.
- **No temperature**: Not exposed by any Ruckus interface.
- **Undocumented web API**: The `_cmdstat.jsp` XML interface is not officially documented and may change between firmware versions. Test fixtures capture expected formats.
- **Web API sessions**: The Unleashed web API uses `-ejs-session-` cookies + CSRF tokens that expire. The exporter re-authenticates automatically.

## MIB Files

See `mibs/README.md` for instructions on obtaining Ruckus MIB files.
