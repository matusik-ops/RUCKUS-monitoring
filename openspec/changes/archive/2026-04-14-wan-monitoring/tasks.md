## 1. Infrastructure

- [x] 1.1 Create `blackbox/blackbox.yml` config with ICMP and DNS modules
- [x] 1.2 Add blackbox_exporter service to `docker-compose.yml`
- [x] 1.3 Add ICMP probe job to `prometheus/prometheus.yml` with targets: gateway (10.91.1.254), 8.8.8.8, 1.1.1.1 (15s scrape interval)
- [x] 1.4 Add DNS probe job to `prometheus/prometheus.yml` targeting DNS resolution of google.com (30s interval)
- [x] 1.5 Add GATEWAY_IP variable to `.env` and `.env.example`

## 2. Dashboard — Network Health

- [x] 2.1 Replace WAN placeholder text panel in SSIDs & Network Events with real panels
- [x] 2.2 Add Internet UP/DOWN stat (green/red based on probe_success for 8.8.8.8 OR 1.1.1.1)
- [x] 2.3 Add Gateway UP/DOWN stat
- [x] 2.4 Add Gateway latency time-series (probe_duration_seconds)
- [x] 2.5 Add Internet latency time-series (probe_duration_seconds for 8.8.8.8 and 1.1.1.1)
- [x] 2.6 Add DNS response time stat

## 3. Dashboard — Network Overview

- [x] 3.1 Add "Internet" UP/DOWN stat to the status bar

## 4. Verify

- [x] 4.1 Start stack, confirm blackbox_exporter is running and probes succeed
- [x] 4.2 Verify Prometheus scrapes probe metrics
- [x] 4.3 Verify dashboard panels show real data
