## Why

The monitoring stack can detect WiFi-side issues (signal, airtime, auth failures) but has zero visibility into the WAN/internet side. When users report "WiFi is slow," operators can't distinguish between a WiFi problem and an ISP outage without manually running ping from a terminal. Adding WAN monitoring completes the picture — "is the problem WiFi, the router, or the ISP?"

## What Changes

- Add `blackbox_exporter` container to Docker Compose for active probing (ICMP ping, DNS, HTTP)
- Configure Prometheus to scrape blackbox probes against: gateway (10.91.1.254), Google DNS (8.8.8.8), Cloudflare (1.1.1.1), DNS resolution test
- Replace the placeholder WAN text panel in Network Health → SSIDs & Network Events with real panels: Internet UP/DOWN, gateway/internet latency, packet loss, DNS response time
- Add WAN status indicator to Network Overview

## Capabilities

### New Capabilities
- `wan-monitoring`: Active WAN/internet health probing via blackbox_exporter — ICMP ping to gateway and internet targets, DNS resolution checks, latency and packet loss metrics

### Modified Capabilities

## Impact

- **Infrastructure**: New `blackbox_exporter` container (~5MB image, minimal resources)
- **Network**: ICMP pings every 10s to 3 targets + DNS query every 30s (negligible traffic)
- **Docker Compose**: 1 new service + 1 new config file
- **Prometheus**: 1 new scrape job with 3-4 targets
- **Dashboards**: Replace WAN placeholder in Network Health, add WAN stat to Network Overview
