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

### Via SNMP (RUCKUS-RADIO-MIB, RUCKUS-UNLEASHED-SYSTEM-MIB)

| Metric | Source | Description |
|---|---|---|
| `ruckusRadioStatsNumSta` | RADIO-MIB | Associated stations per radio |
| `ruckusRadioStatsNumAuthSta` | RADIO-MIB | Authenticated stations per radio |
| `ruckusRadioStatsResourceUtil` | RADIO-MIB | Channel utilization % per radio |
| `ruckusRadioStatsBusyAirtime` | RADIO-MIB | Busy airtime counter per radio* |
| `ruckusRadioStatsRxBytes/TxBytes` | RADIO-MIB | Traffic counters per radio |
| `ruckusRadioStatsAuthFailRate` | RADIO-MIB | Auth failure rate per radio |
| `ruckusRadioStatsAssocFailRate` | RADIO-MIB | Assoc failure rate per radio |
| `ruckusUnleashedSystemStatsCPUUtil` | UNLEASHED-MIB | CPU utilization % |
| `ruckusUnleashedSystemStatsMemoryUtil` | UNLEASHED-MIB | Memory utilization % |
| `ruckusUnleashedSystemStatsWLANTotalTxRetry` | UNLEASHED-MIB | Aggregate Tx retries |
| `ruckusUnleashedSystemStatsWLANTotalTxFail` | UNLEASHED-MIB | Aggregate Tx failures |

*\*Requires firmware with OID .1.3.6.1.4.1.25053.1.1.12.1.1.1.3.1.51 support*

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
| HighChannelUtilization | Resource util > threshold | 80% |
| HighClientCount | Total clients > threshold | 50 |
| AuthFailureSpike | Auth fail rate > threshold | 10 |
| ExcessiveTxRetries | Tx retry rate > threshold | 1000/s |
| HighCPUUsage | CPU util > threshold | 90% |
| PoorClientSignal | Client RSSI < threshold | -75 dBm |

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

- **No per-client metrics via SNMP**: In standalone/Unleashed mode, SNMP only provides aggregate per-radio stats. Per-client data (RSSI, SNR, data rate) comes from the REST API exporter.
- **No noise floor**: Not available in any Ruckus SNMP MIB or REST API.
- **No temperature**: Not exposed by the R720.
- **Airtime OID**: `ruckusRadioStatsBusyAirtime` may not be present on older firmware versions.
- **REST API sessions**: The Unleashed REST API uses session cookies that may expire. The exporter handles re-authentication automatically.

## MIB Files

See `mibs/README.md` for instructions on obtaining Ruckus MIB files.
